# W1 — Ingest / ETL

**Read [`HANDOFF.md`](./HANDOFF.md) §2 (constraints) and §4 (interface contracts) first.**
Design detail: [`DESIGN.md`](./DESIGN.md) §3, §6.

**You own:** the Day-0 throughput spike, all external data acquisition, offline entity resolution,
slice sizing, and the Parquet handoff to W2.
**You are blocked by:** nothing. **You start first.**
**You block:** W2's schema freeze (via D0-1) and W2's load (via Parquet).

---

## The one thing that matters

HydraDB writes at **~225 ops/sec and concurrency does not help** (conc=32 → still ~224 ops/sec,
p50 latency 4.4s → 141s). There is **no bulk loader** and **no atomic `MERGE`**.

Therefore: **you resolve and deduplicate everything offline and emit immutable, pre-keyed
Parquet.** The loader is dumb on purpose. If you find yourself wanting to dedupe inside Cypher,
you have taken a wrong turn.

---

## D0-1 — Throughput spike ⚠️ BLOCKS EVERYTHING

Nobody freezes a schema or sizes a slice until this number exists.

**Question:** what does one "op" mean in HydraDB's write benchmark? Their published numbers
(`ops=227.5/sec` at `p50=4,398ms`) imply ~1,000 operations land per commit — i.e. batched `UNWIND`
gives **~225 edges/sec**, so 1M edges ≈ 74 minutes. **That is an inference, not a fact.** If an
"op" is one row, throughput drops ~10x and the whole slice must shrink.

**Do this:**

1. Start HydraDB locally — the verbatim Docker command is in [`HANDOFF.md`](./HANDOFF.md) §7.
2. Connect with the stock `neo4j` Python driver over Bolt (`bolt://127.0.0.1:7687`). HydraDB
   speaks Bolt 5.x; do not write a driver.
3. Load 100,000 synthetic edges via batched `UNWIND` at batch sizes **100 / 1,000 / 10,000**:
   ```cypher
   UNWIND $rows AS r
   CREATE (a:Version {vid: r.src})-[:DEPENDS_ON {valid_from: r.vf, valid_to: r.vt}]->(b:Version {vid: r.dst})
   ```
4. Record wall-clock seconds and derive **edges/sec** for each batch size.
5. Separately time a batch that creates nodes only, and one that creates edges between
   *existing* nodes (`MATCH` both ends then `CREATE` the rel) — the second is what the real
   loader does and is likely slower.

**Deliverable:** `docs/patient-zero/MEASURED.md` containing:
- edges/sec at each batch size, and the winning batch size
- **the slice budget**: how many total elements fit in a 90-minute load
- whether property-predicate filtering on `valid_from`/`valid_to` is usably fast without an index
  (load 100k edges, then time a filtered 3-hop traversal) — this decides risk #6

**Shortcut worth trying first:** ask in the [HydraDB Discord](https://discord.gg/D8cGSa9H9) office
hours what one "op" means in their benchmark. That answer may replace this entire task.

---

## D0-2 — GCP / BigQuery access

`gcloud` is **not installed** on this machine. Either install it, or use
`google-cloud-bigquery` with a service-account JSON.

Verify you can query the public deps.dev dataset before it is on the critical path:
- Docs: https://docs.deps.dev/bigquery/v1/
- 5M packages, 50M+ versions, npm/PyPI/Go/Maven/Cargo
- **Pre-resolved dependency graphs** — one row per edge. This is why we use deps.dev: you do not
  have to write a semver resolver.
- Free tier is 1 TB/month of query. Budget is $50–300, so this is comfortable — but *do* use
  partition/cluster filters, a naive `SELECT *` over the graph table will burn the free tier.

---

## D1 — Slice extraction

**Do not try to load npm.** 50M versions at 225 ops/sec is 62 hours of pure writing.

**Slice definition:**
1. The **42 seed packages** (`@tanstack/*` compromised May 11 19:20–19:26) — W3 delivers the exact
   list in `data/truth/ioc.parquet`.
2. Their **reverse dependency closure to depth *d***.
3. The **trust-topology neighborhood** of every maintainer touching them (their other packages,
   repos, workflows) — this is Leg 2's substrate and is small relative to the dependency closure.
4. A **20-service synthetic company** built from **real OSS application lockfiles** (decision made:
   real, not hand-authored — same effort, far more credible).

**Tune *d* until total elements land in 1–2M** (3M hard ceiling), using the D0-1 budget.
Start at *d*=3 and measure before going deeper — reverse closures grow viciously.

**Honesty rule:** the headline is *"a 1.8M-element ecosystem slice"* or whatever the real number
is. Never *"14M nodes."* Judges built this database and know its write path; an inflated number is
the fastest way to lose credibility.

---

## D1 — Emit Parquet

Exact schemas are in [`HANDOFF.md`](./HANDOFF.md) §4. Non-negotiable rules:

- **Stable IDs computed here.** `vid = "npm:@tanstack/react-query@5.0.1"`, `pid = "npm:name"`,
  `mid = "npm:login"`, `rid = "github:org/name"`. HydraDB has no `MERGE`, so identity is your job.
- **All timestamps epoch seconds, UTC, integer.**
- **`valid_to` for a still-valid edge is `4102444800`** (2100-01-01), never null. Null handling in
  predicate filters is a risk we are not taking.
- **Fully deduplicated.** A duplicate row becomes a duplicate node, silently, forever.
- **Deterministic ordering** so reloads are reproducible.

Join in W3's `data/enrich/packuments.parquet` (install scripts, maintainers, repo URLs) before
emitting `versions.parquet` and `edges_maintains.parquet`.

---

## Other sources

| Source | Use | Notes |
|---|---|---|
| **npm registry packuments** | maintainers, install scripts, repo URLs, publish times | **W3 pulls these**, you join them |
| **OSV.dev** | advisories + affected ranges | Free bulk zips per ecosystem — take the zip, do not crawl the API |
| **GitHub API** | workflow files, `pull_request_target` + OIDC detection | Token required, rate-limited. Only needed for repos in the trust neighborhood |

---

## Definition of done

- [ ] `MEASURED.md` exists with real edges/sec and a slice budget (**Day 0**)
- [ ] BigQuery queries against deps.dev succeed (**Day 0**)
- [ ] Slice extracted, *d* chosen from measurement, total elements within budget (**Day 1**)
- [ ] All 14 Parquet files emitted, schema-conformant, deduplicated, with stable IDs (**Day 1**)
- [ ] A `scripts/etl.py` that reproduces the whole thing from scratch — judges must be able to
      re-run your pipeline, and the README setup instructions get dry-run on a clean machine Day 6

## Traps

- Parallelizing the loader. Measurably does not help; destroys latency. **One writer.**
- `SELECT *` on deps.dev's graph table. Filter first.
- Deduping in Cypher. There is no `MERGE`. Dedupe in DuckDB.
- Nullable `valid_to`. Use the sentinel.
- Going deeper than *d*=3 before measuring the blowup.
- Loading the full graph "just to see." You get ~90 minutes per load; spend them deliberately.
