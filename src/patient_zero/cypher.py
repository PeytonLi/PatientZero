"""Accepted HydraDB 0.1.0 Cypher shapes — from docs/MEASURED.md.

Do not rewrite these into idiomatic Neo4j. UNWIND node patterns only permit
`id`. Labels attach via exactly one SET. Rel property maps MUST lead with `id:`.
UNWIND batches > 1024 are rejected. Queries > 30s are killed.
"""

from __future__ import annotations

# --- writes that execute (MEASURED.md "Supported Cypher subset") --------------

# Inline: 2 unlabeled nodes + 1 rel per row. `id` is the ONLY node property
# permitted in an UNWIND CREATE.
Q_INLINE = "UNWIND $rows AS row CREATE (a {id: row.src})-[:DEPENDS_ON]->(b {id: row.dst})"

# Node upsert. A label can only be attached via SET, never inline in the pattern.
Q_MERGE_NODES = "UNWIND $rows AS row MERGE (a {id: row.id}) SET a:Version"

# Realistic loader: both endpoints must already exist AND carry exactly one
# label, matched by `id`.
Q_MATCH_CREATE = (
    "UNWIND $rows AS row "
    "MATCH (a:Version {id: row.src}), (b:Version {id: row.dst}) "
    "CREATE (a)-[:DEPENDS_ON]->(b)"
)

# Same, with bitemporal rel properties. The property map MUST lead with `id:`.
Q_MATCH_CREATE_BITEMPORAL = (
    "UNWIND $rows AS row "
    "MATCH (a:Version {id: row.src}), (b:Version {id: row.dst}) "
    "CREATE (a)-[:DEPENDS_ON {id: row.eid, valid_from: row.vf, valid_to: row.vt}]->(b)"
)

# --- reads that execute -------------------------------------------------------

Q_TRAVERSE_3HOP = (
    "MATCH (a:Version)-[r1:DEPENDS_ON]->(b:Version)"
    "-[r2:DEPENDS_ON]->(c:Version)-[r3:DEPENDS_ON]->(d:Version) "
    "WHERE r1.valid_from <= $as_of AND $as_of < r1.valid_to "
    "AND r2.valid_from <= $as_of AND $as_of < r2.valid_to "
    "AND r3.valid_from <= $as_of AND $as_of < r3.valid_to "
    "RETURN count(*) AS c"
)

# Health / connectivity. MEASURED.md: row execution supports MATCH ... RETURN;
# RETURN currently supports <binding>.<property> or count(*). Bare `RETURN 1`
# is not in the accepted set. Do not use the Version count(*) scan as a
# liveness check — it grows with the graph. Point-lookup the demo sentinel.
Q_HEALTH = "MATCH (a:Version) RETURN count(*) AS c"
Q_PACKAGE_EXISTS = "MATCH (a:Package {id: $id}) RETURN a.id AS id"

# HydraDB 0.1.0 admission control rejects UNWIND batches > 1024.
# 1000 is the largest round size that actually runs (measured D0-1).
MAX_UNWIND_BATCH = 1024
PRELIMINARY_BATCH_SIZE = 1000

NODE_LABELS = frozenset({
    "Package", "Version", "Maintainer", "Repo", "Workflow", "Service", "Advisory",
})
REL_TYPES = frozenset({
    "DEPENDS_ON", "PINS", "AFFECTS", "MAINTAINS", "PUBLISHED_FROM",
    "HAS_WORKFLOW", "PUBLISHES_VIA_OIDC",
})


def q_merge_nodes(label: str) -> str:
    if label not in NODE_LABELS:
        raise ValueError(f"unsupported node label: {label}")
    return f"UNWIND $rows AS row MERGE (a {{id: row.id}}) SET a:{label}"


# HydraDB 0.1.0 SSpaths (measured): MATCH+CALL is rejected by Bolt transport;
# README sourceLabel/sourceProperty maps fail with "missing $sourceNode".
# Integer $sourceNode is the hydra_id. pathCount: 0 returns only min-hop
# shortest paths; use pathCount == resultLimit to reach 2-hop co-maintainers.
T1_RELS = ("DEPENDS_ON", "PINS")
T2_RELS = ("MAINTAINS", "PUBLISHED_FROM", "HAS_WORKFLOW", "PUBLISHES_VIA_OIDC")


def ss_paths(
    *,
    rel_types: list[str] | tuple[str, ...],
    direction: str,
    max_len: int,
    path_count: int,
    result_limit: int,
) -> str:
    if path_count < 1:
        raise ValueError("pathCount 0 only returns min-hop shortest paths; pass path_count >= 1")
    if max_len < 1:
        raise ValueError("maxLen must be >= 1")
    types = ", ".join(f"'{rel}'" for rel in rel_types)
    return (
        "CALL algo.SSpaths({\n"
        "  sourceNode: $sourceNode,\n"
        f"  relTypes: [{types}],\n"
        f"  relDirection: '{direction}',\n"
        f"  maxLen: {max_len},\n"
        f"  pathCount: {path_count},\n"
        f"  resultLimit: {result_limit}\n"
        "}) YIELD path\n"
        "RETURN path"
    )


def q_create_rel(src_label: str, rel: str, dst_label: str, *, bitemporal: bool = False) -> str:
    if src_label not in NODE_LABELS or dst_label not in NODE_LABELS:
        raise ValueError("unsupported endpoint label")
    if rel not in REL_TYPES:
        raise ValueError(f"unsupported rel type: {rel}")
    match = (
        f"UNWIND $rows AS row "
        f"MATCH (a:{src_label} {{id: row.src}}), (b:{dst_label} {{id: row.dst}}) "
    )
    if bitemporal:
        create = f"CREATE (a)-[:{rel} {{id: row.eid, valid_from: row.vf, valid_to: row.vt}}]->(b)"
    else:
        create = f"CREATE (a)-[:{rel} {{id: row.eid}}]->(b)"
    return match + create
