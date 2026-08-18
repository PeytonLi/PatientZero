# Patient Zero — product roadmap

North star: epidemiology over **credentials**, not a Snyk clone. The dependency
topology (T1) is the **control**. The trust topology (T2) is the instrument.

This is post-hackathon product work. The May 11 TanStack / Mini Shai-Hulud
slice stays the fixture. We do not retune scoring against that validation set.

## What we will not build first

- Auth, tenancy, SSO
- Full-npm ingest
- A CVE inbox
- Tuning precision@K on the May 11 IOCs (measured 0.0; that result stays)

## Three bets

1. **Stolen-identity simulator** — leverage / forward T2. “If this credential
   is stolen, what falls?” Min-cut is the action.
2. **Contact tracing for a bag of publishes** — index case. This already
   worked: workflow `github:TanStack/router:.github/workflows/release.yml`
   ranked #1.
3. **Registry-boundary map** — npm → PyPI on a shared identity. The edge a
   dependency graph cannot cross.

---

## Now (this pass)

Make the demo a method you can point at a *second* incident later, and make
the control unmissable.

| Item | Why |
|---|---|
| **Incident object** `{seeds, as_of, validation?}` | May 11 is fixture #1, not a pile of constants (`WORM_START`, timeline ticks, `TRUE_ORIGIN_MID`). |
| **T2 bitemporal** `valid_from` / `valid_to` on MAINTAINS, PUBLISHED_FROM, HAS_WORKFLOW, PUBLISHES_VIA_OIDC | Same filter path T1 already has. Without historical tenure, stamp `0 → sentinel` so the path exists. |
| **Min-cut on the trust neighborhood** | Cover the 84 forecast packages, not the 138 validation pids (intersection was empty → `mincut []`). |
| **Control as a first-class strip** | Same `algo.SSpaths`, `relTypes` swapped. Path counts, not precision@K, are the demonstration. Precision stays in the evidence footer, honestly zero. |

## Goal

Finish **Next**. One item at a time: plan → TDD (one behavior, then the code) → next item.

- [x] Identity home
- [x] Cross-registry bridges
- [x] Popularity vs rarity ranks
- [x] On-demand ingest around an identity or incident

### Identity home — plan

Question: *if this credential is stolen, what falls?*

Public interface: `GET /api/identity?id=npm:tannerlinsley` (same envelope as every other
route). Click a leverage chip or index-case candidate; the panel is the stolen-identity
simulator for one maintainer, workflow, or repo.

Behaviors, in TDD order:

1. Unknown id → `found: false`, empty packages.
2. Known maintainer → `kind`, `name`, packages they `MAINTAINS`.
3. That credential in the forecast neighborhood → `packages_at_risk` and min-cut `action`.
4. Workflow → packages they `PUBLISHES_VIA_OIDC`.
5. API route is a 200 envelope.
6. UI opens the panel from leverage / index-case.

Not this item: search-all-npm, ingest, matching the same human across registries
(that is the next item). No new HydraDB procedure — catalog join plus the existing
leverage neighborhood.

### Cross-registry bridges — plan

Question: *does this credential cross npm → PyPI?*

Same identity object. A second join, not a traversal. Link maintainers by
(1) login across ecosystems, (2) `email_domain` when present, (3) GitHub org
via `PUBLISHED_FROM` of packages they touch.

Behaviors, in TDD order:

1. `npm:alice` lists `pypi:alice` as an alias when both exist.
2. Two maintainers sharing `email_domain` are aliases.
3. `registries` is the union of ecosystems on this identity and its aliases.
4. Identity panel already prints "Crosses npm + pypi" when `registries.length > 1`.

### Popularity vs rarity ranks — plan

Question: *is this ranked because the credential is rare, or because it is everywhere?*

Forecast already scores `(1 / degree) × vector` — exclusivity. That down-ranks
`tannerlinsley` (degree 256). Surface it as `rank: rarity | popularity` on the
same forecast. Popularity is `degree × vector`. Index-case stays exclusive
(that is contact tracing). Default remains rarity so existing evidence does
not silently change.

Behaviors, in TDD order:

1. Default `rank=rarity` keeps the rare co-maintainer first.
2. `rank=popularity` inverts that order on the same paths.
3. API accepts `rank` on `/api/forecast`.
4. UI toggle next to TRUST / DEPENDENCY.

### On-demand ingest — plan

Question: *expand the slice around this credential, do not boil npm.*

`POST /api/expand` with `{id, search?}`. Merges maintainer search hits into the
in-memory catalog (MAINTAINS + package stubs). No HydraDB write, no live npm
from the request path — tests inject search JSON; live uses `data/npm-search/{login}.json`
if present. Identity then lists the new packages.

Behaviors, in TDD order:

1. Unknown id → `found: false`, `added: 0`.
2. Known maintainer + search JSON with a new package → `added: 1`, identity lists it.
3. API route is a 200 envelope.
4. Identity panel has an Expand control.

---

## Later

- Credential telemetry (when a token actually moved)
- Policy predicates (“revoke this, disable that”)
- R₀ as weather, not a trophy
- Then auth / SSO

---

## What already measured (do not paper over)

Trust forecast: **84 ranked packages with paths**. Identical query on
`DEPENDS_ON` / `PINS`: **0 paths**. Precision@K and R₀ vs 138 validation IOCs:
**0.0**. Blast radius empty (no reverse npm dependents in the slice). See
`artifacts/evidence.json` and `docs/MEASURED.md`.
