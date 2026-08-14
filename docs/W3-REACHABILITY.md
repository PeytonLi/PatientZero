# W3 — Reachability / Ground Truth

**Read [`HANDOFF.md`](./HANDOFF.md) §4 (contracts) and §5 (ground truth) first.**
Design detail: [`DESIGN.md`](./DESIGN.md) §5 Leg 3, §2.

**You own:** npm packument enrichment, the IOC validation set, and Leg 3 (tiered reachability).
**You are blocked by:** nothing. **You start immediately.**
**You block:** W1's `versions.parquet` (via packuments) and W2's forecast validation (via IOC set).

Your two blocking deliverables are cheap and come first. Leg 3 comes after.

---

## D0/D1 — Packument enrichment (blocks W1)

Pull npm registry packuments for the slice and emit `data/enrich/packuments.parquet`:

```
pid, vid, has_install_script, install_hooks, maintainer_logins[], repo_url, published_at
```

- `install_hooks` ∈ subset of `preinstall`, `install`, `postinstall`, `prepare` — read from
  `scripts` in each version's manifest.
- `repo_url` normalizes to `rid = "github:org/name"` (W1's key format).
- Registry is free but rate-limited. Be polite, cache to disk, make it resumable.

**This is the highest-leverage 3 hours in the project** — see Tier 1 below.

---

## D2 — IOC ground-truth set (blocks W2's trophy metric)

Emit `data/truth/ioc.parquet`:
```
pid, vid, ecosystem, first_seen_utc, sources[], confidence
```

Assemble the confirmed compromised-package list for the May 11 2026 TanStack worm from:

[Wiz](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised) ·
[Aikido](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised) ·
[Snyk](https://snyk.io/blog/tanstack-npm-packages-compromised/) ·
[TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem) ·
[Orca](https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/) ·
[Rescana](https://www.rescana.com/post/tanstack-npm-supply-chain-attack-detailed-analysis-of-the-may-2026-github-actions-breach-and-multi-ecosystem-impact) ·
also check OSV.dev and GitHub Security Advisories for machine-readable entries.

**The split that makes the whole project scoreable:**

| Set | Content | Role |
|---|---|---|
| **Seed** | the 42 `@tanstack/*` packages, 19:20–19:26 UTC | forecast input |
| **Validation** | the 170+ confirmed by end of day May 11 | forecast target |

Mark every row with which set it belongs to and `first_seen_utc`, so W2 can seed at exactly
`19:26` and score against everything after.

**Risk #3 — sources will disagree.** Handle it explicitly:
- **Union of sources**, with per-package `sources[]` provenance and a `confidence` field.
- Do **not** silently drop packages one vendor lists and another does not.
- **Publish the reconciled list as a repo artifact.** Nobody else will have done this, it is
  genuinely useful to the community, and it makes your metric auditable rather than asserted.

---

## D4 — Leg 3: tiered reachability

### The insight — this is the sharpest idea in the project

Commercial SCA tools conflate two completely different questions. We separate them:

| Tier | Question | Cost | Verdict |
|---|---|---|---|
| **1 — install** | Does it run a `preinstall`/`install`/`postinstall`/`prepare` hook? | **Free** — already in the packument | **For worms this is the whole answer** |
| **2 — import** | Does the app transitively import the entry module? | Cheap static parse | module-level `import`/`require` |
| **3 — call** | Does a path exist from a service entrypoint to a flagged symbol? | Expensive | best-effort · **first thing cut** |

**Why Tier 1 dominates for this attack class:** a malicious package is not a "vulnerable function
you might call." It is code that executes at install time. If a compromised version is anywhere in
your tree **and** has an install hook, you are owned — reachability is 100%, and no call graph is
required. That is a property predicate on data you already pulled on Day 0.

Being *more correct than Snyk* on a real semantic distinction is worth more to judges than a
half-finished call graph. Lead with this in the README and the video.

### Tier 2
Module-level: resolve static `import`/`require` from each service's entrypoints through its
dependency tree. Emit `IMPORTS` edges plus `HAS_ENTRY` from `Version` to its entry `Module`.
Feed to W1 as additional edge Parquet, following the §4 contract.

### Tier 3
Symbol-level `CALLS` edges, scoped to the synthetic services and their **direct** deps only.
Answer via `algo.SPpaths` from entrypoint symbol to flagged symbol.

**Build this only if Leg 2 has validated and there is genuine slack on Day 5.** It is planned as
cuttable and the plan is not weakened by cutting it.

### Output — the headline number

Alert triage: **"3,000 findings → 4 that actually execute."**
Serve via W2's `POST /api/reachability` returning per-finding `{vid, tier, evidence}`.

The tiering must be visible in the UI. "We cut 99% of alerts" is only credible if a judge can see
*why* each one was cut.

---

## Definition of done

- [ ] `data/enrich/packuments.parquet` delivered to W1 (**Day 1**)
- [ ] `data/truth/ioc.parquet` with seed/validation split delivered to W2 (**Day 2**)
- [ ] Reconciled IOC list published as a repo artifact with provenance (**Day 2**)
- [ ] Tier 1 verdicts for every finding (**Day 4**)
- [ ] Tier 2 module-level reachability (**Day 4**)
- [ ] Tier 3 — only if Leg 2 validated and slack exists (**Day 5, optional**)

## Traps

- Starting Leg 3 before the two blocking deliverables ship. W1 and W2 stall without you.
- Treating a malicious package like a CVE. Different question, different tier, different answer.
- Dropping packages where sources disagree instead of recording the disagreement.
- Building Tier 3 before Tier 1. Tier 1 is free and carries the leg.
- Trusting a single vendor blog as ground truth.

## Suggested skills

`context7-mcp` (npm registry API shapes) · `superpowers:test-driven-development` (tier
classification logic) · `superpowers:verification-before-completion`
