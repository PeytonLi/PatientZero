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


def _maintainer_aliases(by_stable: dict[str, NodeRec]) -> dict[str, list[str]]:
    by_login: dict[str, list[str]] = {}
    by_email: dict[str, list[str]] = {}
    for rec in by_stable.values():
        if rec.label != "Maintainer":
            continue
        login = str(rec.row.get("login") or rec.name or "").strip().lower()
        if login:
            by_login.setdefault(login, []).append(rec.stable)
        email = rec.row.get("email_domain")
        if email:
            by_email.setdefault(str(email).strip().lower(), []).append(rec.stable)
    aliases: dict[str, list[str]] = {}
    for group in list(by_login.values()) + list(by_email.values()):
        uniq = sorted(set(group))
        if len(uniq) < 2:
            continue
        for mid in uniq:
            others = [other for other in uniq if other != mid]
            bucket = aliases.setdefault(mid, [])
            for other in others:
                if other not in bucket:
                    bucket.append(other)
    return aliases


def _github_org(rid: str) -> str:
    _, _, rest = rid.partition(":")
    org, _, _ = rest.partition("/")
    return org.strip().lower()


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
    packages_by_entity: dict[str, list[str]]
    aliases_by_entity: dict[str, list[str]]
    repos_for_pid: dict[str, list[str]]

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
        packages_by_entity: dict[str, list[str]] = {}
        repos_for_pid: dict[str, list[str]] = {}

        def _touch(entity: str | None, pid_s: str | None) -> None:
            if not entity or not pid_s:
                return
            bucket = packages_by_entity.setdefault(entity, [])
            if pid_s not in bucket:
                bucket.append(pid_s)

        for edge in tables.get("edges_maintains") or []:
            mid = edge.get("mid")
            if mid:
                degree[mid] = degree.get(mid, 0) + 1
                entity_degree[mid] = entity_degree.get(mid, 0) + 1
            _touch(mid, edge.get("pid"))
        for edge in tables.get("edges_published_from") or []:
            rid = edge.get("rid")
            pid_s = edge.get("pid")
            if rid:
                entity_degree[rid] = entity_degree.get(rid, 0) + 1
            _touch(rid, pid_s)
            if pid_s and rid:
                bucket = repos_for_pid.setdefault(pid_s, [])
                if rid not in bucket:
                    bucket.append(rid)
        for edge in tables.get("edges_publishes_via_oidc") or []:
            wid = edge.get("wid")
            if wid:
                entity_degree[wid] = entity_degree.get(wid, 0) + 1
            _touch(wid, edge.get("pid"))
        for edge in tables.get("edges_has_workflow") or []:
            wid = edge.get("wid")
            if wid:
                entity_degree[wid] = max(entity_degree.get(wid, 0), 1)
        for entity, pids in packages_by_entity.items():
            packages_by_entity[entity] = sorted(pids)
        aliases_by_entity = _maintainer_aliases(by_stable)
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
            packages_by_entity=packages_by_entity,
            aliases_by_entity=aliases_by_entity,
            repos_for_pid=repos_for_pid,
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

    def packages_touched(self, stable: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for pid_s in self.packages_by_entity.get(stable) or []:
            rec = self.rec(pid_s)
            eco, _, name = pid_s.partition(":")
            rows.append(
                {
                    "pid": pid_s,
                    "name": str((rec.name if rec else None) or name),
                    "ecosystem": str(
                        (rec.row.get("ecosystem") if rec else None) or eco
                    ),
                }
            )
        return rows

    def aliases(self, stable: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for other in self.aliases_by_entity.get(stable) or []:
            rec = self.rec(other)
            eco, _, rest = other.partition(":")
            rows.append(
                {
                    "id": other,
                    "kind": (rec.label.lower() if rec else "maintainer"),
                    "name": str((rec.name if rec else None) or rest),
                    "ecosystem": str(
                        (rec.row.get("ecosystem") if rec else None) or eco
                    ),
                }
            )
        return rows

    def registries_for(self, stable: str) -> list[str]:
        ecos = {
            row["ecosystem"]
            for row in self.packages_touched(stable)
            if row.get("ecosystem")
        }
        orgs: set[str] = set()
        for pid_s in self.packages_by_entity.get(stable) or []:
            for rid in self.repos_for_pid.get(pid_s) or []:
                org = _github_org(rid)
                if org:
                    orgs.add(org)
        if orgs:
            for pid_s, rids in self.repos_for_pid.items():
                rec = self.rec(pid_s)
                eco = str(
                    (rec.row.get("ecosystem") if rec else None)
                    or pid_s.partition(":")[0]
                )
                if any(_github_org(rid) in orgs for rid in rids):
                    ecos.add(eco)
        return sorted(ecos)

    def ingest_maintains(self, rows: list[dict[str, str]]) -> int:
        """Merge MAINTAINS hits into this catalog. Returns how many packages were new."""
        added = 0
        for row in rows:
            mid_s = row.get("mid")
            pid_s = row.get("pid")
            if not mid_s or not pid_s:
                continue
            bucket = self.packages_by_entity.setdefault(mid_s, [])
            if pid_s in bucket:
                continue
            bucket.append(pid_s)
            bucket.sort()
            added += 1
            self.maintainer_degree[mid_s] = self.maintainer_degree.get(mid_s, 0) + 1
            self.entity_degree[mid_s] = self.entity_degree.get(mid_s, 0) + 1
            if pid_s not in self.by_stable:
                eco, _, name = pid_s.partition(":")
                rec = NodeRec(
                    stable=pid_s,
                    label="Package",
                    name=name,
                    row={"pid": pid_s, "ecosystem": eco, "name": name},
                )
                self.by_stable[pid_s] = rec
                self.by_hydra[hydra_id(pid_s)] = rec
        return added
