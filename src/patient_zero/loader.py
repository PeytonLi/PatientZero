"""Single-threaded HydraDB loader. Shapes from docs/MEASURED.md.

Batch size 1000 (cap 1024). Nodes are `{id}` plus one SET label. Rel property
maps lead with `id:`. Extra node fields stay in Parquet.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from patient_zero.assemble import SENTINEL_VALID_TO
from patient_zero.ids import hydra_id
from patient_zero.cypher import (
    MAX_UNWIND_BATCH,
    PRELIMINARY_BATCH_SIZE,
    Q_INLINE,
    Q_MATCH_CREATE,
    Q_MATCH_CREATE_BITEMPORAL,
    Q_MERGE_NODES,
    q_create_rel,
    q_merge_nodes,
)
from patient_zero.emit import GRAPH_FILES

__all__ = [
    "MAX_UNWIND_BATCH",
    "PRELIMINARY_BATCH_SIZE",
    "Q_INLINE",
    "Q_MATCH_CREATE",
    "Q_MATCH_CREATE_BITEMPORAL",
    "Q_MERGE_NODES",
    "create_bitemporal_edges",
    "create_edges",
    "create_inline",
    "load_from_dir",
    "load_graph",
    "merge_version_nodes",
]

NODE_SPECS: tuple[tuple[str, str, str], ...] = (
    ("packages", "pid", "Package"),
    ("versions", "vid", "Version"),
    ("maintainers", "mid", "Maintainer"),
    ("repos", "rid", "Repo"),
    ("workflows", "wid", "Workflow"),
    ("services", "sid", "Service"),
    ("advisories", "aid", "Advisory"),
)

# table, src_label, src_field, rel, dst_label, dst_field, bitemporal
EDGE_SPECS: tuple[tuple[str, str, str, str, str, str, bool], ...] = (
    ("edges_depends_on", "Version", "src_vid", "DEPENDS_ON", "Version", "dst_vid", True),
    ("edges_pins", "Service", "sid", "PINS", "Version", "dst_vid", True),
    ("edges_affects", "Advisory", "aid", "AFFECTS", "Version", "vid", False),
    ("edges_maintains", "Maintainer", "mid", "MAINTAINS", "Package", "pid", False),
    ("edges_published_from", "Package", "pid", "PUBLISHED_FROM", "Repo", "rid", False),
    ("edges_has_workflow", "Repo", "rid", "HAS_WORKFLOW", "Workflow", "wid", False),
    ("edges_publishes_via_oidc", "Workflow", "wid", "PUBLISHES_VIA_OIDC", "Package", "pid", False),
)


def batches(rows: Sequence[Any], size: int) -> Iterable[list[Any]]:
    for i in range(0, len(rows), size):
        yield list(rows[i : i + size])


def _missing_edge_endpoints(
    tables: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, set[str]]:
    known: dict[str, set[str]] = {label: set() for _, _, label in NODE_SPECS}
    extra: dict[str, set[str]] = {label: set() for _, _, label in NODE_SPECS}
    for table, id_field, label in NODE_SPECS:
        for row in tables.get(table) or []:
            value = row.get(id_field)
            if value:
                known[label].add(value)
    for table, src_label, src_field, _rel, dst_label, dst_field, _bt in EDGE_SPECS:
        for row in tables.get(table) or []:
            src = row.get(src_field)
            dst = row.get(dst_field)
            if src:
                extra[src_label].add(src)
            if dst:
                extra[dst_label].add(dst)
    return {label: extra[label] - known[label] for label in extra}


def _run(session: Any, query: str, rows: Sequence[Mapping[str, Any]]) -> None:
    result = session.run(query, rows=list(rows))
    consume = getattr(result, "consume", None)
    if consume is not None:
        consume()


def merge_version_nodes(session: Any, rows: Sequence[Mapping[str, Any]]) -> None:
    """Upsert nodes by `id`, then SET :Version. rows: [{id: ...}]."""
    _run(session, Q_MERGE_NODES, rows)


def create_inline(session: Any, rows: Sequence[Mapping[str, Any]]) -> None:
    """Unlabeled node pair + DEPENDS_ON per row. rows: [{src, dst}]."""
    _run(session, Q_INLINE, rows)


def create_edges(session: Any, rows: Sequence[Mapping[str, Any]]) -> None:
    """MATCH both :Version endpoints, CREATE DEPENDS_ON. rows: [{src, dst}]."""
    _run(session, Q_MATCH_CREATE, rows)


def create_bitemporal_edges(session: Any, rows: Sequence[Mapping[str, Any]]) -> None:
    """MATCH endpoints, CREATE bitemporal DEPENDS_ON. rows: [{src, dst, eid, vf, vt}]."""
    _run(session, Q_MATCH_CREATE_BITEMPORAL, rows)


def load_graph(
    session: Any,
    tables: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    batch_size: int = PRELIMINARY_BATCH_SIZE,
    checkpoint_path: Path | None = None,
) -> dict[str, int]:
    if batch_size > MAX_UNWIND_BATCH or batch_size < 1:
        raise ValueError(f"batch_size must be 1..{MAX_UNWIND_BATCH}")
    done: set[str] = set()
    if checkpoint_path is not None and checkpoint_path.is_file():
        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        done = set(payload.get("done") or [])

    def mark(key: str) -> None:
        done.add(key)
        if checkpoint_path is None:
            return
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text(
            json.dumps({"done": sorted(done)}, indent=2) + "\n",
            encoding="utf-8",
        )

    nodes = 0
    edges = 0
    for table, id_field, label in NODE_SPECS:
        rows = [
            {"id": hydra_id(row[id_field])}
            for row in tables.get(table) or []
            if row.get(id_field)
        ]
        query = q_merge_nodes(label)
        for i, chunk in enumerate(batches(rows, batch_size)):
            key = f"nodes:{label}:{i}"
            if key in done:
                nodes += len(chunk)
                continue
            print(f"load {key} n={len(chunk)}", file=sys.stderr, flush=True)
            _run(session, query, chunk)
            nodes += len(chunk)
            mark(key)
    extras = _missing_edge_endpoints(tables)
    for _table, _id_field, label in NODE_SPECS:
        missing = sorted(extras.get(label) or [])
        rows = [{"id": hydra_id(stable)} for stable in missing]
        query = q_merge_nodes(label)
        for i, chunk in enumerate(batches(rows, batch_size)):
            key = f"nodes:{label}:from_edges:{i}"
            if key in done:
                nodes += len(chunk)
                continue
            print(f"load {key} n={len(chunk)}", file=sys.stderr, flush=True)
            _run(session, query, chunk)
            nodes += len(chunk)
            mark(key)
    for table, src_label, src_field, rel, dst_label, dst_field, bitemporal in EDGE_SPECS:
        rows = []
        for row in tables.get(table) or []:
            src = row.get(src_field)
            dst = row.get(dst_field)
            if not src or not dst:
                continue
            item: dict[str, Any] = {
                "src": hydra_id(src),
                "dst": hydra_id(dst),
                "eid": hydra_id(f"{rel}:{src}->{dst}"),
            }
            if bitemporal:
                item["vf"] = int(row.get("valid_from") or 0)
                item["vt"] = int(row.get("valid_to") or SENTINEL_VALID_TO)
            rows.append(item)
        query = q_create_rel(src_label, rel, dst_label, bitemporal=bitemporal)
        for i, chunk in enumerate(batches(rows, batch_size)):
            key = f"edges:{rel}:{i}"
            if key in done:
                edges += len(chunk)
                continue
            print(f"load {key} n={len(chunk)}", file=sys.stderr, flush=True)
            _run(session, query, chunk)
            edges += len(chunk)
            mark(key)
    return {"nodes": nodes, "edges": edges, "batch_size": batch_size}


def read_graph_dir(graph_dir: Path) -> dict[str, list[dict[str, Any]]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    for filename in GRAPH_FILES:
        key = filename.removesuffix(".parquet")
        path = graph_dir / filename
        if path.is_file():
            tables[key] = pq.read_table(path).to_pylist()
        else:
            tables[key] = []
    return tables


def load_from_dir(
    session: Any,
    graph_dir: Path,
    *,
    batch_size: int = PRELIMINARY_BATCH_SIZE,
    checkpoint_path: Path | None = None,
) -> dict[str, int]:
    return load_graph(
        session,
        read_graph_dir(graph_dir),
        batch_size=batch_size,
        checkpoint_path=checkpoint_path,
    )
