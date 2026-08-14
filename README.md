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

> 🚧 **In development, Aug 14–20 2026.** Numbers below are filled in only once measured.
> Nothing in this README is an estimate presented as a result.

## Why trust edges

The May 11 2026 TanStack npm worm spread on stolen CI credentials, not dependency relationships:
a `pull_request_target` "Pwn Request" → GitHub Actions cache poisoning across the fork↔base trust
boundary → an OIDC token lifted from runner memory. That is why it crossed from npm to PyPI — a
jump that is impossible along dependency edges and trivial along maintainer edges.

## Results

Filled in on Day 4 (Aug 18), measured, including anything that underperformed.

| Metric | Trust topology | Dependency topology (control) |
|---|---|---|
| Forecast precision@10 / @50 / @100 | — | — |
| Recall@K | — | — |
| R₀ | — | — |
| Index case: rank of true origin | — | n/a |
| Alert triage collapse | — | |
| Graph size actually loaded | — | |

The dependency-topology column is a **negative control**: the identical query, one parameter
changed. The thesis predicts it scores near zero.

## HydraDB integration

Documented on Day 5 with the real queries and measured latencies. See
[`docs/MEASURED.md`](docs/MEASURED.md) for the throughput and traversal numbers this
architecture was designed around.

## Setup

Dry-run on a clean machine on Day 6, before submission.

## Documentation

- [`docs/DESIGN.md`](docs/DESIGN.md) — the design spec
- [`docs/HANDOFF.md`](docs/HANDOFF.md) — constraints, interface contracts, schedule
- [`docs/MEASURED.md`](docs/MEASURED.md) — measured HydraDB throughput and the slice budget
- [`ATTRIBUTION.md`](ATTRIBUTION.md) — third-party data sources and licenses

## License

[Apache-2.0](LICENSE).
