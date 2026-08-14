"""Patient Zero HTTP API — STUB.

Every response here is synthetic. Nothing in this file touches HydraDB, and no number
it returns is a measurement. The shapes are the contract from docs/HANDOFF.md §4; the
`cypher` strings are the queries the real implementation is *intended* to issue
(docs/DESIGN.md §5), so the show-query toggle in the UI lays out correctly now.

Three invariants the frontend depends on and the real implementation must preserve:
  1. every response carries `cypher` (str) and `latency_ms` (float)
  2. every response carries `stub: true` until it is served from a real traversal
  3. /api/forecast switches topology on one parameter — trust vs dependency (the control)

Scoring fields that would be *measured* results (precision@K, R0) are returned as null
until they are actually measured. A fake precision number reaching the README, the demo,
or the video is the single worst outcome for this project.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Callable, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .db import HEALTH_CYPHER, ping as hydradb_ping

log = logging.getLogger("patient_zero.api")

STUB = True  # flip (and delete this module's fixtures) when the loader lands
SENTINEL_VALID_TO = 4102444800  # 2100-01-01, per DESIGN.md §4
WORM_START = 1778527200  # 2026-05-11T19:20:00Z


# --- the queries the real implementation will issue (DESIGN.md §5) --------------------
# Rendered with maxLen / resultLimit interpolated so the UI shows the actual bounds.
# Bounding every traversal is not decoration: HydraDB tops out at fanout 10k, 20 hops
# = 10.9s. An unbounded traversal hangs the demo.


def _radius_cypher(max_hops: int, limit: int) -> str:
    return f"""CALL algo.SSpaths({{
  sourceLabel: 'Version', sourceProperty: 'vid', sourceValues: $compromised,
  relTypes: ['DEPENDS_ON','PINS'], relDirection: 'incoming',
  maxLen: {max_hops}, resultLimit: {limit}
}}) YIELD path
WHERE all(r IN relationships(path) WHERE r.valid_from <= $as_of < r.valid_to)
RETURN path"""


def _forecast_cypher(topology: str, max_hops: int, limit: int) -> str:
    rel_types = (
        "['MAINTAINS','PUBLISHED_FROM','HAS_WORKFLOW','PUBLISHES_VIA_OIDC','SHARES_EMAIL_DOMAIN']"
        if topology == "trust"
        else "['DEPENDS_ON','PINS']"
    )
    return f"""// topology={topology}  <- the negative control is this one parameter
CALL algo.SSpaths({{
  sourceLabel: 'Package', sourceProperty: 'pid', sourceValues: $seeds,
  relTypes: {rel_types}, relDirection: 'outgoing',
  maxLen: {max_hops}, resultLimit: {limit}
}}) YIELD path
WITH last(nodes(path)) AS candidate, path
WHERE NOT candidate.pid IN $seeds
RETURN candidate.pid AS pid, count(DISTINCT path) AS support, collect(path)[0] AS justification
ORDER BY support DESC LIMIT $k"""


def _index_case_cypher(max_hops: int, limit: int) -> str:
    return f"""// same primitive, walked backward: given the symptoms, find the index case
CALL algo.SSpaths({{
  sourceLabel: 'Package', sourceProperty: 'pid', sourceValues: $observed,
  relTypes: ['MAINTAINS','PUBLISHED_FROM','HAS_WORKFLOW','PUBLISHES_VIA_OIDC'],
  relDirection: 'incoming',
  maxLen: {max_hops}, resultLimit: {limit}
}}) YIELD path
WITH last(nodes(path)) AS origin, count(DISTINCT head(nodes(path))) AS covered, path
RETURN origin, covered,
       coalesce(origin.uses_pull_request_target, false) AS vector_match,
       coalesce(origin.has_oidc_publish, false) AS oidc_publish, path
ORDER BY covered DESC, vector_match DESC LIMIT $k"""


_REACHABILITY_CYPHER = """// Leg 3 Tier 1: a property predicate, not a traversal
MATCH (s:Service {sid: $sid})-[p:PINS]->(v:Version)
WHERE v.vid IN $finding_vids AND p.valid_from <= $as_of < p.valid_to
RETURN v.vid AS vid, v.has_install_script AS install, v.install_hooks AS hooks"""


def _leverage_cypher(max_hops: int, limit: int) -> str:
    return f"""// Leg 4: forward from nothing — as if each credential were already stolen
MATCH (m:Maintainer)
CALL algo.SSpaths({{
  sourceLabel: 'Maintainer', sourceProperty: 'mid', sourceValues: [m.mid],
  relTypes: ['MAINTAINS','PUBLISHED_FROM','HAS_WORKFLOW','PUBLISHES_VIA_OIDC','DEPENDS_ON','PINS'],
  relDirection: 'outgoing',
  maxLen: {max_hops}, resultLimit: {limit}
}}) YIELD path
WITH m, [n IN nodes(path) WHERE n:Service] AS hit, path
RETURN m.mid AS id, count(DISTINCT hit) AS services_at_risk, collect(path)[0] AS path
ORDER BY services_at_risk DESC LIMIT $k"""


_EVIDENCE_CYPHER = """// the control: identical forecast, relTypes swapped, scored against the same IOC set
// precision@K and R0 are computed in the scorer over both result sets; see DESIGN.md §6
CALL algo.SSpaths({ /* forecast, relTypes: T2 */ }) YIELD path
UNION
CALL algo.SSpaths({ /* forecast, relTypes: T1 */ }) YIELD path"""

_TIMELINE_CYPHER = """MATCH (v:Version)
WHERE v.published_at >= $window_start AND v.published_at < $window_end
RETURN v.ecosystem AS ecosystem, v.published_at AS at, count(*) AS versions
ORDER BY at"""


# --- request models -------------------------------------------------------------------


class BlastRadiusReq(BaseModel):
    ecosystem: str = "npm"
    name: str = "@tanstack/react-query"
    version: str = "5.0.1"
    window_start: int = WORM_START
    window_end: int = SENTINEL_VALID_TO
    max_hops: int = Field(default=6, ge=1, le=20)
    limit: int = Field(default=500, ge=1, le=5000)


class ForecastReq(BaseModel):
    seeds: list[str] = Field(default_factory=list)
    as_of: int = WORM_START + 360
    k: int = Field(default=10, ge=1, le=500)
    topology: Literal["trust", "dependency"] = "trust"
    max_hops: int = Field(default=3, ge=1, le=20)
    limit: int = Field(default=500, ge=1, le=5000)


class IndexCaseReq(BaseModel):
    observed: list[str] = Field(default_factory=list)
    as_of: int = WORM_START + 360
    k: int = Field(default=5, ge=1, le=100)
    max_hops: int = Field(default=4, ge=1, le=20)
    limit: int = Field(default=500, ge=1, le=5000)


class ReachabilityReq(BaseModel):
    sid: str = "svc:example-app"
    finding_vids: list[str] = Field(default_factory=list)
    as_of: int = WORM_START + 360


# --- app ------------------------------------------------------------------------------

BANNER = r"""
================================================================================
  PATIENT ZERO API IS SERVING SYNTHETIC STUB DATA
  Every response carries "stub": true. No value returned here is a measurement.
  Do NOT copy any number from this server into the README, the demo, or the video.
================================================================================
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    if STUB:
        log.warning(BANNER)
    yield


app = FastAPI(title="Patient Zero (STUB)", version="0.1.0", lifespan=lifespan)

# W4 (and any local preview) talks to this stub from a browser origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _timed(cypher: str, build: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    """Envelope every response: real elapsed time, the query, and the stub flag."""
    t0 = time.perf_counter()
    body = build()
    body["cypher"] = cypher
    body["latency_ms"] = round((time.perf_counter() - t0) * 1000, 3)
    body["stub"] = STUB
    return body


@app.post("/api/blast-radius")
def blast_radius(req: BlastRadiusReq) -> dict[str, Any]:
    vid = f"{req.ecosystem}:{req.name}@{req.version}"
    return _timed(
        _radius_cypher(req.max_hops, req.limit),
        lambda: {
            "services": [
                {
                    "sid": "svc:stub-storefront",
                    "name": "stub-storefront",
                    "exposed_at": req.window_start + 180,
                    "path": [vid, "npm:stub-ui-kit@2.4.0", "npm:stub-storefront@1.9.3"],
                },
                {
                    "sid": "svc:stub-billing",
                    "name": "stub-billing",
                    "exposed_at": req.window_start + 540,
                    "path": [vid, "npm:stub-forms@1.1.0", "npm:stub-billing@0.8.2"],
                },
            ],
            "stats": {
                "source_vid": vid,
                "services_exposed": 2,
                "paths_returned": 2,
                "max_hops": req.max_hops,
                "result_limit": req.limit,
                "as_of": req.window_end,
            },
        },
    )


@app.post("/api/forecast")
def forecast(req: ForecastReq) -> dict[str, Any]:
    """Forecast (topology=trust) and its negative control (topology=dependency).

    The thesis predicts the dependency control scores at or near zero — the worm did not
    spread that way. The stub reflects that shape so the UI renders both honestly. These
    are stub propagation scores, not precision; precision@K stays null until measured.
    """
    trust = req.topology == "trust"
    seeds = req.seeds or ["npm:@tanstack/react-query"]
    base = 0.91 if trust else 0.04
    step = 0.07 if trust else 0.01
    preds = []
    for i in range(min(req.k, 5)):
        pid = (
            f"npm:stub-trust-neighbour-{i}"
            if trust
            else f"npm:stub-dependent-{i}"
        )
        preds.append(
            {
                "pid": pid,
                "score": round(max(base - i * step, 0.0), 4),
                "justification_path": (
                    [seeds[0], "npm:stub-maintainer-shared", pid]
                    if trust
                    else [seeds[0], pid]
                ),
            }
        )
    return _timed(
        _forecast_cypher(req.topology, req.max_hops, req.limit),
        lambda: {
            "predictions": preds,
            "stats": {
                "topology": req.topology,
                "is_negative_control": not trust,
                "seeds": len(seeds),
                "k": req.k,
                "max_hops": req.max_hops,
                "result_limit": req.limit,
                "as_of": req.as_of,
                "precision_at_k": None,  # measured by the scorer, never invented here
            },
        },
    )


@app.post("/api/index-case")
def index_case(req: IndexCaseReq) -> dict[str, Any]:
    observed = req.observed or ["npm:@tanstack/react-query"]
    kinds = [("workflow", "stub-repo/.github/workflows/release.yml"), ("maintainer", "npm:stub-maintainer"), ("repo", "github:stub-org/stub-repo")]
    return _timed(
        _index_case_cypher(req.max_hops, req.limit),
        lambda: {
            "candidates": [
                {
                    "id": ident,
                    "kind": kind,
                    "score": round(0.88 - i * 0.19, 4),
                    "path_to_observed": [ident, "npm:stub-package", observed[0]],
                }
                for i, (kind, ident) in enumerate(kinds[: req.k])
            ],
            "stats": {
                "observed": len(observed),
                "k": req.k,
                "max_hops": req.max_hops,
                "result_limit": req.limit,
                "as_of": req.as_of,
                "true_origin_rank": None,  # the Leg 0 verdict; measured, never invented
            },
        },
    )


@app.post("/api/reachability")
def reachability(req: ReachabilityReq) -> dict[str, Any]:
    vids = req.finding_vids or ["npm:stub-ui-kit@2.4.0", "npm:stub-forms@1.1.0"]
    verdicts = [
        {
            "vid": vid,
            "tier": "install" if i == 0 else "none",
            "evidence": (
                {"has_install_script": True, "install_hooks": ["postinstall"]}
                if i == 0
                else {"has_install_script": False, "install_hooks": []}
            ),
        }
        for i, vid in enumerate(vids)
    ]
    return _timed(
        _REACHABILITY_CYPHER,
        lambda: {
            "verdicts": verdicts,
            "stats": {
                "sid": req.sid,
                "findings_in": len(vids),
                "findings_executing": sum(v["tier"] == "install" for v in verdicts),
                "as_of": req.as_of,
            },
        },
    )


@app.get("/api/leverage")
def leverage(k: int = 5, max_hops: int = 4, limit: int = 500) -> dict[str, Any]:
    return _timed(
        _leverage_cypher(max_hops, limit),
        lambda: {
            "ranked": [
                {
                    "id": f"npm:stub-maintainer-{i}",
                    "kind": "maintainer" if i % 2 == 0 else "workflow",
                    "services_at_risk": 12 - i * 2,
                    "path": [f"npm:stub-maintainer-{i}", "npm:stub-package", "svc:stub-storefront"],
                }
                for i in range(min(k, 5))
            ],
            "mincut": [
                {"id": "npm:stub-maintainer-0", "kind": "maintainer", "action": "enforce 2FA"},
                {
                    "id": "github:stub-org/stub-repo/.github/workflows/release.yml",
                    "kind": "workflow",
                    "action": "drop pull_request_target",
                },
            ],
            "stats": {
                "k": k,
                "max_hops": max_hops,
                "result_limit": limit,
                "spread_blocked_pct": None,  # min-cut result; measured, never invented
            },
        },
    )


@app.get("/api/evidence")
def evidence() -> dict[str, Any]:
    """The evidence layer. Every field here is a *measured* result, so the stub returns null.

    Shipping plausible-looking precision or R0 numbers from a stub is how a fabricated
    number ends up in a video. The UI should render null as "not yet measured".
    """
    unmeasured = {"precision_at_10": None, "precision_at_50": None, "precision_at_100": None,
                  "recall_at_100": None, "measured": False}
    return _timed(
        _EVIDENCE_CYPHER,
        lambda: {
            "precision_trust": dict(unmeasured, topology="trust"),
            "precision_dependency": dict(unmeasured, topology="dependency", role="negative control"),
            "r0_trust": None,
            "r0_dependency": None,
            "note": "STUB: no validation has been run. Nulls are literal, not zeros.",
            "stats": {"measured": False, "ioc_set_loaded": False},
        },
    )


@app.get("/api/timeline")
def timeline() -> dict[str, Any]:
    """The May 11 2026 event timeline that drives the scrubbable clock.

    The timestamps and the public event descriptions are from the published record
    (HANDOFF.md §5); the per-tick counts are stub.
    """
    return _timed(
        _TIMELINE_CYPHER,
        lambda: {
            "events": [
                {"at": WORM_START, "label": "worm begins", "packages": 1, "source": "published record"},
                {"at": WORM_START + 360, "label": "42 @tanstack/* packages compromised (seed set)",
                 "packages": 42, "source": "published record"},
                {"at": WORM_START + 1560, "label": "first public detection (StepSecurity)",
                 "packages": 42, "source": "published record"},
                {"at": WORM_START + 16200, "label": "npm -> PyPI crossing", "packages": 120,
                 "source": "stub"},
                {"at": WORM_START + 30600, "label": "end of day: 170+ packages", "packages": 170,
                 "source": "published record"},
            ],
            "window_start": WORM_START,
            "window_end": WORM_START + 30600,
            "stats": {"ticks": 5, "counts_are_stub": True},
        },
    )


@app.get("/api/health")
def health() -> dict[str, Any]:
    return _timed(
        HEALTH_CYPHER,
        lambda: {"ok": True, "hydradb_connected": hydradb_ping()},
    )


# Mount last so /api/* path operations win. html=True serves index.html at /.
# check_dir=False: W4 may still be writing app.css/app.js/mock.js; missing files
# 404, they must not prevent the API from starting.
_STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True, check_dir=False), name="ui")
