"""Turn a deps.dev Dependencies JSON document into DEPENDS_ON rows."""

from __future__ import annotations

from typing import Any

from patient_zero.assemble import SENTINEL_VALID_TO
from patient_zero.ids import vid


def _eco(system: str) -> str:
    return system.lower() if system else "npm"


def _node_vid(node: dict[str, Any]) -> str:
    key = node.get("versionKey") or {}
    return vid(_eco(key.get("system") or "npm"), key["name"], key["version"])


def depends_on_edges(
    graph: dict[str, Any],
    published_at: int | None,
) -> list[dict[str, Any]]:
    nodes = graph.get("nodes") or []
    valid_from = int(published_at) if published_at else 0
    rows = []
    for edge in graph.get("edges") or []:
        src = nodes[edge["fromNode"]]
        dst = nodes[edge["toNode"]]
        dst_key = dst.get("versionKey") or {}
        rows.append(
            {
                "src_vid": _node_vid(src),
                "dst_vid": _node_vid(dst),
                "range": edge.get("requirement") or "",
                "resolved_version": dst_key.get("version") or "",
                "valid_from": valid_from,
                "valid_to": SENTINEL_VALID_TO,
            }
        )
    rows.sort(key=lambda r: (r["src_vid"], r["dst_vid"]))
    return rows
