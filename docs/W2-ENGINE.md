# W2 — Engine / Queries

**Read [`HANDOFF.md`](./HANDOFF.md) §2 (constraints) and §4 (interface contracts) first.**
Design detail: [`DESIGN.md`](./DESIGN.md) §4, §5.

**You own:** the graph schema, the loader, Leg 1 (blast radius), Leg 2 (blast forecast), and the
HTTP API.
**You are blocked by:** W1's D0-1 number (schema freeze), W1's Parquet (load), W3's IOC set
(forecast validation).
**You block:** W4 — so **ship stub endpoints on Day 1**, before any logic exists.

---

## Day 1, hour 1: unblock W4 before anything else

W4 cannot build the demo against nothing. Before you write a line of Cypher, ship a FastAPI app on
`localhost:8000` with all four endpoints from [`HANDOFF.md`](./HANDOFF.md) §4 returning
correctly-shaped **fake** data. Then W4 runs at full speed all week and the swap to real data is a
non-event.

This is 30 minutes of work that buys you a parallel workstream. Do it first.

---

## Schema

Full node/edge model: [`DESIGN.md`](./DESIGN.md) §4. Three topologies over shared nodes:

- **T1 Dependency** (Leg 1, backward): `DEPENDS_ON`, `PINS`, `AFFECTS`
- **T2 Trust** (Leg 2, forward): `MAINTAINS`, `PUBLISHED_FROM`, `HAS_WORKFLOW`,
  `PUBLISHES_VIA_OIDC`, `SHARES_EMAIL_DOMAIN`
- **T3 Execution** (Leg 3, forward — W3 owns the logic): `IMPORTS`, `CALLS`, `HAS_ENTRY`

**Freeze the schema only after W1 delivers `MEASURED.md`.** The element budget determines what you
can afford to model.

### Bitemporality

Every T1 edge carries `valid_from` / `valid_to` (epoch seconds, int, sentinel `4102444800` for
open-ended). Queries take `as_of` and filter `valid_from <= $as_of < valid_to`.

This is what makes *"which applications resolved the compromised version **while it was live**"*
answerable, and it is the part most teams will skip. It is a differentiator — protect it.

**Risk #6:** there is no documented `CREATE INDEX`, so this is an unindexed property predicate on
every traversed edge. W1's D0-1 measures whether it is usably fast.
**Fallback if not:** partition into per-day graph namespaces and pin the snapshot at query time.
Closer to HydraDB's grain, more moving parts. Decide on measurement, not preference.

### Supernode strategy — do not skip this

`lodash`-class packages have millions of dependents. HydraDB's own benchmark tops out at fanout
10,000 for a reason: 20 hops at that fanout is 10.9s. Unbounded traversal will hang the demo.

1. **Every** traversal passes explicit `maxLen` and `resultLimit`. No exceptions.
2. Cap in-degree at ingest; overflow dependents route through a `:BulkDependents` summary node.
3. Precompute closures for the top-N fan-in packages into a materialized edge.

Designing around their published supernode ceiling is itself a scoring moment under "use of
HydraDB." Say so in the README.

---

## The loader

Dumb by design. W1 hands you pre-resolved, pre-keyed, deduplicated Parquet — you `UNWIND` it.

- **Single-threaded. One writer.** Concurrency measurably does not help (conc=32 → same 224
  ops/sec, p50 141s). Do not "optimize" this.
- Batch size from `MEASURED.md`.
- **Idempotent and resumable.** You get roughly one 90-minute load attempt per iteration and you
  will not get the schema right the first time. Checkpoint progress; a crash at 80% must not
  restart from zero.
- Nodes first, then edges (`MATCH` both endpoints, then `CREATE` the relationship).
- Log throughput continuously so you know at minute 5 whether the load will finish.

---

## Leg 1 — Bitemporal blast radius (Day 2)

**Input:** `(ecosystem, package, version, window_start, window_end, max_hops)`
**Method:** reverse traversal over `DEPENDS_ON`/`PINS` from the compromised `Version`, edges
filtered to the compromise window, bounded depth, terminating at `Service`.

```cypher
CALL algo.SSpaths({
  sourceLabel: 'Version', sourceProperty: 'vid', sourceValues: $compromised,
  relTypes: ['DEPENDS_ON','PINS'], relDirection: 'incoming',
  maxLen: $maxHops, resultLimit: $limit
}) YIELD path
WHERE all(r IN relationships(path) WHERE r.valid_from <= $as_of < r.valid_to)
RETURN path
```

Use the **native** `algo.SSpaths` rather than client-side fan-out. That is the graph-native
scoring moment and the brief calls it out explicitly.

**Must answer all six questions from the track brief:**
1. Which internal services are transitively exposed?
2. Which version of the dependency introduced the vulnerability?
3. Which applications resolved the compromised version **while it was live**?
4. Which other packages share maintainers or infrastructure with it? *(spans into T2)*
5. Are there likely typosquat packages nearby?
6. What is the complete blast radius?

**Typosquats (Q5) — do it graph-native, not with Levenshtein.** Everyone else will use string
distance. A typosquat is a name-similar node in an **anomalous graph position**: brand-new
maintainer, zero reverse deps, dependency set copied wholesale from its target, published right
after the target's popularity spike. Name similarity is the *filter*; graph position is the
*signal*.

---

## Leg 2 — Blast forecast (Day 3–4) ← the trophy

**Input:** seed set (the 42 packages known at 19:26) + `as_of` + `k`.
**Method:** propagation scoring over **T2, not T1**. A package scores high when it shares a
maintainer, repo, publishing workflow, or OIDC trust path with an already-compromised package.

Weighting that matters:
- **Exclusivity** — a maintainer with 3 packages is a far stronger signal than one with 400.
  Inverse-frequency weight the shared-entity edges, or the result is just a popularity ranking.
- **Vector match** — workflows carrying the `pull_request_target` pattern that was the actual
  breach vector score higher. This is the detail that makes the forecast *about this attack* rather
  than generic co-occurrence.
- **Cross-ecosystem** — a maintainer publishing to both npm and PyPI is exactly how the worm
  crossed. Do not filter these out; they are the thesis.

**Output:** ranked packages, each with the **justifying trust path**. The path is not optional —
an unexplained ranking is not a product, and the path is what makes the demo legible.

**Cost:** near zero LLM. This is graph structure over registry metadata. Budget is not a constraint here.

### Validation — required by end of Day 4

Seed with only the 42 packages known at 19:26. Score the ranked output against W3's reconciled
`data/truth/ioc.parquet` (the 170+ confirmed later that day).

Report **precision@10 / @50 / @100 and recall@K**, plus the t+6min vs t+26min detection-baseline
comparison.

**If the forecast has no signal, say so.** Report the negative result with the numbers. A measured
miss scores better under "quality of results" than an unmeasured demo, and Legs 1+3 still carry
the submission. Do not tune against the validation set until it looks good — that is the one way
to actually lose this track.

---

## Definition of done

- [ ] Stub API live on `localhost:8000`, all 4 endpoints, correct shapes (**Day 1, hour 1**)
- [ ] Schema frozen against `MEASURED.md` (**Day 1**)
- [ ] Idempotent resumable loader written (**Day 1**)
- [ ] First full load completed and timed (**Day 2**)
- [ ] Leg 1 answers all six brief questions on real data (**Day 2**)
- [ ] T2 trust topology built (**Day 3**)
- [ ] Leg 2 produces ranked predictions with justifying paths (**Day 3**)
- [ ] **Validation numbers exist** (**Day 4** — hard gate, one day of slack remains)
- [ ] All endpoints serving real data (**Day 4**)

## Traps

- Building the loader before `MEASURED.md` exists.
- Parallelizing writers.
- Any unbounded traversal. One missing `maxLen` hangs the demo in front of judges.
- Client-side fan-out instead of `algo.SSpaths` — throws away the graph-native score.
- Levenshtein typosquat detection.
- Forecasting over the dependency topology. **The worm did not spread that way.** T2, not T1.
- Tuning the forecast against the validation set.
- Leaving W4 without stub endpoints.

## Suggested skills

`superpowers:test-driven-development` (traversal correctness is not eyeballable) ·
`superpowers:systematic-debugging` (the loader will stall) ·
`context7-mcp` (`neo4j` driver API — do not guess) ·
`superpowers:verification-before-completion`
