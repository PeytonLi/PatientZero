"""Patient Zero HTTP API — bounded algo.SSpaths plus Parquet joins.

Every response carries `cypher`, `latency_ms`, and `stub`. `stub` is false:
handlers call HydraDB (or an injected runner in tests) and join names/hooks
from Parquet. Precision@K is scored against the IOC validation split only
when a forecast actually returned paths; otherwise it stays JSON null.
R0 is the mean number of validation pids reached per seed, measured
from those same paths. Min-cut is greedy cover on T2, not Edmonds-Karp.
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

from .db import HEALTH_CYPHER, bolt_driver, ping as hydradb_ping
from .engine import Engine, SENTINEL_VALID_TO, WORM_START

log = logging.getLogger("patient_zero.api")

STUB = False

_state: dict[str, Any] = {"engine": None, "driver": None}


def configure(engine: Engine | None) -> None:
    """Tests inject a fake runner. Production lifespan builds a live engine."""
    _state["engine"] = engine


def get_engine() -> Engine:
    engine = _state.get("engine")
    if engine is None:
        engine = Engine.live()
        _state["engine"] = engine
    return engine


class BlastRadiusReq(BaseModel):
    ecosystem: str = "npm"
    name: str = "@tanstack/react-query"
    version: str = "5.101.4"
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
    sid: str = "svc:mattermost"
    finding_vids: list[str] = Field(default_factory=list)
    as_of: int = WORM_START + 360


def _bolt_runner(driver):
    def run(cypher: str, params: dict[str, Any]) -> list[Any]:
        with driver.session() as session:
            return [record["path"] for record in session.run(cypher, **params)]

    return run


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    created = False
    driver = None
    if _state["engine"] is None:
        try:
            driver = bolt_driver()
            driver.verify_connectivity()
            _state["driver"] = driver
            configure(Engine.live(run_paths=_bolt_runner(driver)))
            created = True
            log.info("API wired to HydraDB; stub=false")
        except Exception:
            log.exception("HydraDB unavailable; traversals return empty path sets")
            configure(Engine.live(run_paths=lambda _q, _p: []))
            created = True
    yield
    if created:
        configure(None)
        if driver is not None:
            driver.close()
        _state["driver"] = None


app = FastAPI(title="Patient Zero", version="0.1.0", lifespan=lifespan)

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
    t0 = time.perf_counter()
    body = build()
    body["cypher"] = body.get("cypher") or cypher
    body["latency_ms"] = round((time.perf_counter() - t0) * 1000, 3)
    body["stub"] = STUB
    return body


@app.post("/api/blast-radius")
def blast_radius(req: BlastRadiusReq) -> dict[str, Any]:
    engine = get_engine()
    return _timed(
        "",
        lambda: engine.blast_radius(
            ecosystem=req.ecosystem,
            name=req.name,
            version=req.version,
            window_start=req.window_start,
            window_end=req.window_end,
            max_hops=req.max_hops,
            limit=req.limit,
        ),
    )


@app.post("/api/forecast")
def forecast(req: ForecastReq) -> dict[str, Any]:
    engine = get_engine()
    return _timed(
        "",
        lambda: engine.forecast(
            seeds=req.seeds,
            as_of=req.as_of,
            k=req.k,
            topology=req.topology,
            max_hops=req.max_hops,
            limit=req.limit,
        ),
    )


@app.post("/api/index-case")
def index_case(req: IndexCaseReq) -> dict[str, Any]:
    engine = get_engine()
    return _timed(
        "",
        lambda: engine.index_case(
            observed=req.observed,
            as_of=req.as_of,
            k=req.k,
            max_hops=req.max_hops,
            limit=req.limit,
        ),
    )


@app.post("/api/reachability")
def reachability(req: ReachabilityReq) -> dict[str, Any]:
    engine = get_engine()
    return _timed(
        "",
        lambda: engine.reachability(
            sid=req.sid,
            finding_vids=req.finding_vids,
            as_of=req.as_of,
        ),
    )


@app.get("/api/leverage")
def leverage(k: int = 5, max_hops: int = 4, limit: int = 500) -> dict[str, Any]:
    engine = get_engine()
    return _timed("", lambda: engine.leverage(k=k, max_hops=max_hops, limit=limit))


@app.get("/api/evidence")
def evidence() -> dict[str, Any]:
    engine = get_engine()
    return _timed("", lambda: engine.evidence())


@app.get("/api/timeline")
def timeline() -> dict[str, Any]:
    engine = get_engine()
    return _timed("", lambda: engine.timeline())


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    engine = get_engine()
    return _timed("", lambda: engine.meta())


@app.get("/api/health")
def health() -> dict[str, Any]:
    return _timed(
        HEALTH_CYPHER,
        lambda: {
            "ok": True,
            "hydradb_connected": hydradb_ping(),
            "catalog_nodes": len(get_engine().catalog.by_hydra),
        },
    )


_STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True, check_dir=False), name="ui")
