# Patient Zero

**A supply chain worm does not travel down dependency edges. It travels along trust edges.**

Patient Zero models both topologies in [HydraDB](https://github.com/hydra-db/hydradb) and runs one
graph primitive — bounded pathfinding via `algo.SSpaths` — in three directions of time:

| Direction | Question | Product |
|---|---|---|
| **Backward** over trust edges | Who did this? | **Index case** |
| **Forward** over trust edges | Who falls next? | **Forecast** |
| **Forward from nothing** | Who *could* fall? | **Leverage + min-cut** |

Plus **blast radius** over the dependency topology, walked backward and filtered bitemporally, and
**reachability** triage via install-hook analysis.

Built for [Hack Hydra](https://hackhydra.hydradb.com/), Track 2A — Supply Chain Blast Radius.

Numbers below are from one live run against the loaded graph
([`artifacts/evidence.json`](artifacts/evidence.json), `as_of` = 19:26 on 11 May 2026).
Nothing here is an estimate.

## Why trust edges

The May 11 2026 TanStack npm worm spread on stolen CI credentials, not dependency relationships:
a `pull_request_target` "Pwn Request" → GitHub Actions cache poisoning across the fork↔base trust
boundary → an OIDC token lifted from runner memory. That is why it crossed from npm to PyPI — a
jump that is impossible along dependency edges and trivial along maintainer edges.

## Results

Clock: 42 IOC **seed** pids at 19:26, scored against 138 **validation** pids. Forecast ranking is
`(1 / degree(shared entity)) × vector`, with `vector = 2` on a `pull_request_target` / OIDC
workflow path and `1` otherwise. Weights were frozen before this run. `split == validation` is
never an input to the score.

| Metric | Trust topology | Dependency topology (control) |
|---|---|---|
| Forecast precision@10 / @50 / @100 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 |
| Recall@100 | 0.0 | 0.0 |
| R₀ (mean validation pids reached per seed) | 0.0 | 0.0 |
| Index case: rank of true origin (`npm:tannerlinsley`) | not in top 5 | n/a |
| Alert triage collapse | — | |
| Graph size actually loaded | 14,910 nodes / 25,954 edges | same snapshot |

The dependency column is a **negative control**: the identical forecast, `relTypes` swapped.
It returned **0** paths. Trust returned **84** ranked packages; none of them are in the IOC
validation split under `maxLen=3`, `pathCount=100`. R₀ was defined as the mean, over the 42
seeds, of unique validation pids appearing as forecast candidates from that seed. The thesis
expected trust R₀ > 1 and the control near 0. The control matched. Trust R₀ did not.

What the trust walk *did* return, ranked by exclusivity:

1. `npm:gl-react-blurhash` and `npm:seroval` via co-maintainer `npm:schiller-manuel` (degree 15)
2. then `@tanstack/*` neighbours via `npm:tannerlinsley` (degree 256)

Index case (k=5), same exclusivity + vector: #1 is
`github:TanStack/router:.github/workflows/release.yml` (OIDC / `pull_request_target` workflow).
`tannerlinsley` is not in that list — a high-degree maintainer is down-ranked on purpose.

Leverage ranks T2 packages-at-risk, not August lockfile services.
`tannerlinsley` covers 82 forecast packages; `schiller-manuel` covers 2. Min-cut is **greedy
set cover** on seed→validation paths, not Edmonds-Karp. `reachable_validation = 0`, so
`mincut = []` and `spread_blocked_pct` stays JSON null.

Blast radius is empty at 19:26: there is no reverse-npm closure in this slice, and the 24
lockfile `PINS` use fetch-time `lockfile_at`, not the May 11 clock. Reachability has no install
hooks on unpublished IOC tarballs.

Full Cypher and paths: [`artifacts/evidence.json`](artifacts/evidence.json).
Load notes: [`artifacts/load_manifest.json`](artifacts/load_manifest.json).
Slice honesty: [`artifacts/graph_manifest.json`](artifacts/graph_manifest.json)
(IOC versions unpublished so `DEPENDS_ON` is the current default version;
`fallback_default=142`; no reverse npm dependents from deps.dev REST).

## HydraDB integration

HydraDB 0.1.0 nodes store `{id}` plus one label. Extra fields live in Parquet and are joined at
read time. Path records come back with **empty node properties**; identity is `element_id` (the
integer id as a string). `id` / `eid` must be non-negative integers — `hydra_id(stable)` is
blake2b truncated to 63 bits.

The README `sourceLabel` / `sourceProperty` / `sourceValues` map fails (`missing $sourceNode`).
`MATCH` then `CALL` is rejected by Bolt. The query that actually runs:

```cypher
CALL algo.SSpaths({
  sourceNode: $sourceNode,   // integer hydra_id
  relTypes: ['MAINTAINS', 'PUBLISHED_FROM', 'HAS_WORKFLOW', 'PUBLISHES_VIA_OIDC'],
  relDirection: 'both',
  maxLen: 3,
  pathCount: 100,
  resultLimit: 100
}) YIELD path
RETURN path
```

`pathCount` must be ≥ 1. `0` returns min-hop only and misses 2-hop co-maintainers.
T1 (dependency) uses `relTypes: ['DEPENDS_ON', 'PINS']`, `relDirection: 'incoming'`, and
filters `valid_from` / `valid_to` on the client after the procedure returns. T2 rels have no
`valid_from`; do not bitemporal-filter them.

Health is `verify_connectivity` only. Do not `count(*)` all Version nodes.
UNWIND batches cap at 1024; the loader uses 1000. Query timeout is 30s. One writer.

Throughput probes: [`docs/MEASURED.md`](docs/MEASURED.md).

## Setup

Needs Python 3.12+, Docker, and Bolt on `127.0.0.1:7687`.

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
pip install -e ".[test]"
```

HydraDB (Windows: drop `--user`; use an absolute volume path if bind-mount fails):

```bash
docker pull ghcr.io/hydra-db/hydradb:latest
mkdir -p hydradb-data/store hydradb-data/cache
printf '%s\n' 'local-development-token-32-bytes' > hydradb-data/auth-token
docker run --rm \
  -p 7687:7687 -p 8443:8443 -p 9090:9090 -v "$PWD/hydradb-data:/data" \
  -e CLOUD_PROVIDER=local -e LOCAL_PATH=/data/store \
  -e GRAPH_NAMESPACE=default -e GRAPH_ID=default \
  -e GRAPH_CELL_ID=cell-0 -e GRAPH_CELLS=cell-0 -e GRAPH_NODE_ID=node-0 \
  -e GRAPH_BOLT_NODE_ADDRESSES=node-0=127.0.0.1:7687 \
  -e GRAPH_ADVERTISED_BOLT_ADDR=127.0.0.1:7687 \
  -e GRAPH_DATA_CACHE_DIR=/data/cache -e GRAPH_AUTH_TOKEN_FILE=/data/auth-token \
  -e GRAPH_ALLOW_PLAINTEXT=true -e RUST_MIN_STACK=33554432 \
  ghcr.io/hydra-db/hydradb:latest
```

Graph (Parquet is gitignored under `data/graph/`):

```bash
python scripts/etl.py --offline          # after caches exist; omit --offline to fetch
python scripts/load.py                   # CREATE, not upsert
# Do not re-run load.py without wiping the graph and runs/load-checkpoint.json.
# A second pass duplicates edges.
python -m patient_zero                   # http://127.0.0.1:8080  (not :8000)
```

`file://` on `src/patient_zero/static/` still serves the mock. Live mode talks to `:8080`.

## Documentation

- [`docs/DESIGN.md`](docs/DESIGN.md) — the design spec
- [`docs/HANDOFF.md`](docs/HANDOFF.md) — constraints, interface contracts, schedule
- [`docs/MEASURED.md`](docs/MEASURED.md) — measured HydraDB throughput and the slice budget
- [`ATTRIBUTION.md`](ATTRIBUTION.md) — third-party data sources and licenses

## License

[Apache-2.0](LICENSE).
