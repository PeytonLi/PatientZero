"""Join table for HydraDB integer `id` ↔ stable vid/pid/sid and extra fields.

HydraDB 0.1.0 nodes store `{id}` plus one label. Path records come back with
empty properties; `element_id` is the integer id as a string. Names, install
hooks, and IOC splits live in Parquet and are joined here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import pyarrow.parquet as pq

from .emit import GRAPH_FILES, _TABLE_KEY
from .ids import hydra_id, pid as make_pid, vid as make_vid

_NODE_KEY = {
    "packages": ("pid", "Package"),
    "versions": ("vid", "Version"),
    "maintainers": ("mid", "Maintainer"),
    "repos": ("rid", "Repo"),
    "workflows": ("wid", "Workflow"),
    "services": ("sid", "Service"),
    "advisories": ("aid", "Advisory"),
}


@dataclass(frozen=True)
class NodeRec:
    stable: str
    label: str
    name: str | None = None
    row: dict[str, Any] = field(default_factory=dict)


@dataclass
class Catalog:
    by_hydra: dict[int, NodeRec]
    by_stable: dict[str, NodeRec]
    versions_for_pid: dict[str, list[str]]
    seed_pids: frozenset[str]
    validation_pids: frozenset[str]
    pins: list[dict[str, Any]]
    ioc_records: list[dict[str, Any]]
    maintainer_degree: dict[str, int]
    entity_degree: dict[str, int]

    @classmethod
    def from_tables(
        cls,
        tables: dict[str, list[dict[str, Any]]],
        ioc_records: Iterable[dict[str, Any]] | None = None,
    ) -> Catalog:
        by_hydra: dict[int, NodeRec] = {}
        by_stable: dict[str, NodeRec] = {}
        versions_for_pid: dict[str, list[str]] = {}
        for table_name, (key, label) in _NODE_KEY.items():
            for row in tables.get(table_name) or []:
                stable = row.get(key)
                if not stable:
                    continue
                rec = NodeRec(
                    stable=stable,
                    label=label,
                    name=row.get("name") or row.get("login") or row.get("path"),
                    row=row,
                )
                hid = hydra_id(stable)
                by_hydra[hid] = rec
                by_stable[stable] = rec
                if label == "Version":
                    versions_for_pid.setdefault(row.get("pid") or "", []).append(stable)

        ioc = list(ioc_records or [])
        seed = frozenset(r["pid"] for r in ioc if r.get("split") == "seed")
        validation = frozenset(r["pid"] for r in ioc if r.get("split") == "validation")
        degree: dict[str, int] = {}
        entity_degree: dict[str, int] = {}
        for edge in tables.get("edges_maintains") or []:
            mid = edge.get("mid")
            if mid:
                degree[mid] = degree.get(mid, 0) + 1
                entity_degree[mid] = entity_degree.get(mid, 0) + 1
        for edge in tables.get("edges_published_from") or []:
            rid = edge.get("rid")
            if rid:
                entity_degree[rid] = entity_degree.get(rid, 0) + 1
        for edge in tables.get("edges_publishes_via_oidc") or []:
            wid = edge.get("wid")
            if wid:
                entity_degree[wid] = entity_degree.get(wid, 0) + 1
        for edge in tables.get("edges_has_workflow") or []:
            wid = edge.get("wid")
            if wid:
                entity_degree[wid] = max(entity_degree.get(wid, 0), 1)
        return cls(
            by_hydra=by_hydra,
            by_stable=by_stable,
            versions_for_pid=versions_for_pid,
            seed_pids=seed,
            validation_pids=validation,
            pins=list(tables.get("edges_pins") or []),
            ioc_records=ioc,
            maintainer_degree=degree,
            entity_degree=entity_degree,
        )

    @classmethod
    def from_dir(cls, graph_dir: Path, ioc_path: Path | None = None) -> Catalog:
        tables: dict[str, list[dict[str, Any]]] = {}
        for filename in GRAPH_FILES:
            path = graph_dir / filename
            key = _TABLE_KEY[filename]
            if path.is_file():
                tables[key] = pq.read_table(path).to_pylist()
            else:
                tables[key] = []
        ioc: list[dict[str, Any]] = []
        if ioc_path and ioc_path.is_file():
            payload = json.loads(ioc_path.read_text(encoding="utf-8"))
            ioc = payload.get("records", payload if isinstance(payload, list) else [])
        return cls.from_tables(tables, ioc_records=ioc)

    def stable(self, hid: int) -> str | None:
        rec = self.by_hydra.get(hid)
        return rec.stable if rec else None

    def rec(self, stable: str) -> NodeRec | None:
        return self.by_stable.get(stable)

    def resolve_vid(self, ecosystem: str, name: str, version: str) -> str | None:
        exact = make_vid(ecosystem, name, version)
        if exact in self.by_stable:
            return exact
        pkg = make_pid(ecosystem, name)
        versions = self.versions_for_pid.get(pkg) or []
        return versions[0] if versions else None

    def first_vid(self, package_id: str) -> str | None:
        versions = self.versions_for_pid.get(package_id) or []
        return versions[0] if versions else None

    def degree(self, stable: str) -> int:
        """MAINTAINS / PUBLISHED_FROM / OIDC-publish counts. Unknown → 1, never 0."""
        return max(int(self.entity_degree.get(stable) or 0), 1)
