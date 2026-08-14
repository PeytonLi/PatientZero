"""Assemble the 14-table graph from already-fetched documents. No network."""

from __future__ import annotations

from typing import Any

from patient_zero.advisories import advisory_tables
from patient_zero.assemble import _split_pid, assemble
from patient_zero.depends import depends_on_edges
from patient_zero.expand import packages_from_search
from patient_zero.merge import ensure_endpoint_nodes, merge_tables


def _empty() -> dict[str, list[dict[str, Any]]]:
    return {
        "packages": [],
        "versions": [],
        "maintainers": [],
        "repos": [],
        "workflows": [],
        "services": [],
        "advisories": [],
        "edges_depends_on": [],
        "edges_pins": [],
        "edges_maintains": [],
        "edges_published_from": [],
        "edges_has_workflow": [],
        "edges_publishes_via_oidc": [],
        "edges_affects": [],
    }


def _package_stub(pid_s: str) -> dict[str, str]:
    eco, name = _split_pid(pid_s)
    return {"pid": pid_s, "ecosystem": eco, "name": name}


def _expansion(searches: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    packages: dict[str, dict[str, str]] = {}
    maintains: list[dict[str, str]] = []
    for login, search in searches.items():
        for row in packages_from_search(search, login=login, ecosystem="npm"):
            packages[row["pid"]] = _package_stub(row["pid"])
            maintains.append({"mid": row["mid"], "pid": row["pid"]})
    return {"packages": list(packages.values()), "edges_maintains": maintains}


def _depends(
    dep_graphs: dict[str, dict[str, Any]],
    versions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    published = {row["vid"]: row.get("published_at") for row in versions}
    rows: list[dict[str, Any]] = []
    for vid_s, graph in dep_graphs.items():
        rows.extend(depends_on_edges(graph, published_at=published.get(vid_s)))
    return rows


def _oidc_edges(
    workflows: list[dict[str, Any]],
    published_from: list[dict[str, str]],
) -> list[dict[str, str]]:
    pids_by_rid: dict[str, list[str]] = {}
    for row in published_from:
        pids_by_rid.setdefault(row["rid"], []).append(row["pid"])
    edges: list[dict[str, str]] = []
    for wf in workflows:
        if not wf.get("has_oidc_publish"):
            continue
        for pid_s in pids_by_rid.get(wf["rid"], []):
            edges.append({"wid": wf["wid"], "pid": pid_s})
    return edges


def build_graph(
    *,
    ioc_records: list[dict[str, Any]],
    packuments: list[dict[str, Any]],
    dep_graphs: dict[str, dict[str, Any]] | None = None,
    searches: dict[str, dict[str, Any]] | None = None,
    services: list[dict[str, Any]] | None = None,
    pins: list[dict[str, Any]] | None = None,
    workflows: list[dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    tables = merge_tables(_empty(), assemble(ioc_records, packuments))
    tables = merge_tables(tables, _expansion(searches or {}))
    tables["edges_depends_on"] = _depends(dep_graphs or {}, tables["versions"])
    tables["services"] = list(services or [])
    tables["edges_pins"] = list(pins or [])
    tables["workflows"] = list(workflows or [])
    tables["edges_has_workflow"] = [
        {"rid": wf["rid"], "wid": wf["wid"]} for wf in tables["workflows"]
    ]
    tables["edges_publishes_via_oidc"] = _oidc_edges(
        tables["workflows"], tables["edges_published_from"]
    )
    advisories, affects = advisory_tables(ioc_records)
    tables["advisories"] = advisories
    tables["edges_affects"] = affects
    ensure_endpoint_nodes(tables)
    return merge_tables(_empty(), tables)
