# Data sources — W3 ground truth

This file records the public sources used to assemble the reconciled IOC set
and packuments. It is the W3 attribution surface; do not treat a single vendor
blog as complete.

## Incident

Mini Shai-Hulud / TeamPCP, May 11 2026. Initial burst: 84 malicious versions
across 42 `@tanstack/*` packages (19:20–19:26 UTC), published via a hijacked
GitHub Actions OIDC identity on `TanStack/router`. Worm propagation then hit
other npm namespaces and two PyPI projects.

## Primary sources (fetched 2026-08-14)

| id | url | status | published |
|---|---|---|---|
| tanstack_postmortem | https://tanstack.com/blog/npm-supply-chain-compromise-postmortem | **200** | 2026-05-11 |
| wiz | https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised | **200** | 2026-05-12 (updated 05-13) |
| aikido | https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised | **200** | 2026-05-12 (updated 05-19) |
| snyk | https://snyk.io/blog/tanstack-npm-packages-compromised/ | **200** | 2026-05-11 |
| orca | https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/ | **200** | 2026-05-12T15:29:00Z |
| rescana | https://www.rescana.com/post/tanstack-npm-supply-chain-attack-detailed-analysis-of-the-may-2026-github-actions-breach-and-multi-ecosystem-impact | **200** | 2026-05-12 |
| ghsa | https://github.com/advisories/GHSA-g7cv-rxg3-hmpx | **200** (API) | 2026-05-12T00:12:49Z |
| osv | https://osv.dev/vulnerability/GHSA-g7cv-rxg3-hmpx | **200** (API) | same GHSA |
| cve | https://osv.dev/vulnerability/CVE-2026-45321 | **200** | alias of GHSA |

No specified URL 404'd. The GitHub HTML advisory page is a JS shell; the
machine-readable copy was taken from `api.github.com/advisories/GHSA-g7cv-rxg3-hmpx`
and `api.osv.dev/v1/vulns/GHSA-g7cv-rxg3-hmpx`.

## Additional listings used (not in the original six-URL list)

These were needed because Snyk/Orca/Rescana do not publish a complete
per-package table, and the HANDOFF asked to search OSV and GHSA.

| id | url | why |
|---|---|---|
| stepsecurity | https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem | First public detection (issue #7383 at 19:46:46 UTC); versioned table |
| safedep | https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral | Versioned appendix: 170 npm + 2 PyPI |
| socket | https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack | PyPI confirmation at 2026-05-12 03:05:38 UTC |

## Machine-readable caches (gitignored)

`data/truth/raw/osv_GHSA-g7cv-rxg3-hmpx.json` — 42 packages × 2 versions.
`data/truth/raw/github_GHSA-g7cv-rxg3-hmpx.json`
`data/truth/raw/osv_CVE-2026-45321.json`
`data/truth/raw/osv_MAL-2026-3465.json` (`@tanstack/react-router`)
`data/truth/raw/osv_MAL-2026-3432.json` (`@mistralai/mistralai`, also cited by Snyk)

OSSF `MAL-*` records exist per package; GHSA-g7cv-rxg3-hmpx is the seed-set
advisory. We did not scrape every MAL file; vendor tables already union to 170+.

## Packuments

npm: `GET https://registry.npmjs.org/<name>` (scoped: `@tanstack%2f…`).
PyPI: `GET https://pypi.org/pypi/<name>/json`.
Cache: `data/enrich/packuments/`.

Pulled **180** packuments (42 seed + 138 validation). **172 ok, 8 HTTP 404**:
`@dirigible-ai/sdk`, `@draftauth/client`, `@draftauth/core`, `@draftlab/auth-router`,
`@ml-toolkit-ts/preprocessing`, `@ml-toolkit-ts/xgboost`, npm `guardrails-ai`, npm `mistralai`.
The last two 404s support treating them as PyPI-only (Wiz also listed them under npm).

All **84 seed version documents are unpublished** (`vid_source=ioc_vid_unpublished`).
npm's packument `time` map still carries the original timestamps (19:20:39 / 19:26:14).
`has_install_script` is **false on all 84 seed rows**. That matches the postmortem: the
host `scripts` block was not modified; `prepare` ran on the git optionalDependency
`@tanstack/setup`. Live follow-up versions also have no install hooks.

## Regeneration

```
python scripts/ioc_reconcile.py --build-sources
python scripts/packuments.py
```
