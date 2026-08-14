# Attribution

Patient Zero is licensed under [Apache-2.0](LICENSE).

This file lists third-party systems and published sources the project is **designed to use**.
Listing a source here does **not** mean its data has been ingested, loaded into HydraDB, or
scored. Ingest and validation status live in the data pipeline, not in this file.

## Graph engine

- [HydraDB](https://github.com/hydra-db/hydradb) — graph store and native path procedures (`algo.SSpaths`). Apache-2.0.

## Intended data sources (not a claim of ingest)

- [deps.dev](https://deps.dev/) — package and dependency metadata (REST-first path).
- [npm registry](https://www.npmjs.com/) — packuments, including install-hook fields used for reachability triage.
- [OSV](https://osv.dev/) — advisory records, if/when wired.

## Incident chronology — published record

The May 11 2026 TanStack / “Mini Shai-Hulud” timestamps and vector description used by the demo
clock come from vendor write-ups, not from a graph traversal:

- [Wiz — Mini Shai-Hulud strikes again](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised)
- [Aikido — Mini Shai-Hulud is back](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised)
- [Snyk — TanStack npm packages compromised](https://snyk.io/blog/tanstack-npm-packages-compromised/)
- [TanStack — npm supply-chain compromise postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)
- [Orca — TanStack npm supply-chain worm](https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/)
- [Rescana — TanStack npm supply-chain attack analysis](https://www.rescana.com/post/tanstack-npm-supply-chain-attack-detailed-analysis-of-the-may-2026-github-actions-breach-and-multi-ecosystem-impact)

A reconciled IOC list (seed vs validation split) is a W3 artifact. It is not published from this
file, and the demo must not treat stub/mock panel values as measurements.

## Data sources (W3, assembled 2026-08-14)

Reconciled IOC set and packuments are in `artifacts/`. Provenance notes: [`artifacts/SOURCES.md`](artifacts/SOURCES.md).

| Artifact | What |
|---|---|
| `artifacts/ioc.json` / `artifacts/ioc.md` | Union IOC list with `split ∈ {seed, validation}` and per-row `sources[]` |
| `artifacts/seed_packages.txt` | The 42 `@tanstack/*` seed names |
| `artifacts/packuments_seed.json` | npm packuments for the seed set (install-hook flags) |
| `artifacts/ioc_sources.json` | Checked-in vendor mapping; regenerate with `python scripts/ioc_reconcile.py --build-sources` |

Machine-readable copies used: GHSA-g7cv-rxg3-hmpx / CVE-2026-45321 via OSV and GitHub Advisory API. Additional full tables: StepSecurity, SafeDep, Socket (PyPI confirmation). None of the six specified blog URLs 404'd.

PyPI thesis evidence: `pypi:guardrails-ai@0.10.1` and `pypi:mistralai@2.4.6` are in the validation split.

## License of this repository

Apache License 2.0. See [LICENSE](LICENSE).
