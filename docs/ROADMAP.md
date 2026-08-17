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

## Next

- **Identity home** — pick a maintainer / workflow / OIDC grant; see packages
  at risk and the min-cut action.
- **Cross-registry bridges** — same human across npm and PyPI (login, email
  domain, GitHub org). Needs a second data join, not another traversal.
- **Popularity vs rarity ranks** — exclusivity already down-ranks
  `tannerlinsley` (degree 256). Surface that as a toggle, not a buried weight.
- **On-demand ingest around an identity or incident** — expand the slice
  instead of boiling the registry.

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
