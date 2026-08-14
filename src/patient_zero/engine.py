"""Bounded algo.SSpaths in three time directions. Join names from the catalog.

HydraDB 0.1.0 SSpaths takes integer `$sourceNode` (the hydra_id). Path nodes
come back with empty properties; identity is `element_id`. T1 bitemporal
filters run on relationship properties after the procedure returns — the
server rejects MATCH+CALL and `WHERE all(r IN relationships(path) ...)`.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from .catalog import Catalog
from .cypher import T1_RELS, T2_RELS, ss_paths
from .ids import hydra_id

log = logging.getLogger("patient_zero.engine")

WORM_START = 1778527200
SENTINEL_VALID_TO = 4102444800
TRUE_ORIGIN_MID = "npm:tannerlinsley"  # TanStack postmortem; used only to rank, never as a seed

RunPaths = Callable[[str, dict[str, Any]], list[Any]]
_KIND = {"Maintainer": "maintainer", "Repo": "repo", "Workflow": "workflow", "Service": "service"}


def _bound(limit: int, k: int | None = None) -> int:
    """pathCount 500 per seed hangs the scrubber. Cap to what the UI can show."""
    target = limit if k is None else max(k * 8, 32)
    return min(limit, target, 200)


def _node_id(node: Any) -> int:
    eid = getattr(node, "element_id", None)
    if eid is not None:
        return int(eid)
    if isinstance(node, int):
        return node
    try:
        return int(node["id"])
    except Exception as exc:
        raise TypeError(f"cannot read hydra id from {type(node)!r}") from exc


def _node_label(node: Any) -> str:
    labels = getattr(node, "labels", None)
    if labels:
        return next(iter(labels))
    return ""


def _rel_type(rel: Any) -> str:
    return str(getattr(rel, "type", "") or "")


def _rel_props(rel: Any) -> dict[str, Any]:
    if isinstance(rel, dict):
        return rel
    try:
        return dict(rel)
    except Exception:
        out: dict[str, Any] = {}
        getter = getattr(rel, "get", None)
        if getter:
            for key in ("valid_from", "valid_to", "id"):
                val = getter(key)
                if val is not None:
                    out[key] = val
        return out


def _in_window(props: dict[str, Any], as_of: int) -> bool:
    vf = props.get("valid_from")
    vt = props.get("valid_to")
    if vf is None:
        return True
    end = SENTINEL_VALID_TO if vt is None else vt
    return vf <= as_of < end


class DecodedPath:
    def __init__(self, stables: list[str], labels: list[str], rels: list[dict[str, Any]], types: list[str]):
        self.stables = stables
        self.labels = labels
        self.rel_props = rels
        self.rel_types = types

    def in_window(self, as_of: int) -> bool:
        return all(_in_window(props, as_of) for props in self.rel_props)

    def exposed_at(self) -> int | None:
        times = [
            props["valid_from"]
            for props, typ in zip(self.rel_props, self.rel_types)
            if typ == "PINS" and props.get("valid_from") is not None
        ]
        return max(times) if times else None


class Engine:
    def __init__(self, catalog: Catalog, run_paths: RunPaths):
        self.catalog = catalog
        self.run_paths = run_paths
        self._evidence_cache: dict[tuple[int, int], dict[str, Any]] = {}

    @classmethod
    def live(
        cls,
        *,
        graph_dir: Path | None = None,
        ioc_path: Path | None = None,
        run_paths: RunPaths | None = None,
    ) -> Engine:
        root = Path(__file__).resolve().parents[2]
        catalog = Catalog.from_dir(
            graph_dir or root / "data" / "graph",
            ioc_path or root / "artifacts" / "ioc.json",
        )
        return cls(catalog, run_paths=run_paths or _bolt_run_once)

    def decode(self, path: Any) -> DecodedPath | None:
        nodes = list(getattr(path, "nodes", path))
        rels = list(getattr(path, "relationships", []))
        stables: list[str] = []
        labels: list[str] = []
        for node in nodes:
            hid = _node_id(node)
            rec = self.catalog.by_hydra.get(hid)
            if rec is None:
                return None
            stables.append(rec.stable)
            labels.append(_node_label(node) or rec.label)
        return DecodedPath(
            stables,
            labels,
            [_rel_props(rel) for rel in rels],
            [_rel_type(rel) for rel in rels],
        )

    def _safe_paths(self, cypher: str, source: str) -> list[Any]:
        try:
            return list(self.run_paths(cypher, {"sourceNode": hydra_id(source)}) or [])
        except Exception:
            log.exception("SSpaths failed for %s", source)
            return []

    def blast_radius(
        self,
        *,
        ecosystem: str,
        name: str,
        version: str,
        window_start: int,
        window_end: int,
        max_hops: int,
        limit: int,
    ) -> dict[str, Any]:
        source = self.catalog.resolve_vid(ecosystem, name, version)
        bound = _bound(limit)
        cypher = ss_paths(
            rel_types=T1_RELS,
            direction="incoming",
            max_len=max_hops,
            path_count=bound,
            result_limit=bound,
        )
        services: list[dict[str, Any]] = []
        seen: set[str] = set()
        paths_kept = 0
        if source:
            for raw in self._safe_paths(cypher, source):
                decoded = self.decode(raw)
                if decoded is None or not decoded.stables:
                    continue
                if not decoded.in_window(window_end):
                    continue
                paths_kept += 1
                if decoded.labels[-1] != "Service":
                    continue
                sid = decoded.stables[-1]
                if sid in seen:
                    continue
                seen.add(sid)
                rec = self.catalog.rec(sid)
                services.append(
                    {
                        "sid": sid,
                        "name": (rec.name if rec else sid.removeprefix("svc:")),
                        "exposed_at": decoded.exposed_at() or window_end,
                        "path": decoded.stables,
                    }
                )
        return {
            "cypher": cypher,
            "services": services,
            "stats": {
                "source_vid": source or f"{ecosystem}:{name}@{version}",
                "services_exposed": len(services),
                "paths_returned": paths_kept,
                "max_hops": max_hops,
                "result_limit": bound,
                "as_of": window_end,
                "window_start": window_start,
            },
        }

    def forecast(
        self,
        *,
        seeds: list[str],
        as_of: int,
        k: int,
        topology: str,
        max_hops: int,
        limit: int,
    ) -> dict[str, Any]:
        seed_list = list(seeds) or sorted(self.catalog.seed_pids)
        seed_set = set(seed_list)
        trust = topology == "trust"
        bound = _bound(limit, k)
        if trust:
            cypher = ss_paths(
                rel_types=T2_RELS,
                direction="both",
                max_len=max_hops,
                path_count=bound,
                result_limit=bound,
            )
            sources = [pid for pid in seed_list if pid in self.catalog.by_stable]
        else:
            # Package nodes have no DEPENDS_ON/PINS. Control starts at a Version.
            cypher = ss_paths(
                rel_types=T1_RELS,
                direction="incoming",
                max_len=max_hops,
                path_count=bound,
                result_limit=bound,
            )
            sources = [
                vid
                for pid in seed_list
                if (vid := self.catalog.first_vid(pid))
            ]
        support: dict[str, int] = defaultdict(int)
        example: dict[str, list[str]] = {}
        for src in sources:
            for raw in self._safe_paths(cypher, src):
                decoded = self.decode(raw)
                if decoded is None:
                    continue
                if not trust and not decoded.in_window(as_of):
                    continue
                cand = self._forecast_candidate(decoded, seed_set, trust)
                if cand:
                    support[cand] += 1
                    example.setdefault(cand, decoded.stables)
        ranked = sorted(support, key=lambda pid: (-support[pid], pid))[:k]
        peak = max(support.values(), default=1)
        preds = [
            {
                "pid": pid,
                "score": round(support[pid] / peak, 4),
                "justification_path": example[pid],
            }
            for pid in ranked
        ]
        return {
            "cypher": cypher,
            "predictions": preds,
            "stats": {
                "topology": topology,
                "is_negative_control": not trust,
                "seeds": len(seed_list),
                "k": k,
                "max_hops": max_hops,
                "result_limit": bound,
                "as_of": as_of,
                "precision_at_k": None,
            },
        }

    def _forecast_candidate(self, decoded: DecodedPath, seed_set: set[str], trust: bool) -> str | None:
        if trust:
            if decoded.labels and decoded.labels[-1] == "Package":
                pid = decoded.stables[-1]
                return pid if pid not in seed_set else None
            return None
        for stable, label in zip(reversed(decoded.stables), reversed(decoded.labels)):
            if label != "Version":
                continue
            rec = self.catalog.rec(stable)
            pid = rec.row.get("pid") if rec else None
            if pid and pid not in seed_set:
                return pid
            return None
        return None

    def index_case(
        self,
        *,
        observed: list[str],
        as_of: int,
        k: int,
        max_hops: int,
        limit: int,
    ) -> dict[str, Any]:
        observed_list = list(observed) or sorted(self.catalog.seed_pids)
        bound = _bound(limit, k)
        cypher = ss_paths(
            rel_types=T2_RELS,
            direction="both",
            max_len=max_hops,
            path_count=bound,
            result_limit=bound,
        )
        coverage: dict[str, set[str]] = defaultdict(set)
        example: dict[str, list[str]] = {}
        kind_of: dict[str, str] = {}
        for obs in observed_list:
            if obs not in self.catalog.by_stable:
                continue
            for raw in self._safe_paths(cypher, obs):
                decoded = self.decode(raw)
                if decoded is None:
                    continue
                for stable, label in zip(decoded.stables, decoded.labels):
                    kind = _KIND.get(label)
                    if not kind:
                        continue
                    coverage[stable].add(obs)
                    kind_of[stable] = kind
                    example.setdefault(stable, list(reversed(decoded.stables)))
        n_obs = max(len(observed_list), 1)
        ranked = sorted(coverage, key=lambda s: (-len(coverage[s]), s))
        candidates = []
        for stable in ranked[:k]:
            candidates.append(
                {
                    "id": stable,
                    "kind": kind_of[stable],
                    "score": round(len(coverage[stable]) / n_obs, 4),
                    "path_to_observed": example[stable],
                }
            )
        true_origin_rank = None
        for i, cand in enumerate(candidates, 1):
            if cand["id"] == TRUE_ORIGIN_MID:
                true_origin_rank = i
                break
        return {
            "cypher": cypher,
            "candidates": candidates,
            "stats": {
                "observed": len(observed_list),
                "k": k,
                "max_hops": max_hops,
                "result_limit": bound,
                "as_of": as_of,
                "true_origin_rank": true_origin_rank,
            },
        }

    def reachability(self, *, sid: str, finding_vids: list[str], as_of: int) -> dict[str, Any]:
        cypher = ss_paths(
            rel_types=("PINS",),
            direction="outgoing",
            max_len=1,
            path_count=max(len(finding_vids), 1) * 4,
            result_limit=max(len(finding_vids), 1) * 4,
        )
        findings = list(finding_vids)
        pin_rows = [p for p in self.catalog.pins if p.get("sid") == sid]
        by_vid = {p["dst_vid"]: p for p in pin_rows}
        verdicts: list[dict[str, Any]] = []
        for vid in findings:
            pin = by_vid.get(vid)
            if pin is not None and not _in_window(pin, as_of):
                continue
            if pin is None:
                rec = self.catalog.rec(vid)
                hooks = list((rec.row.get("install_hooks") or []) if rec else [])
                verdicts.append(
                    {
                        "vid": vid,
                        "tier": "none",
                        "evidence": {"has_install_script": False, "install_hooks": hooks},
                    }
                )
                continue
            rec = self.catalog.rec(vid)
            hooks = list((rec.row.get("install_hooks") or []) if rec else [])
            has = bool(rec.row.get("has_install_script")) if rec else False
            if hooks:
                has = True
            verdicts.append(
                {
                    "vid": vid,
                    "tier": "install" if has else "none",
                    "evidence": {"has_install_script": has, "install_hooks": hooks},
                }
            )
        executing = sum(1 for v in verdicts if v["tier"] == "install")
        return {
            "cypher": cypher,
            "verdicts": verdicts,
            "stats": {
                "sid": sid,
                "findings_in": len(findings),
                "findings_executing": executing,
                "as_of": as_of,
            },
        }

    def leverage(self, *, k: int, max_hops: int, limit: int) -> dict[str, Any]:
        rels = tuple(T2_RELS) + tuple(T1_RELS)
        bound = _bound(limit, k)
        cypher = ss_paths(
            rel_types=rels,
            direction="both",
            max_len=max_hops,
            path_count=bound,
            result_limit=bound,
        )
        mids = sorted(
            self.catalog.maintainer_degree,
            key=lambda mid: (-self.catalog.maintainer_degree[mid], mid),
        )[:k]
        ranked: list[dict[str, Any]] = []
        for mid in mids:
            services: set[str] = set()
            example: list[str] | None = None
            for raw in self._safe_paths(cypher, mid):
                decoded = self.decode(raw)
                if decoded is None:
                    continue
                for stable, label in zip(decoded.stables, decoded.labels):
                    if label == "Service":
                        services.add(stable)
                        example = example or decoded.stables
            rec = self.catalog.rec(mid)
            ranked.append(
                {
                    "id": mid,
                    "kind": "maintainer",
                    "services_at_risk": len(services),
                    "path": example or [mid],
                    "packages_maintained": self.catalog.maintainer_degree.get(mid, 0),
                    "login": rec.name if rec else mid,
                }
            )
        ranked.sort(key=lambda row: (-row["services_at_risk"], -row["packages_maintained"], row["id"]))
        return {
            "cypher": cypher,
            "ranked": ranked,
            "mincut": [],
            "stats": {
                "k": k,
                "max_hops": max_hops,
                "result_limit": bound,
                "spread_blocked_pct": None,
            },
        }

    def evidence(self, *, k: int = 100, as_of: int = WORM_START + 360) -> dict[str, Any]:
        cached = self._evidence_cache.get((k, as_of))
        if cached is not None:
            return cached
        unmeasured = {
            "precision_at_10": None,
            "precision_at_50": None,
            "precision_at_100": None,
            "recall_at_100": None,
            "measured": False,
        }
        cypher = (
            "// control: identical forecast, relTypes swapped, scored against IOC validation pids\n"
            + ss_paths(
                rel_types=T2_RELS,
                direction="both",
                max_len=3,
                path_count=k,
                result_limit=k,
            )
        )
        seeds = sorted(self.catalog.seed_pids)
        key = (k, as_of)
        if not seeds or not self.catalog.validation_pids:
            body = {
                "cypher": cypher,
                "precision_trust": dict(unmeasured, topology="trust"),
                "precision_dependency": dict(
                    unmeasured, topology="dependency", role="negative control"
                ),
                "r0_trust": None,
                "r0_dependency": None,
                "note": "IOC split missing; precision is not invented.",
                "stats": {"measured": False, "ioc_set_loaded": False},
            }
            self._evidence_cache[key] = body
            return body
        trust = self.forecast(
            seeds=seeds, as_of=as_of, k=k, topology="trust", max_hops=3, limit=k
        )
        dep = self.forecast(
            seeds=seeds, as_of=as_of, k=k, topology="dependency", max_hops=3, limit=k
        )
        if not trust["predictions"] and not dep["predictions"]:
            body = {
                "cypher": cypher,
                "precision_trust": dict(unmeasured, topology="trust"),
                "precision_dependency": dict(
                    unmeasured, topology="dependency", role="negative control"
                ),
                "r0_trust": None,
                "r0_dependency": None,
                "note": "No forecast paths returned; precision is not invented.",
                "stats": {"measured": False, "ioc_set_loaded": True},
            }
            self._evidence_cache[key] = body
            return body
        truth = self.catalog.validation_pids

        def precision(preds: list[dict[str, Any]], kk: int) -> float:
            top = [row["pid"] for row in preds[:kk]]
            if not top:
                return 0.0
            return round(sum(1 for pid in top if pid in truth) / len(top), 4)

        def recall(preds: list[dict[str, Any]], kk: int) -> float:
            if not truth:
                return 0.0
            top = {row["pid"] for row in preds[:kk]}
            return round(len(top & truth) / len(truth), 4)

        def pack(preds: list[dict[str, Any]], topology: str, **extra: Any) -> dict[str, Any]:
            return {
                "precision_at_10": precision(preds, 10),
                "precision_at_50": precision(preds, 50),
                "precision_at_100": precision(preds, 100),
                "recall_at_100": recall(preds, 100),
                "measured": True,
                "topology": topology,
                **extra,
            }

        body = {
            "cypher": cypher,
            "precision_trust": pack(trust["predictions"], "trust"),
            "precision_dependency": pack(
                dep["predictions"], "dependency", role="negative control"
            ),
            "r0_trust": None,
            "r0_dependency": None,
            "note": "precision@K is scored against IOC validation pids. R0 is not yet defined.",
            "stats": {
                "measured": True,
                "ioc_set_loaded": True,
                "seeds": len(seeds),
                "validation_pids": len(truth),
            },
        }
        self._evidence_cache[key] = body
        return body

    def timeline(self) -> dict[str, Any]:
        cypher = (
            "// published-record clock; per-tick counts from IOC first_seen_utc\n"
            "/* Version.published_at is not stored on HydraDB nodes */"
        )
        records = self.catalog.ioc_records
        ticks = (
            (WORM_START, "worm begins"),
            (WORM_START + 360, "42 @tanstack/* packages compromised (seed set)"),
            (WORM_START + 1560, "first public detection (StepSecurity)"),
            (WORM_START + 16200, "npm -> PyPI crossing"),
            (WORM_START + 30600, "end of day: 170+ packages"),
        )
        events = []
        for at, label in ticks:
            pids = {
                row["pid"]
                for row in records
                if row.get("first_seen_utc") is not None and row["first_seen_utc"] <= at
            }
            events.append(
                {
                    "at": at,
                    "label": label,
                    "packages": len(pids),
                    "source": "ioc" if records else "published record",
                }
            )
        return {
            "cypher": cypher,
            "events": events,
            "window_start": WORM_START,
            "window_end": WORM_START + 30600,
            "stats": {
                "ticks": len(events),
                "counts_are_stub": not bool(records),
            },
        }

    def meta(self) -> dict[str, Any]:
        seed = next(iter(sorted(self.catalog.seed_pids)), "npm:@tanstack/react-query")
        vid = self.catalog.first_vid(seed)
        version = "5.101.4"
        name = seed.split(":", 1)[-1]
        eco = seed.split(":", 1)[0] if ":" in seed else "npm"
        if vid and "@" in vid:
            version = vid.rsplit("@", 1)[-1]
        sid = next(
            (rec.stable for rec in self.catalog.by_stable.values() if rec.label == "Service"),
            "svc:mattermost",
        )
        return {
            "cypher": "// catalog lookup, not a traversal",
            "default_blast": {"ecosystem": eco, "name": name, "version": version},
            "default_sid": sid,
            "seed_pids": sorted(self.catalog.seed_pids),
        }


def _bolt_run_once(cypher: str, params: dict[str, Any]) -> list[Any]:
    from .db import bolt_driver

    driver = bolt_driver()
    try:
        with driver.session() as session:
            return [record["path"] for record in session.run(cypher, **params)]
    except Exception:
        log.exception("HydraDB SSpaths query failed")
        return []
    finally:
        driver.close()
