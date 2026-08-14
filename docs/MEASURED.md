# Patient Zero — Measured HydraDB throughput (D0-1)

Measured 2026-08-14 on the machine that will run the real load. Every number is
wall-clock from `scripts/spike_throughput.py` / `scripts/probe_set_props.py`.
Nothing here is inferred from the vendor benchmark.

**Status:** complete enough to freeze the loader shape. 100k×3 batch-size sweep
was aborted after admission control rejected batch 10,000. 20k rows at the
legal batch sizes is the number we size against.

## Environment

| | |
|---|---|
| OS | Windows 11 (10.0.26200), PowerShell |
| HydraDB | 0.1.0 (`ghcr.io/hydra-db/hydradb:latest`, container `hydradb`) |
| Driver | neo4j 6.2.0 (Python 3.13.11) |
| Connection | `bolt://127.0.0.1:7687`, `neo4j.basic_auth("neo4j", token)` |
| Writers | one session / one writer for all main tests |
| Query timeout | **30,000 ms hard cap** (`client_query_runtime`) |
| UNWIND cap | **1,024 rows** (`client_query_batch_items`) |

## Hard limits discovered (load-bearing for W2)

1. **UNWIND batch > 1024 is rejected.**
   `client_query_batch_items rejected by admission control: actual 10000 exceeds limit 1024`
   **Winning batch size = 1000.** Do not try 10k. `MAX_UNWIND_BATCH = 1024`.
2. **Queries that run longer than 30s are killed.** The unbounded 3-hop
   bitemporal `count(*)` hit this. Every demo query must pass `maxLen` +
   `resultLimit` into `algo.SSpaths`. A global `MATCH` scan is not a product query.
3. **UNWIND node patterns only permit `id`.** Labels attach with exactly one
   `SET a:Label`, never inline. Extra node properties **cannot** be bulk-set
   (see SET probes below). Encode identity in `id` (already the vid/pid/mid/rid
   plan) and keep the rest in Parquet, joined at the API.
4. **Relationship properties are allowed** on MATCH-then-CREATE **if the map
   starts with `id:`**. That is how bitemporal `valid_from` / `valid_to` lands.

## Supported Cypher subset

```cypher
-- Inline: 2 unlabeled nodes + 1 rel per row. `id` is the ONLY node property.
UNWIND $rows AS row CREATE (a {id: row.src})-[:DEPENDS_ON]->(b {id: row.dst})

-- Node upsert. One label via SET. No extra properties in this statement.
UNWIND $rows AS row MERGE (a {id: row.id}) SET a:Version

-- Realistic loader: endpoints already exist, exactly one label, matched by id.
UNWIND $rows AS row
MATCH (a:Version {id: row.src}), (b:Version {id: row.dst})
CREATE (a)-[:DEPENDS_ON]->(b)

-- Bitemporal rel properties. Property map MUST lead with `id:`.
UNWIND $rows AS row
MATCH (a:Version {id: row.src}), (b:Version {id: row.dst})
CREATE (a)-[:DEPENDS_ON {id: row.eid, valid_from: row.vf, valid_to: row.vt}]->(b)

-- Per-node property SET (NOT a bulk path — ~1s each, see probes).
MATCH (a:Version {id: $id}) SET a.name = $name
```

`MERGE (a {id}) SET a:Version` **does work** as a node upsert. DESIGN.md said
MERGE was undocumented; on 0.1.0 it is the node loader.

### Rejected (do not use)

- `UNWIND … MATCH … SET a.prop = …` — “UNWIND MATCH must end in RETURN or DELETE”
- `UNWIND … MERGE … SET a:Label SET a.prop = …` — “vertex upsert requires MERGE by id followed by SET” (one SET, the label)
- Inline labels in UNWIND CREATE (`CREATE (a:Version {id: …})`)
- UNWIND batches > 1024
- Bare `RETURN 1`
- 10k-row UNWIND

`algo.SSpaths` was **not** exercised in D0-1. First use is Leg 1. Bound it.

## Table: mode × batch_size (20k rows, post-restart DB still holding earlier probe nodes)

Elements/row: inline = 3; match_create / bitemporal = 1 (nodes preloaded, timed separately).

| mode | batch_size | rows | seconds | edges/sec | elements/sec | notes |
|---|---:|---:|---:|---:|---:|---|
| inline | 100 | 20_000 | 212.25 | **94.2** | 282.7 | too chatty |
| match_create | 100 | 20_000 | 149.945 | **133.4** | 133.4 | preload 14.231s / 2000 nodes |
| inline | 1000 | 20_000 | 19.494 | **1026.0** | 3077.9 | |
| match_create | 1000 | 20_000 | 16.005 | **1249.6** | 1249.6 | preload 1.208s / 2000 nodes |
| bitemporal_load | 1000 | 20_000 | 13.985 | **1430.1** | 1430.1 | rel props `{id, valid_from, valid_to}` |
| inline | 10000 | 20_000 | — | **rejected** | — | admission control, limit 1024 |

5k-row probe at batch 1000 earlier printed ~5–7k edges/sec. That number is a
**startup artifact**. 20k is the one we believe. Do not freeze a slice on the 5k figure.

## Winning loader shape

**MATCH existing `:Label {id}` endpoints, CREATE the rel, UNWIND batch = 1000.**

Bitemporal rel properties do not slow the write (1430 edges/sec vs 1250 without).
Use that shape for T1.

Node preload (`MERGE {id} SET :Label`) at batch 1000: ~1,650 nodes/sec
(2000 nodes in 1.2s). Budget nodes and edges separately.

## Slice budget (90-minute single-threaded)

Using match_create @ 1000 @ 20k: **1,250 edges/sec**.

- 90 min = 5400 s × 1250 ≈ **6.75 million relationship creates**
- Node upserts at ~1,650/sec → **~8.9 million nodes** in 90 min
- Combined 1–2M element design target fits in **~15–25 minutes**, with slack

Vendor inference of ~225 edges/sec → 1M edges in ~74 min is **pessimistic on
this machine at batch 1000**, and **optimistic at batch 100**. Batch size is
the whole game, and 1024 is the ceiling.

Honesty headline: whatever W1 actually loads, not “14M nodes.”

## Bitemporal 3-hop predicate — Risk #6 CONFIRMED

After loading 20k bitemporal edges onto a graph that already had ~47k `:Version`
nodes from earlier probes:

```
MATCH 3-hop DEPENDS_ON with valid_from/valid_to predicates, RETURN count(*)
→ killed at 30,000 ms (client_query_runtime)
```

Unindexed property predicates over an unbounded MATCH are **not** a demo query.
Fallback, in order:

1. **Always** `algo.SSpaths` from a concrete source with `maxLen` + `resultLimit`.
2. If even that is slow: per-day graph namespaces (DESIGN.md risk #6).
3. Do not ship a full-graph 3-hop count.

Reads of a **point lookup** (`MATCH (a:Version {id:$id}) RETURN a.name`) are
2.5 ms. The timeout is the scan, not Bolt.

## SET extra node properties

| probe | ok? | seconds | meaning |
|---|---|---:|---|
| `UNWIND MERGE {id} SET a:Version` | yes | 0.45 | node loader |
| `UNWIND MATCH SET a.name` | **no** | — | UNWIND MATCH must RETURN/DELETE |
| `UNWIND MERGE SET a:Package SET a.name` | **no** | — | only one SET, the label |
| `MATCH (a:Version {id:$id}) SET a.name` | yes | **1.09** | works, ~1 node/sec, unusable in bulk |
| read-back `a.name` | yes | 0.003 | the one-node SET actually stuck |

**W2 schema consequence:** HydraDB nodes are `{id: <stable id>}` plus one label.
Put bitemporality and range/lockfile metadata on **relationships**. Join
packument fields (install hooks, maintainers) from Parquet at the API.
`algo.SSpaths` `sourceProperty` is `id`, not `vid`.

## deps.dev REST (same day, not a write measurement)

`scripts/depsdev.py` against `@tanstack/query-core@5.101.4`:

- Forward graph: 1 node (SELF), 0 edges — a leaf. `@tanstack/react-query` is
  2 nodes / 1 DIRECT edge.
- `GET …/versions/{v}:dependents` (v3alpha) returns **counts only**:
  5789 total / 170 direct / 5650 indirect. **No listing of who they are.**
- Reverse-dependency **closure for Leg 1 cannot be built from REST.**
  Options: BigQuery public dataset (`https://docs.deps.dev/bigquery/v1/`),
  or shrink Leg 1 to real lockfile `PINS` + the 180-package IOC set + the
  trust neighborhood already in packuments.

## What this freezes

| Decision | Choice |
|---|---|
| Writer | one, single-threaded |
| UNWIND batch | **1000** (cap 1024) |
| Node load | `UNWIND MERGE (a {id}) SET a:Label` |
| Edge load | `UNWIND MATCH both ends CREATE rel` with `{id, …}` leading the map |
| Node properties in HydraDB | **`id` only** |
| Extra attributes | Parquet / DuckDB, joined at read time |
| Traversals | bounded `algo.SSpaths` only; 30s query timeout |
| Slice | 1–2M elements is comfortably inside a 90-minute load |
| Reverse npm closure | not via REST; lockfiles + IOC + trust neighborhood first |
