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
filters `valid_from` / `valid_to` on the client after the procedure returns. T2 rels
carry the same columns (stamped `0 → 2100` until we have real tenure) and the
forecast filters them the same way.

Health is `verify_connectivity` only. Do not `count(*)` all Version nodes.
UNWIND batches cap at 1024; the loader uses 1000. Query timeout is 30s. One writer.

Throughput probes: [`docs/MEASURED.md`](docs/MEASURED.md).

## Try it

**Live demo:** [https://patient-zero-me3t.onrender.com](https://patient-zero-me3t.onrender.com)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/PeytonLi/PatientZero)

That runs HydraDB and the API in one Standard instance (2 GB, ~$25/mo) with a
5 GB disk. First boot loads ~41k elements (1–2 min, masthead may read DEGRADED).
Later boots skip the load. Starter (512 MB) is too small for HydraDB + Python.

### Local Docker

```bash
docker compose up --build
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080). The masthead should read **LIVE** with a node count, not MOCK or DEGRADED. Press **Play 19:20 → 19:46** (or space) to walk the May 11 clock.

If port 7687 is already taken by a local HydraDB container, stop that one first. To wipe the graph and reload: `docker compose down -v && docker compose up --build`.

### Local Python (HydraDB still in Docker)

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
pip install -e ".[test]"
docker compose up hydradb -d
python scripts/load.py          # no-ops if the sentinel package is already present
python -m patient_zero          # http://127.0.0.1:8080
```

Serve from that URL. Opening `src/patient_zero/static/index.html` via `file://` falls back to mock data.

## Why trust edges

## Documentation

- [`docs/ROADMAP.md`](docs/ROADMAP.md) — product bets after the hackathon
- [`docs/DESIGN.md`](docs/DESIGN.md) — the design spec
- [`docs/HANDOFF.md`](docs/HANDOFF.md) — constraints, interface contracts, schedule
- [`docs/MEASURED.md`](docs/MEASURED.md) — measured HydraDB throughput and the slice budget
- [`ATTRIBUTION.md`](ATTRIBUTION.md) — third-party data sources and licenses

## License

[Apache-2.0](LICENSE).
