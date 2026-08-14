"""Loader skeleton — UNWIND shapes from docs/MEASURED.md, no full load.

Batch size is 1000 (HydraDB 0.1.0 rejects UNWIND > 1024). Extra node
properties cannot ride in the CREATE/MERGE pattern — only `id`, then SET label.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from patient_zero.cypher import (
    MAX_UNWIND_BATCH,
    PRELIMINARY_BATCH_SIZE,
    Q_INLINE,
    Q_MATCH_CREATE,
    Q_MATCH_CREATE_BITEMPORAL,
    Q_MERGE_NODES,
)

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
    "merge_version_nodes",
]


def merge_version_nodes(session: Any, rows: Sequence[Mapping[str, Any]]) -> None:
    """Upsert nodes by `id`, then SET :Version. rows: [{id: ...}].

    Extra node properties cannot ride in the UNWIND pattern. Only :Version has
    been measured; other labels wait on schema freeze.
    """
    session.run(Q_MERGE_NODES, rows=list(rows))


def create_inline(session: Any, rows: Sequence[Mapping[str, Any]]) -> None:
    """Unlabeled node pair + DEPENDS_ON per row. rows: [{src, dst}]."""
    session.run(Q_INLINE, rows=list(rows))


def create_edges(session: Any, rows: Sequence[Mapping[str, Any]]) -> None:
    """MATCH both :Version endpoints, CREATE DEPENDS_ON. rows: [{src, dst}]."""
    session.run(Q_MATCH_CREATE, rows=list(rows))


def create_bitemporal_edges(session: Any, rows: Sequence[Mapping[str, Any]]) -> None:
    """MATCH endpoints, CREATE bitemporal DEPENDS_ON. rows: [{src, dst, eid, vf, vt}].

    Rel property map must lead with `id:` (row.eid).
    """
    session.run(Q_MATCH_CREATE_BITEMPORAL, rows=list(rows))
