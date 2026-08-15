"""Bounded algo.SSpaths in three time directions. Join names from the catalog.

HydraDB 0.1.0 SSpaths takes integer `$sourceNode` (the hydra_id). Path nodes
come back with empty properties; identity is `element_id`. T1 bitemporal
filters run on relationship properties after the procedure returns — the
server rejects MATCH+CALL and `WHERE all(r IN relationships(path) ...)`.
"""

from __future__ import annotations

import logging
import threading
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
_SHARED_LABELS = frozenset({"Maintainer", "Repo", "Workflow"})
VECTOR_DEFAULT = 1
VECTOR_TRUST_WORKFLOW = 2  # pull_request_target or OIDC publish; fixed before any live run


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


def _path_vector(decoded: DecodedPath, catalog: Catalog) -> int:
    for stable, label in zip(decoded.stables, decoded.labels):
        if label != "Workflow":
            continue
        rec = catalog.rec(stable)
        row = rec.row if rec else {}
        if row.get("uses_pull_request_target") or row.get("has_oidc_publish"):
            return VECTOR_TRUST_WORKFLOW
    return VECTOR_DEFAULT


def _shared_on_path(decoded: DecodedPath) -> tuple[str | None, str]:
    for stable, label in zip(decoded.stables, decoded.labels):
        if label in _SHARED_LABELS:
            return stable, label
    return None, ""


def _path_weight(decoded: DecodedPath, catalog: Catalog) -> float:
    entity, _label = _shared_on_path(decoded)
    deg = catalog.degree(entity) if entity else 1
    return (1.0 / deg) * _path_vector(decoded, catalog)


def _forecast_key(
    topology: str, seed_list: list[str], as_of: int, k: int, max_hops: int, limit: int
) -> tuple[Any, ...]:
    return (topology, tuple(seed_list), as_of, k, max_hops, _bound(limit, k))


def _mean_validation_hits(
    reached: dict[str, frozenset[str]], seeds: list[str], truth: frozenset[str]
) -> float:
    if not seeds:
        return 0.0
    hits = [len(reached.get(seed, frozenset()) & truth) for seed in seeds]
    return round(sum(hits) / len(hits), 4)


def _greedy_cover(
    covers: dict[str, frozenset[str]],
    universe: set[str],
    kinds: dict[str, str],
) -> tuple[list[dict[str, Any]], float | None]:
    inverted: dict[str, set[str]] = defaultdict(set)
    for pid, ents in covers.items():
        if pid not in universe:
            continue
        for entity in ents:
            inverted[entity].add(pid)
    remaining = set(universe)
    picked: list[dict[str, Any]] = []
    reachable = len(universe)
    while remaining:
        best: str | None = None
        best_got: set[str] = set()
        for entity, pids in inverted.items():
            got = pids & remaining
            if not got:
                continue
            if len(got) > len(best_got) or (
                len(got) == len(best_got) and (best is None or entity < best)
            ):
                best = entity
                best_got = got
        if best is None:
            break
        kind = kinds.get(best, "maintainer")
        picked.append(
            {
                "id": best,
                "kind": kind,
                "covers": len(best_got),
                "action": "revoke" if kind == "maintainer" else "disable",
            }
        )
        remaining -= best_got
    if not reachable:
        return picked, None
    return picked, round((reachable - len(remaining)) / reachable, 4)


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
        self._forecast_lock = threading.Lock()
        self._evidence_cache: dict[tuple[int, int], dict[str, Any]] = {}
        self._forecast_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
        self._forecast_reached: dict[tuple[Any, ...], dict[str, frozenset[str]]] = {}
        self._forecast_covers: dict[tuple[Any, ...], dict[str, frozenset[str]]] = {}
        self._forecast_entity_kind: dict[tuple[Any, ...], dict[str, str]] = {}
        self._forecast_entity_path: dict[tuple[Any, ...], dict[str, list[str]]] = {}

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
        cache_key = _forecast_key(topology, seed_list, as_of, k, max_hops, limit)
        cached = self._forecast_cache.get(cache_key)
        if cached is not None:
            return cached
        with self._forecast_lock:
            cached = self._forecast_cache.get(cache_key)
            if cached is not None:
                return cached
            return self._forecast_compute(
                seed_list=seed_list,
                seed_set=seed_set,
                trust=trust,
                topology=topology,
                as_of=as_of,
                k=k,
                max_hops=max_hops,
                limit=limit,
                cache_key=cache_key,
            )

    def _forecast_compute(
        self,
        *,
        seed_list: list[str],
        seed_set: set[str],
        trust: bool,
        topology: str,
        as_of: int,
        k: int,
        max_hops: int,
        limit: int,
        cache_key: tuple[Any, ...],
    ) -> dict[str, Any]:
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
        scores: dict[str, float] = defaultdict(float)
        example: dict[str, list[str]] = {}
        best_w: dict[str, float] = {}
        reached_by_source: dict[str, set[str]] = defaultdict(set)
        covers: dict[str, set[str]] = defaultdict(set)
        entity_kind: dict[str, str] = {}
        entity_path: dict[str, list[str]] = {}
        for src in sources:
            src_pid = src
            if not trust:
                rec = self.catalog.rec(src)
                src_pid = (rec.row.get("pid") if rec else None) or src
            for raw in self._safe_paths(cypher, src):
                decoded = self.decode(raw)
                if decoded is None:
                    continue
                if not trust and not decoded.in_window(as_of):
                    continue
                cand = self._forecast_candidate(decoded, seed_set, trust)
                if not cand:
                    continue
                weight = _path_weight(decoded, self.catalog)
                scores[cand] += weight
                if weight >= best_w.get(cand, float("-inf")):
                    example[cand] = decoded.stables
                    best_w[cand] = weight
                reached_by_source[src_pid].add(cand)
                entity, label = _shared_on_path(decoded)
                if entity:
                    covers[cand].add(entity)
                    entity_kind.setdefault(entity, _KIND.get(label, "maintainer"))
                    entity_path.setdefault(entity, decoded.stables)
        ranked = sorted(scores, key=lambda pid: (-scores[pid], pid))[:k]
        peak = max(scores.values(), default=1.0)
        preds = [
            {
                "pid": pid,
                "score": round(scores[pid] / peak, 4) if peak else 0.0,
                "justification_path": example[pid],
            }
            for pid in ranked
        ]
        body = {
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
        self._forecast_cache[cache_key] = body
        self._forecast_reached[cache_key] = {
            src: frozenset(pids) for src, pids in reached_by_source.items()
        }
        self._forecast_covers[cache_key] = {pid: frozenset(ents) for pid, ents in covers.items()}
        self._forecast_entity_kind[cache_key] = entity_kind
        self._forecast_entity_path[cache_key] = entity_path
        return body

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
        best: dict[tuple[str, str], float] = {}
        for obs in observed_list:
            if obs not in self.catalog.by_stable:
                continue
            for raw in self._safe_paths(cypher, obs):
                decoded = self.decode(raw)
                if decoded is None:
                    continue
                vector = _path_vector(decoded, self.catalog)
                for stable, label in zip(decoded.stables, decoded.labels):
                    kind = _KIND.get(label)
                    if not kind:
                        continue
                    weight = (1.0 / self.catalog.degree(stable)) * vector
                    pair = (stable, obs)
                    if weight >= best.get(pair, float("-inf")):
                        best[pair] = weight
                    coverage[stable].add(obs)
                    kind_of[stable] = kind
                    example.setdefault(stable, list(reversed(decoded.stables)))
        scores: dict[str, float] = defaultdict(float)
        for (stable, _obs), weight in best.items():
            scores[stable] += weight
        ranked = sorted(scores, key=lambda s: (-scores[s], s))
        peak = max(scores.values(), default=1.0)
        candidates = []
        for stable in ranked[:k]:
            candidates.append(
                {
                    "id": stable,
                    "kind": kind_of[stable],
                    "score": round(scores[stable] / peak, 4) if peak else 0.0,
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
        seeds = sorted(self.catalog.seed_pids)
        as_of = WORM_START + 360
        measure_k = max(k, 100)
        measure_hops = 3
        trust = self.forecast(
            seeds=seeds,
            as_of=as_of,
            k=measure_k,
            topology="trust",
            max_hops=measure_hops,
            limit=measure_k,
        )
        fkey = _forecast_key("trust", seeds, as_of, measure_k, measure_hops, measure_k)
        covers = self._forecast_covers.get(fkey) or {}
        kinds = self._forecast_entity_kind.get(fkey) or {}
        paths = self._forecast_entity_path.get(fkey) or {}
        at_risk: dict[str, set[str]] = defaultdict(set)
        for pid, ents in covers.items():
            for entity in ents:
                at_risk[entity].add(pid)
        ranked_ids = sorted(at_risk, key=lambda e: (-len(at_risk[e]), e))
        ranked: list[dict[str, Any]] = []
        for eid in ranked_ids[:k]:
            rec = self.catalog.rec(eid)
            ranked.append(
                {
                    "id": eid,
                    "kind": kinds.get(eid, "maintainer"),
                    "packages_at_risk": len(at_risk[eid]),
                    "path": paths.get(eid) or [eid],
                    "packages_maintained": self.catalog.degree(eid),
                    "login": rec.name if rec else eid,
                }
            )
        universe = {pid for pid in covers if pid in self.catalog.validation_pids}
        mincut, blocked = _greedy_cover(covers, universe, kinds)
        return {
            "cypher": trust["cypher"],
            "ranked": ranked,
            "mincut": mincut,
            "stats": {
                "k": k,
                "max_hops": max_hops,
                "result_limit": _bound(limit, k),
                "spread_blocked_pct": blocked,
                "cover": "greedy",
                "reachable_validation": len(universe),
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

        trust_key = _forecast_key("trust", seeds, as_of, k, 3, k)
        dep_key = _forecast_key("dependency", seeds, as_of, k, 3, k)
        r0_trust = _mean_validation_hits(
            self._forecast_reached.get(trust_key) or {}, seeds, truth
        )
        r0_dep = _mean_validation_hits(
            self._forecast_reached.get(dep_key) or {}, seeds, truth
        )
        body = {
            "cypher": cypher,
            "precision_trust": pack(trust["predictions"], "trust"),
            "precision_dependency": pack(
                dep["predictions"], "dependency", role="negative control"
            ),
            "r0_trust": r0_trust,
            "r0_dependency": r0_dep,
            "note": "precision@K and R0 scored against IOC validation pids. Min-cut is greedy cover.",
            "stats": {
                "measured": True,
                "ioc_set_loaded": True,
                "seeds": len(seeds),
                "validation_pids": len(truth),
                "r0_definition": "mean validation pids reached per seed",
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
        nodes = []
        seen_pids: set[str] = set()
        for row in records:
            pid = row.get("pid")
            at = row.get("first_seen_utc")
            if not pid or at is None or pid in seen_pids:
                continue
            seen_pids.add(pid)
            eco = "pypi" if str(pid).startswith("pypi:") else "npm"
            role = "origin" if row.get("split") == "seed" else "hit"
            nodes.append(
                {
                    "id": pid,
                    "at": at,
                    "eco": eco,
                    "role": role,
                    "label": str(pid).split(":", 1)[-1],
                }
            )
        return {
            "cypher": cypher,
            "events": events,
            "nodes": nodes,
            "window_start": WORM_START,
            "window_end": WORM_START + 30600,
            "stats": {
                "ticks": len(events),
                "counts_are_stub": not bool(records),
            },
        }

    def meta(self) -> dict[str, Any]:
        seed = None
        vid = None
        for pid in sorted(self.catalog.seed_pids):
            found = self.catalog.first_vid(pid)
            if found:
                seed = pid
                vid = found
                break
        if seed is None:
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
