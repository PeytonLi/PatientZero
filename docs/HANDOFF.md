# Patient Zero — Handoff (v2)

**Read this first, then [`DESIGN.md`](./DESIGN.md).** The design was revised on Aug 14 —
[`DESIGN.md`](./DESIGN.md) is authoritative and supersedes anything here that contradicts it.

| | |
|---|---|
| **Event** | [Hack Hydra](https://hackhydra.hydradb.com/), Aug 12–20 2026, 100% online |
| **Track** | 2A — Supply Chain Blast Radius |
| **Deadline** | **Aug 20 2026, 11:59 PM PT** (submit by 2 PM PT — §6) |
| **Today** | Aug 14 2026 — ~6 build days remain |
| **Budget** | $50–300 LLM+compute |
| **Prizes** | $5,000 grand · $3,000 runner-up · $1,500 third · $500 best HydraDB use |
| **Repo** | `C:\Users\lipey\Code\PatientZero` — local, Apache-2.0. **Public remote not yet created.** |

---

## 1. What we are building, in five lines

> **A supply chain worm travels along trust edges — maintainer accounts, publishing workflows,
> OIDC grants — not down dependency edges.** Two topologies over the same nodes. Every existing
> tool walks only the first, which is why every existing tool is purely retrospective.

The May 11 2026 TanStack npm worm is the proof: it spread on **stolen CI credentials**, which is
why it jumped from npm to PyPI — a crossing impossible along dependency edges and trivial along
maintainer edges.

**The system is one graph primitive — bounded `algo.SSpaths` — run in three directions of time:**

| Direction | Product | Scored against |
|---|---|---|
| **Backward** over trust | **Leg 0 — index case.** Who did this? | TanStack's published postmortem |
| **Forward** over trust | **Leg 2 — forecast.** Who falls next? | the reconciled 170+ IOC set |
| **Forward from nothing** | **Leg 4 — leverage + min-cut.** Who could fall? | live prediction |

Plus **Leg 1** (blast radius: the same primitive over the *dependency* topology, backward,
bitemporally filtered) and **Leg 3** (reachability: a property predicate, Tier 1 only).

And an **evidence layer** that most hackathon projects skip: a **negative control** (identical
forecast over dependency edges, expected to score ≈0) and **R₀ per topology**.

Full detail: [`DESIGN.md`](./DESIGN.md) §1, §5, §6.

---

## 2. Non-negotiable constraints — read before designing anything

Measured from HydraDB's own published benchmarks, not guessed.

| Constraint | Value | What it forces |
|---|---|---|
| **Write throughput** | **~225 ops/sec, flat** | Graph targets **1–2M elements**, not 50M |
| **Write concurrency** | conc=32 → still ~224 ops/sec, p50 **141s** | **Never parallelize writers.** One loader, single-threaded. |
| **Read throughput** | 14,554 QPS @ conc=32 | Reads are free. Put all cleverness at read time. |
| **Traversal @ fanout 10k** | 1 hop 824ms · 10 hops 5.5s · 20 hops 10.9s | Supernodes are the query risk. Bound **every** traversal. |
| **Bulk loader** | **Does not exist** | Bolt / HTTP NDJSON only, via batched `UNWIND` |
| **Atomic `MERGE`** | Not documented as upsert | **All dedup happens offline**, with precomputed stable IDs |

```
deps.dev (REST) ───┐
npm packuments  ───┼──▶ DuckDB / Parquet ──▶ ONE single-threaded ──▶ HydraDB ──▶ fast bounded
OSV.dev         ───┤    (resolve + dedupe +   idempotent loader        (immutable   traversals
GitHub API      ───┘     stable IDs)          (batched UNWIND)          snapshot)
                          W1                        W2                      W2 → W4
```

**Everything v2 added — Leg 0, the control, R₀, Leg 4 — is read-time work over a graph we were
already loading. It costs zero write budget.**

### ⚠️ Day-0 gate — blocks schema design and slice sizing

Their `ops=227.5/sec` at `p50=4,398ms` implies ~1,000 operations per commit → batched `UNWIND`
gives **~225 edges/sec → 1M edges in ~74 min**. **That is an inference, not a documented fact.**
If an "op" is one *row*, throughput collapses ~10x and the slice must shrink hard.

Task **D0-1** measures it → [`MEASURED.md`](./MEASURED.md). **No schema is frozen until that file
exists.**

---

## 3. Hackathon rules that can disqualify you

- ✅ **Work must start on or after Aug 12 2026.** Do not import code written before Aug 12.
- ✅ **Public GitHub repo** with complete source, README with setup instructions, an explanation of
  HydraDB integration, an **open-source license**, and third-party attribution.
- ✅ **Demo video, 3 minutes or less** — problem, solution, demo, HydraDB usage.
- ✅ **Submission form** by Aug 20 11:59 PM PT.
- ⚠️ **"HydraDB has to do real work in your project, not just sit in the README."** → this is why
  the UI has a **show-query toggle** exposing the literal Cypher and its latency ([`DESIGN.md`](./DESIGN.md) §6).
- ⚠️ Missing video, private repo, no license, or late submission = **disqualified**.

**Judging:** technical execution · use of HydraDB and graph-native approaches · product
completeness and usability · quality of results · originality. Judged within track first.

---

## 4. Delegation map

| Workstream | File | Owns | Blocked by |
|---|---|---|---|
| **W1 — Ingest / ETL** | [`W1-INGEST.md`](./W1-INGEST.md) | D0-1 spike, deps.dev→Parquet, slice sizing, stable IDs | nothing — **starts first** |
| **W2 — Engine / Queries** | [`W2-ENGINE.md`](./W2-ENGINE.md) | Loader, schema, Legs 0/1/2/4, evidence layer, HTTP API | D0-1 (schema), W1 Parquet (load), W3 IOC (validation) |
| **W3 — Ground truth** | [`W3-REACHABILITY.md`](./W3-REACHABILITY.md) | Packuments, IOC validation set, Leg 3 Tier 1 | nothing — **starts first** |
| **W4 — Demo / Frontend** | [`W4-DEMO.md`](./W4-DEMO.md) | Scrubbable clock UI, show-query, README, video | nothing (mock the API) — **starts first** |

### Interface contracts — fixed here, not negotiated at runtime

**W1 → W2: Parquet in `data/graph/`.** Stable IDs computed **offline by W1**, because HydraDB has
no `MERGE`:
```
vid = "npm:@tanstack/react-query@5.0.1"   pid = "npm:@tanstack/react-query"
mid = "npm:tannerlinsley"                 rid = "github:TanStack/query"
```

| File | Columns |
|---|---|
| `packages.parquet` | `pid, ecosystem, name` |
| `versions.parquet` | `vid, pid, ecosystem, name, version, published_at, unpublished_at, has_install_script, install_hooks` |
| `maintainers.parquet` | `mid, ecosystem, login, email_domain, twofa` |
| `repos.parquet` | `rid, host, org, name` |
| `workflows.parquet` | `wid, rid, path, trigger, uses_pull_request_target, has_oidc_publish` |
| `services.parquet` | `sid, name, source_repo` |
| `advisories.parquet` | `aid, source, severity` |
| `edges_depends_on.parquet` | `src_vid, dst_vid, range, resolved_version, valid_from, valid_to` |
| `edges_pins.parquet` | `sid, dst_vid, lockfile_at, valid_from, valid_to` |
| `edges_maintains.parquet` | `mid, pid` |
| `edges_published_from.parquet` | `pid, rid` |
| `edges_has_workflow.parquet` | `rid, wid` |
| `edges_publishes_via_oidc.parquet` | `wid, pid` |
| `edges_affects.parquet` | `aid, vid` |

All timestamps are **epoch seconds, UTC, integer**. `valid_to` for a still-valid edge is
`4102444800` (2100-01-01), **never null**.

**W3 → W1: `data/enrich/packuments.parquet`**
`pid, vid, has_install_script, install_hooks, maintainer_logins[], repo_url, published_at`

**W3 → W2: `data/truth/ioc.parquet`**
`pid, vid, ecosystem, first_seen_utc, sources[], confidence, split` where `split ∈ {seed, validation}`
— seed is the 42 packages visible at 19:26, validation is everything confirmed after.

**W2 → W4: HTTP API** (FastAPI, `localhost:8000`)
```
POST /api/blast-radius {ecosystem,name,version,window_start,window_end,max_hops}
                    -> {services:[{sid,name,exposed_at,path:[vid,...]}], stats, cypher, latency_ms}
POST /api/forecast     {seeds:[pid,...], as_of, k, topology:"trust"|"dependency"}
                    -> {predictions:[{pid,score,justification_path}], stats, cypher, latency_ms}
POST /api/index-case   {observed:[pid,...], as_of, k}
                    -> {candidates:[{id,kind,score,path_to_observed}], stats, cypher, latency_ms}
POST /api/reachability {sid, finding_vids:[vid,...]}
                    -> {verdicts:[{vid,tier:"install"|"none",evidence}], stats, cypher, latency_ms}
GET  /api/leverage     -> {ranked:[{id,kind,services_at_risk,path}], mincut:[...], stats, cypher}
GET  /api/evidence     -> {precision_trust:{...}, precision_dependency:{...}, r0_trust, r0_dependency}
GET  /api/timeline     -> the May 11 event timeline for the clock component
```

Two contract changes from v1, both load-bearing:
- **every response carries `cypher` and `latency_ms`** — this feeds the show-query toggle that
  proves HydraDB is doing real work;
- **`/api/forecast` takes a `topology` parameter** — the same endpoint serves the forecast and its
  negative control. That is what makes the control one changed parameter rather than a second system.

**W4 mocks these from hour one.** W2 ships correctly-shaped stubs on **Day 1** before the logic exists.

---

## 5. Ground truth

| Time (UTC, May 11 2026) | Event |
|---|---|
| 19:20–19:26 | 84 malicious versions across **42 `@tanstack/*` packages** |
| ~19:46 | First public detection (external researcher, StepSecurity) |
| End of day | **170+ packages, 400+ malicious versions**, npm *and* PyPI |

Vector: `pull_request_target` "Pwn Request" → GitHub Actions cache poisoning across the fork↔base
trust boundary → OIDC token extracted from runner memory. Actor: TeamPCP, "Mini Shai-Hulud."

**Two independent validations:**
- **Leg 2** — seed with only the 42 packages known at 19:26; score the ranked output against the
  170+ confirmed later. Report precision@10/@50/@100 and recall@K, **alongside the same numbers
  for the dependency-topology control.**
- **Leg 0** — seed with the same 42, never revealing the vector, and check where the true origin
  (named in TanStack's postmortem) ranks.

The claim, if it works: *"The world found out at 19:46. At 19:26 we would have named both the
origin and the next victims."*

If either fails, **report the negative result with the numbers.** A measured miss scores better
under "quality of results" than an unmeasured demo.

Sources: [Wiz](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised) ·
[Aikido](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised) ·
[Snyk](https://snyk.io/blog/tanstack-npm-packages-compromised/) ·
[TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem) ·
[Orca](https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/) ·
[Rescana](https://www.rescana.com/post/tanstack-npm-supply-chain-attack-detailed-analysis-of-the-may-2026-github-actions-breach-and-multi-ecosystem-impact)

---

## 6. Schedule

See [`DESIGN.md`](./DESIGN.md) §8. Two hard gates:

- **Day 4 (Tue Aug 18):** all validation numbers exist — Leg 0 rank, Leg 2 precision@K, the
  dependency control, R₀. 🔒 **Feature freeze end of day.**
- **Day 6 (Thu Aug 20):** **submit by 2 PM PT.** Not 11:59. The form is a single point of failure.

---

## 7. Environment

- Docker 29.2.1 ✅ · Python 3.13 ✅ · ~1 TB free ✅ · Windows 11 / PowerShell (Bash also available)
- `pip install neo4j duckdb pyarrow fastapi uvicorn` — none were present initially
- `gcloud` ❌ not installed. **This does not block anything** — the data path is deps.dev REST-first.

**HydraDB local** — verbatim from their README (Unix; on Windows drop `--user` and use an absolute
volume path):
```bash
docker pull ghcr.io/hydra-db/hydradb:latest
mkdir -p hydradb-data/store hydradb-data/cache
printf '%s\n' 'local-development-token-32-bytes' > hydradb-data/auth-token
docker run --rm --user "$(id -u):$(id -g)" \
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

**HydraDB speaks Bolt 5.x — the stock `neo4j` Python driver connects.** You are not writing a
driver. OpenCypher subset: typed relationships, bounded variable-length paths, property and label
predicates, ordering, pagination, aggregation, `OPTIONAL MATCH`, `UNION`, batched `UNWIND` writes.

Native path procedures — **this is the whole engine**:
```cypher
CALL algo.SPpaths({sourceLabel, sourceProperty, sourceValues, targetValues,
                   relTypes, relDirection, maxLen, pathCount, resultLimit}) YIELD path
CALL algo.SSpaths({...same...})
CALL algo.MSpaths({...same..., pairwise, fairRelationshipVariants})
```

**Links:** [repo](https://github.com/hydra-db/hydradb) · [benchmarks](http://graph-benchmark.hydradb.com/) ·
[Discord](https://discord.gg/D8cGSa9H9) (office hours all 9 days — **ask them what one "op" means**) ·
[submission form](https://forms.gle/WEwqEmmN7Bkp4HyJ6)

---

## 8. Decisions — do not relitigate

| Decision | Choice | Why |
|---|---|---|
| Track | **2A** | Lowest entrant density, most graph-native, only track with dated objective ground truth |
| Framing | **One primitive, three directions of time** | Parts reinforce instead of competing for six days |
| Leg 0 (index case) | **In** | Second independent validation; de-risks Leg 2; makes the name mean something |
| Evidence layer | **In** | Control + R₀ turn an assertion into an experiment. Near-zero cost |
| Leg 3 | **Tier 1 only** | Correct answer for worms, and funds the above |
| Leg 4 | **In, cuttable after Day 4** | The only pre-incident, actionable output |
| Data path | **deps.dev REST-first** | Never blocked on GCP billing |
| Ecosystem | npm for T1 + reachability; **PyPI in T2 only** | Cross-ecosystem jump is the thesis evidence and is cheap there |
| Lockfiles | **Real** OSS app lockfiles | Same effort, far more credible |
| Writers | **One, single-threaded** | Concurrency measurably does not help |
| Dedup | **Offline, in DuckDB** | No atomic `MERGE` |
| Repo | Fresh, local, Apache-2.0 | Public remote awaits explicit go-ahead — publishing is outward-facing |

---

## 9. Risk register

See [`DESIGN.md`](./DESIGN.md) §9. Net effect of v2: risk #4 (forecast has no signal) is materially
reduced by Leg 0 and the control; risk #5 (tier 3 unfinished) is eliminated by cutting it; risk #7
(cloud access) is reduced by the REST-first path. One new risk: **#9, v2 scope creep** — Leg 4 and
the scrubbable clock are explicitly cuttable; Legs 0–3 plus the evidence layer are the committed core.

---

## 10. Immediate next actions

1. ✅ **D0-1 throughput spike** — running. Everything downstream is sized by its result.
2. ✅ **Repo scaffolded** at `C:\Users\lipey\Code\PatientZero` with Apache-2.0.
3. **W3 and W4 start immediately** — neither is blocked.
4. **Create the public GitHub remote** — needs a human go-ahead, then push same day.
5. Join the [HydraDB Discord](https://discord.gg/D8cGSa9H9) and ask in office hours what one "op"
   means in their write benchmark. That single answer may confirm or overturn D0-1.
