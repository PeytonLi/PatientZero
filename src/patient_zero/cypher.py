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
# is not in the accepted set.
Q_HEALTH = "MATCH (a:Version) RETURN count(*) AS c"

# HydraDB 0.1.0 admission control rejects UNWIND batches > 1024.
# 1000 is the largest round size that actually runs (measured D0-1).
MAX_UNWIND_BATCH = 1024
PRELIMINARY_BATCH_SIZE = 1000
