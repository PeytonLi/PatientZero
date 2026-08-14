# Patient Zero — Design Spec (v2)

**Hackathon:** Hack Hydra (Aug 12–20, 2026) · **Track:** 2A, Supply Chain Blast Radius
**Date:** 2026-08-14 · **Budget:** $50–300 · **Deadline:** Aug 20, 11:59 PM PT

> **v2 changes from the original design:** the three "legs" are reframed as one primitive run in
> three directions of time; **Leg 0 (index-case tracing)** is added; a **negative control** and
> **R₀ per topology** are added as the evidence layer; **prophylactic leverage + min-cut** is added
> as the actionable output; **Leg 3 is cut to Tier 1 only** to pay for all of it.

---

## 1. Thesis

> **A supply chain worm does not travel down dependency edges. It travels along trust edges —
> maintainer accounts, publishing workflows, OIDC grants.**
> These are two different graph topologies over the same nodes. Every existing tool walks only
> the first, which is why every existing tool can only tell you what already happened.

The May 11 2026 TanStack worm is the proof. The attacker never exploited a dependency
relationship to spread. They used a `pull_request_target` "Pwn Request" plus GitHub Actions cache
poisoning across the fork↔base trust boundary, extracted an OIDC token from runner memory, and
published with stolen credentials. That is why the worm crossed from npm to PyPI — a jump that is
**impossible** along dependency edges and **trivial** along maintainer edges.

### The reframe: one primitive, three directions of time

The original design listed three "legs" as if they were three features. They are not. They are one
graph primitive — **bounded pathfinding over the trust topology, `algo.SSpaths` with an explicit
`maxLen` and `resultLimit`** — pointed in three different directions of time.

| Direction | Question | Product | Ground truth to score against |
|---|---|---|---|
| **Backward** from observed compromise | *Who did this?* | **Index case** (Leg 0) | TanStack's published postmortem names the vector |
| **Forward** from observed compromise | *Who falls next?* | **Forecast** (Leg 2) | the 170+ reconciled IOC set |
| **Forward from nothing** | *Who could fall?* | **Leverage + min-cut** (Leg 4) | live, checkable prediction |

Two supporting queries complete the product, and neither needs the trust topology:

- **Blast radius** (Leg 1) — the same bounded pathfinding over the *dependency* topology, walked
  backward, filtered bitemporally. This is table stakes, done properly.
- **Reachability** (Leg 3) — a property predicate, not a traversal. See §6.

That is the whole system. One traversal primitive, two topologies, five products. It is a thesis
rather than a feature list, and it is why the parts reinforce each other instead of competing for
the six days.

---

## 2. Ground truth

The TanStack compromise is publicly documented with timestamps, giving a real train/validate split:

| Time (UTC, May 11 2026) | Event |
|---|---|
| 19:20–19:26 | 84 malicious versions across **42 `@tanstack/*` packages** |
| ~19:46 | First public detection (external researcher, StepSecurity) |
| End of day | **170+ packages, 400+ malicious versions**, across npm *and* PyPI |

**Validation protocol:** seed the forecast with only the 42 packages known at 19:26. Score its
ranked output against the 170+ confirmed later that day. Headline metric: **precision@K and
recall@K at t+6min, against a detection baseline of t+26min.**

If the forecast works, the claim is: *"The world learned about this at 19:46. We would have named
the next victims at 19:26."* If it does not work, we report the negative result honestly — and
this is precisely why **Leg 0 exists** (§5): it is validated against a *different, already-published*
answer, so a null result in Leg 2 does not leave the submission without a measured claim.

**Risk:** IOC lists live in vendor blogs (Aikido, Wiz, Snyk, Orca, Rescana, the TanStack
postmortem), not in one machine-readable file. Assembling and reconciling them is a real task with
a real chance of disagreement between sources. Union-of-sources with per-package provenance, and
we publish our reconciled list as a repo artifact.

---

## 3. Hard constraints (measured, not assumed)

From HydraDB's own published benchmarks (15-core Apple Silicon, MinIO in Docker):

| Metric | Value | Consequence |
|---|---|---|
| Write throughput | **~225 ops/sec**, flat | Graph must target **1–2M elements** (3M hard ceiling), **not** 50M |
| Write concurrency | conc=32 → still ~224 ops/sec, p50 **141s** | Do **not** parallelize writers. One loader. |
| Read throughput | 14,554 QPS @ conc=32 | Query freely. Reads are not the constraint. |
| Traversal @ fanout 10k | 1 hop 824ms · 10 hops 5.5s · 20 hops 10.9s | Supernodes are the query risk. Bound every traversal. |
| Bulk loader | **Does not exist** | Only Bolt / HTTP NDJSON, via batched `UNWIND` |
| `CREATE INDEX` | Not documented | — |
| Atomic `MERGE` | Not documented as upsert | **All dedup happens offline. Load pre-resolved, immutable data.** |

**Architecture forced by the above, and fortunately the right one anyway:** resolve and deduplicate
everything in DuckDB/Parquet locally → **one** single-threaded idempotent load into HydraDB → put
all the cleverness in read-time traversals. This mirrors HydraDB's own immutable-snapshot-over-
object-storage design, which is worth stating explicitly to the judges.

**The write ceiling is also why the v2 reframe is affordable.** Leg 0, the negative control, R₀,
and the leverage index are all *read-time* work over a graph we were already loading. They cost
zero write budget. The only thing v2 removes is Leg 3 Tiers 2–3, which cost build days.

### ⚠️ Day-0 gate: the meaning of "op" — being measured now

`ops=227.5/sec` at `p50=4,398ms` implies **~1,000 operations land per commit**. If one batched
`UNWIND` of 1,000 rows commits in ~4.4s, effective throughput is **~225 edges/sec → 1M edges in
~74 min**, which is workable. If an "op" is one *row*, throughput collapses and the slice must
shrink by an order of magnitude.

**This is an inference from their benchmark, not a documented fact.** Task D0-1 measures it. The
result lands in [`MEASURED.md`](./MEASURED.md) and **nobody freezes a schema until it exists.**

---

## 4. Graph model

One graph, two load-bearing topologies over shared nodes. (The original design's third
"execution topology" is cut to a property predicate — see §6.)

### Nodes
```
Package    {ecosystem, name}
Version    {ecosystem, name, version, published_at, unpublished_at, has_install_script, install_hooks}
Maintainer {ecosystem, login, email_domain, twofa}
Repo       {host, org, name}
Workflow   {repo, path, trigger, uses_pull_request_target, has_oidc_publish}
Service    {name}                      -- real OSS applications, via their real lockfiles
Advisory   {id, source, severity}
```

### T1 — Dependency (blast radius; walked backward)
```
(Version)-[:DEPENDS_ON {range, resolved_version, valid_from, valid_to}]->(Version)
(Service)-[:PINS       {lockfile_at, valid_from, valid_to}]->(Version)
(Advisory)-[:AFFECTS]->(Version)
```

### T2 — Trust (index case, forecast, leverage; walked in all three directions)
```
(Maintainer)-[:MAINTAINS]->(Package)
(Package)-[:PUBLISHED_FROM]->(Repo)
(Repo)-[:HAS_WORKFLOW]->(Workflow)
(Workflow)-[:PUBLISHES_VIA_OIDC]->(Package)
(Maintainer)-[:SHARES_EMAIL_DOMAIN]->(Maintainer)
```

T2 is small. That is the point — it is registry metadata, not a dependency closure, so the entire
trust neighborhood of the slice costs a rounding error of the write budget while carrying three of
the five products.

### Bitemporality
Every T1 edge carries `valid_from` / `valid_to` as epoch integers — the window during which that
resolution was actually true. Queries take an `as_of` parameter and filter
`valid_from <= $as_of < valid_to`. `valid_to` for a still-valid edge is the sentinel `4102444800`
(2100-01-01), never null.

This is what makes *"which applications resolved the compromised version **while it was live**"*
answerable, and it is the part most teams will skip. It is also what makes the **scrubbable clock**
in §7 possible, which is the demo's whole interaction model.

Property-predicate filtering with no index is a performance unknown. **Fallback if too slow:**
partition into per-day graph namespaces and pin the snapshot at query time. D0-1 decides this on
measurement, not preference.

### Supernode strategy
`lodash`-class packages have millions of dependents and will blow up any unbounded traversal
(their own benchmark tops out at fanout 10,000 for a reason). In order:
1. **Every** traversal passes explicit `maxLen` + `resultLimit` to `algo.SSpaths`. No exceptions.
2. Cap in-degree at ingest; overflow dependents route through a `:BulkDependents` summary node.
3. Precompute closures for the top-N fan-in packages into a materialized edge.

Reading their benchmark and designing around their published supernode ceiling is itself a scoring
moment under "use of HydraDB." Say so in the README.

---

## 5. The five products

### Leg 1 — Bitemporal blast radius (T1, backward)
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
**Output:** exposed services, the exact dependency path, and the timestamp each became exposed.
**Answers from the brief:** transitively exposed services · which version introduced it · who
resolved the bad version while it was live · complete blast radius.

**Typosquats (brief Q5) — graph-native, not Levenshtein.** Everyone else will use string distance.
A typosquat is a name-similar node in an **anomalous graph position**: brand-new maintainer, zero
reverse deps, dependency set copied wholesale from its target, published right after the target's
popularity spike. Name similarity is the *filter*; graph position is the *signal*.

---

### Leg 0 — Index case ← NEW in v2, and the reason the project has its name

**Input:** the observed compromised set (or any subset of it) + `as_of`.
**Method:** the same bounded pathfinding over **T2, walked backward**. Rank candidate origins by
how many of the observed compromised packages are reachable *from* that candidate along trust
edges, weighted by path exclusivity and by whether the candidate carries the vector signature
(`uses_pull_request_target`, `has_oidc_publish`).

This is epidemiological contact tracing. Given the symptoms, find the index case.

**Why this earns its place:**
1. **The name finally means something.** "Patient Zero" currently describes a project that never
   looks for patient zero.
2. **It is validated against a *different* published ground truth.** TanStack's own postmortem
   names the vector and the originating workflow. We seed with the 42 observed packages, never
   telling the system the answer, and check whether the true origin ranks first.
3. **It de-risks the trophy.** Risk #4 is "the forecast has no signal." Leg 0 is a second,
   independent, objectively-scoreable claim. If Leg 2 comes back null, the submission still has a
   validated result rather than a hedge.
4. **It is cheap.** Same procedure, `relDirection` reversed. It is the highest value-per-hour item
   in v2.

**Output:** ranked candidate origins with the trust path from each to the observed set, and a
single verdict line: *"Given only the 42 packages visible at 19:26, the true origin ranked #N."*

---

### Leg 2 — Blast forecast (T2, forward) ← the trophy

**Input:** seed set (the 42 packages known at 19:26) + `as_of` + `k`.
**Method:** propagation scoring over **T2, not T1**. A package scores high when it shares a
maintainer, repo, publishing workflow, or OIDC trust path with an already-compromised package.

Weighting that matters:
- **Exclusivity** — a maintainer with 3 packages is a far stronger signal than one with 400.
  Inverse-frequency weight the shared-entity edges, or the result is just a popularity ranking.
- **Vector match** — workflows carrying the `pull_request_target` pattern that was the actual
  breach vector score higher. This is what makes the forecast *about this attack* rather than
  generic co-occurrence.
- **Cross-ecosystem** — a maintainer publishing to both npm and PyPI is exactly how the worm
  crossed. Do not filter these out; they are the thesis.

**Output:** ranked packages, each with the **justifying trust path**. The path is not optional — an
unexplained ranking is not a product, and the path is what makes the demo legible.

**Do not tune against the validation set.** That is the one way to actually lose this track.

---

### Leg 3 — Reachability, Tier 1 only ← CUT in v2

| Tier | Question | Status in v2 |
|---|---|---|
| **1 — install** | Does it run a `preinstall`/`install`/`postinstall`/`prepare` hook? | **Shipped.** Free — already in the packument |
| 2 — import | Does the app transitively import the entry module? | **Cut** |
| 3 — call | Does a path exist from an entrypoint to a flagged symbol? | **Cut** |

**Why Tier 1 alone is the correct answer, not a compromise.** Commercial SCA conflates two
different questions. A malicious package is not "a vulnerable function you might call" — it is code
that executes at install time. If a compromised version is anywhere in your tree **and** it has an
install hook, you are owned. Reachability is 100% and no call graph is required. That is a property
predicate on data W3 already pulled on Day 0.

Being *more correct than Snyk on a real semantic distinction* is worth more to judges than a
half-finished call graph. Tiers 2–3 were the least original hours in the plan; cutting them funds
Leg 0, the evidence layer, and Leg 4.

**Output:** the alert-triage collapse — *"3,000 findings → 4 that actually execute"* — with the
reason each was cut visible in the UI. "We cut 99% of alerts" is only credible if a judge can see
*why*.

---

### Leg 4 — Leverage and min-cut ← NEW in v2, the actionable output

Everything above is forensic: it explains an incident that already happened. Leg 4 runs the same
math with **no incident at all**.

**Leverage index.** For every maintainer and workflow in the slice, run the forward T2 traversal
*as if* that credential were stolen, and count the services that fall. Output: a ranked list of the
highest-leverage trust paths in the slice. This is a **pre-incident** product — the thing someone
would actually buy — and it is a live prediction a judge can go check.

**Min-cut.** On the observed TanStack spread, compute the minimum set of accounts or workflows
whose hardening would have severed the propagation paths. Output: *"2FA on these N accounts would
have blocked X% of the observed spread."*

This is the demo's closing beat. It turns a scary chart into a decision, and it is graph theory the
judges will recognize on sight.

---

## 6. The evidence layer ← NEW in v2

The original design asserted the thesis and then demonstrated a forecast. v2 **tests** the thesis.

### The negative control
Run the **identical** forecast over T1 (dependency edges) and report its precision@K. Then run it
over T2 and report its precision@K.

The prediction the thesis makes is that T1 scores at or near zero, because the worm did not spread
that way. If T1 scores as well as T2, the thesis is wrong and we say so.

**Cost: one changed parameter** (`relTypes`). Almost nobody ships a control at a hackathon, and it
converts "quality of results" from an assertion into an experiment. Report both numbers side by
side, always, including in the video.

### R₀ per topology
Compute the basic reproduction number of the worm along each topology: the mean number of
subsequent compromises attributable to each compromised node, along T1 edges and along T2 edges.

Expected shape of the result: **R₀ ≈ 0 along dependency edges, R₀ > 1 along trust edges.** That
single pair of numbers is the entire thesis in one figure, it is a genuinely novel framing for
supply chain security, and it is the most quotable line available for a three-minute video.

### Show the query
Every panel in the UI carries a toggle that reveals the literal Cypher issued — the actual
`algo.SSpaths` call with its `maxLen` and `resultLimit` — and its measured latency.

The rules say HydraDB "has to do real work in your project, not just sit in the README." This makes
that inarguable, in the UI, in front of the judge. It costs approximately nothing.

---

## 7. Demo

A scrubbable clock, not a movie. The judge drags the timeline and **every panel re-queries at that
instant** — which is only possible because T1 is bitemporal, and only affordable because reads run
at 14,554 QPS while writes crawl at 225/sec. The demo *is* the argument for the architecture.

```
  19:20 ─────────────── 19:26 ─────────────── 19:46 ───────────────▶
        │                 │                    │
        │                 │                    └─ "The world found out here."
        │                 └─ we name the next victims  (Leg 2)
        │                    and the origin            (Leg 0)
        └─ worm begins

  LEFT   │ spread across the TRUST topology, incl. the npm→PyPI jump
  RIGHT  │ radius (Leg 1) · forecast (Leg 2) · origin (Leg 0) · triage (Leg 3)
  FOOTER │ T1 precision@K vs T2 precision@K · R₀ per topology   ← the control, always visible
```

The npm→PyPI crossing gets its own visual moment. It is the one edge a dependency-graph tool
cannot cross, and it is the thesis in a single animation.

**Video structure (3:00 hard limit):** problem 0:30 · the two-topologies insight + the npm→PyPI
proof 0:30 · live scrubbing demo 1:30 · HydraDB's role, the control, R₀, and the real element
count 0:30.

**Every number spoken is a measured number.** The element count is whatever W1 actually loaded —
*"a 1.8M-element ecosystem slice,"* never *"14M nodes."* Judges built this database and will know.

---

## 8. Schedule (v2)

| Day | Date | Milestone | Gate |
|---|---|---|---|
| **0** | Fri Aug 14 | D0-1 throughput spike · repo + Apache-2.0 · data path verified · packuments started | **Measured elements/sec → slice budget** |
| **1** | Sat Aug 15 | Slice → Parquet · schema frozen · loader written · stub API up | Slice fits the write budget |
| **2** | Sun Aug 16 | First full load · **Leg 1 end to end** · IOC set reconciled | Leg 1 answers the brief on real data |
| **3** | Mon Aug 17 | T2 built · **Leg 0 + Leg 2 scoring** · UI scaffold | Both produce ranked lists with paths |
| **4** | Tue Aug 18 | **Validation numbers: Leg 0 rank, Leg 2 precision@K, the T1 control, R₀** · Leg 4 · demo wired | 🔒 **FEATURE FREEZE end of day** |
| **5** | Wed Aug 19 | Polish · README with real numbers · attribution · **record video** | Video exists, ≤3:00 |
| **6** | Thu Aug 20 | Buffer · clean-machine dry run · **SUBMIT BY 2 PM PT** | Submitted |

**All validation numbers are due Day 4, not Day 5** — they must exist while there is still a day to
react if they are bad. **Submit Day 6 afternoon, not 11:59 PM.** The form is a single point of
failure and late is fatal.

---

## 9. Risk register (v2)

| # | Risk | Likelihood | Mitigation | Changed in v2 |
|---|---|---|---|---|
| 1 | Ingest slower than the "op" inference | **High** | D0-1 gates slice size; shrink depth until it fits | — |
| 2 | Supernode traversal blowup | High | Bounded `maxLen`/`resultLimit`, in-degree cap, precomputed closures | — |
| 3 | IOC ground truth incomplete/contradictory | Medium | Union-of-sources with provenance; publish the reconciled list | — |
| 4 | Forecast has no signal | Medium | **Leg 0 is a second independently-validated claim**; the control makes even a null result a reportable finding | ✅ materially reduced |
| 5 | Leg 3 tier 3 unfinished | ~~High~~ | **Cut by design.** Tier 1 is free and is the correct answer for worms | ✅ eliminated |
| 6 | Bitemporal filtering too slow unindexed | Medium | D0-1 measures it; fall back to per-day namespaces | — |
| 7 | Data-source access friction | Low | **deps.dev REST-first**, so nothing blocks on GCP billing | ✅ reduced |
| 8 | Submission mechanics | Low / **fatal** | Repo + license Day 0; submit Day 6 afternoon | — |
| 9 | v2 scope creep sinks the schedule | **Medium** | Leg 4 and the scrubbable clock are explicitly cuttable after Day 4 freeze; Legs 0–3 + evidence layer are the committed core | 🆕 |

---

## 10. Scoring self-check

| Criterion | How v2 wins it |
|---|---|
| Technical execution | Bitemporal graph, measured throughput budget, deliberate supernode strategy |
| **Use of HydraDB / graph-native** | One native `algo.SSpaths` primitive run in three directions over two topologies; architecture designed around *their* published write ceiling and supernode limits; the query is visible in the UI |
| Product completeness | Forensic *and* prophylactic, with an actionable min-cut output |
| **Quality of results** | Two independent validations (Leg 0 rank, Leg 2 precision@K) plus a **negative control** and **R₀** — an experiment, not a demo |
| **Originality** | Nobody else forecasts along the trust topology, traces an index case, ships a control, or reports a supply-chain R₀ |

---

## 11. Assumptions in force

Recorded because they were adopted without confirmation and should be revisited if wrong:

1. **Capacity is solo + subagents.** The four-workstream split is a task decomposition, not four
   people. Scope reflects this.
2. **Data path is deps.dev REST-first**, with BigQuery as an optimization if GCP billing is
   already available. W1 is never blocked on cloud account setup.
3. **Leg 3 is Tier 1 only.** Tiers 2–3 fund the v2 additions.
4. **Repo is fresh and local until pushed.** `C:\Users\lipey\Code\PatientZero`, Apache-2.0. The
   public GitHub remote is created on explicit go-ahead, since publishing is outward-facing.
5. **Ecosystem scope:** npm for T1 and reachability; PyPI in T2 only, where the cross-ecosystem
   evidence lives and where it is cheap.
6. **Services are real OSS application lockfiles**, not hand-authored. Same effort, far more
   credible.
