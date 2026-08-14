# Reconciled IOC set — Mini Shai-Hulud / TanStack (May 11 2026)

Union of public vendor listings. A package one vendor lists and another
omits is **kept**, with the disagreement recorded. Do not treat this as
npm's unpublished-tarball ground truth; several malicious versions were
removed from the registry the same evening.

## Counts

- **Seed packages:** 42 / 42 target (84 malicious versions)
- **Validation packages:** 138 (target was 170+; see honesty note) (331 malicious versions)
- **Source disagreements:** 46 packages
- **PyPI packages:** 2 — pypi:guardrails-ai, pypi:mistralai

### Honesty note

Aikido claimed 169 npm names (no PyPI). SafeDep published 170 npm + 2 PyPI = 172 total. Vendor '170+' figures are end-of-day totals including the 42 seed packages, not a 170-row validation split. Union here is 180 packages (42 seed + 138 validation) and 415 versions (84 seed + 331 validation). Wiz-only extras kept per union policy: @cap-js/*, intercom-client, lightning, mbt, and unscoped npm mistralai/guardrails-ai (those two 404 on npm; they exist on PyPI).

Seed timestamps are the two publish batches from TanStack's postmortem
(`2026-05-11T19:20:39Z` and `2026-05-11T19:26:14Z`). Validation timestamps
are the **earliest citing article `published_utc`**, not the registry
publish time — vendors rarely give one. `first_seen_utc` is null only
when no source timestamp exists; we did not guess 19:26 for later victims.

## Sources

| id | published_utc | url |
|---|---|---|
| `tanstack_postmortem` | 2026-05-11T21:00:00Z | https://tanstack.com/blog/npm-supply-chain-compromise-postmortem |
| `ghsa` | 2026-05-12T00:12:49Z | https://github.com/advisories/GHSA-g7cv-rxg3-hmpx |
| `osv` | 2026-05-12T00:12:49Z | https://osv.dev/vulnerability/GHSA-g7cv-rxg3-hmpx |
| `wiz` | 2026-05-12T11:00:00Z | https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised |
| `aikido` | 2026-05-12T00:00:00Z | https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised |
| `snyk` | 2026-05-11T00:00:00Z | https://snyk.io/blog/tanstack-npm-packages-compromised/ |
| `orca` | 2026-05-12T15:29:00Z | https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/ |
| `rescana` | 2026-05-12T00:00:00Z | https://www.rescana.com/post/tanstack-npm-supply-chain-attack-detailed-analysis-of-the-may-2026-github-actions-breach-and-multi-ecosystem-impact |
| `stepsecurity` | 2026-05-11T19:46:46Z | https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem |
| `safedep` | 2026-05-12T00:00:00Z | https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral |
| `socket` | 2026-05-11T20:00:00Z | https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack |

## Disagreements (package-level)

Coverage = listed by at least one of Wiz / Aikido / SafeDep but not all three.
Version-set = those sources that gave versions do not agree on the set.

| pid | kind | missing full-table sources |
|---|---|---|
| `npm:@beproduct/nestjs-auth` | version_set | — |
| `npm:@cap-js/db-service` | coverage | aikido, safedep |
| `npm:@cap-js/postgres` | coverage | aikido, safedep |
| `npm:@cap-js/sqlite` | coverage | aikido, safedep |
| `npm:@draftlab/db` | version_set | — |
| `npm:@mistralai/mistralai` | version_set | — |
| `npm:@mistralai/mistralai-azure` | version_set | — |
| `npm:@mistralai/mistralai-gcp` | version_set | — |
| `npm:@opensearch-project/opensearch` | version_set+coverage | aikido |
| `npm:@squawk/airport-data` | version_set | — |
| `npm:@squawk/airports` | version_set | — |
| `npm:@squawk/airspace` | version_set | — |
| `npm:@squawk/airspace-data` | version_set | — |
| `npm:@squawk/airway-data` | version_set | — |
| `npm:@squawk/airways` | version_set | — |
| `npm:@squawk/fix-data` | version_set | — |
| `npm:@squawk/fixes` | version_set | — |
| `npm:@squawk/flight-math` | version_set | — |
| `npm:@squawk/flightplan` | version_set | — |
| `npm:@squawk/geo` | version_set | — |
| `npm:@squawk/icao-registry` | version_set | — |
| `npm:@squawk/icao-registry-data` | version_set | — |
| `npm:@squawk/mcp` | version_set | — |
| `npm:@squawk/navaid-data` | version_set | — |
| `npm:@squawk/navaids` | version_set | — |
| `npm:@squawk/notams` | version_set | — |
| `npm:@squawk/procedure-data` | version_set | — |
| `npm:@squawk/procedures` | version_set | — |
| `npm:@squawk/types` | version_set | — |
| `npm:@squawk/units` | version_set | — |
| `npm:@squawk/weather` | version_set | — |
| `npm:@tanstack/eslint-plugin-router` | version_set | — |
| `npm:@tolka/cli` | version_set | — |
| `npm:cross-stitch` | version_set | — |
| `npm:git-branch-selector` | version_set | — |
| `npm:git-git-git` | version_set | — |
| `npm:guardrails-ai` | coverage | aikido, safedep |
| `npm:intercom-client` | coverage | aikido, safedep |
| `npm:lightning` | coverage | aikido, safedep |
| `npm:mbt` | coverage | aikido, safedep |
| `npm:mistralai` | coverage | aikido, safedep |
| `npm:nextmove-mcp` | version_set | — |
| `npm:ts-dna` | version_set | — |
| `npm:wot-api` | version_set | — |
| `pypi:guardrails-ai` | coverage | aikido |
| `pypi:mistralai` | coverage | aikido |

## Seed (`split=seed`)

| pid | vid | first_seen_utc | confidence | source ids |
|---|---|---|---|---|
| `npm:@tanstack/arktype-adapter` | `npm:@tanstack/arktype-adapter@1.166.12` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/arktype-adapter` | `npm:@tanstack/arktype-adapter@1.166.15` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/eslint-plugin-router` | `npm:@tanstack/eslint-plugin-router@1.161.9` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/eslint-plugin-router` | `npm:@tanstack/eslint-plugin-router@1.161.12` | 1778527574 | 0.95 | ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/eslint-plugin-start` | `npm:@tanstack/eslint-plugin-start@0.0.4` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/eslint-plugin-start` | `npm:@tanstack/eslint-plugin-start@0.0.7` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/history` | `npm:@tanstack/history@1.161.9` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/history` | `npm:@tanstack/history@1.161.12` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/nitro-v2-vite-plugin` | `npm:@tanstack/nitro-v2-vite-plugin@1.154.12` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/nitro-v2-vite-plugin` | `npm:@tanstack/nitro-v2-vite-plugin@1.154.15` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-router` | `npm:@tanstack/react-router@1.169.5` | 1778527239 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, socket, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-router` | `npm:@tanstack/react-router@1.169.8` | 1778527574 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, socket, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-router-devtools` | `npm:@tanstack/react-router-devtools@1.166.16` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-router-devtools` | `npm:@tanstack/react-router-devtools@1.166.19` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-router-ssr-query` | `npm:@tanstack/react-router-ssr-query@1.166.15` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-router-ssr-query` | `npm:@tanstack/react-router-ssr-query@1.166.18` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-start` | `npm:@tanstack/react-start@1.167.68` | 1778527239 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-start` | `npm:@tanstack/react-start@1.167.71` | 1778527574 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-start-client` | `npm:@tanstack/react-start-client@1.166.51` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-start-client` | `npm:@tanstack/react-start-client@1.166.54` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-start-rsc` | `npm:@tanstack/react-start-rsc@0.0.47` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-start-rsc` | `npm:@tanstack/react-start-rsc@0.0.50` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-start-server` | `npm:@tanstack/react-start-server@1.166.55` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/react-start-server` | `npm:@tanstack/react-start-server@1.166.58` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-cli` | `npm:@tanstack/router-cli@1.166.46` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-cli` | `npm:@tanstack/router-cli@1.166.49` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-core` | `npm:@tanstack/router-core@1.169.5` | 1778527239 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-core` | `npm:@tanstack/router-core@1.169.8` | 1778527574 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-devtools` | `npm:@tanstack/router-devtools@1.166.16` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-devtools` | `npm:@tanstack/router-devtools@1.166.19` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-devtools-core` | `npm:@tanstack/router-devtools-core@1.167.6` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-devtools-core` | `npm:@tanstack/router-devtools-core@1.167.9` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-generator` | `npm:@tanstack/router-generator@1.166.45` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-generator` | `npm:@tanstack/router-generator@1.166.48` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-plugin` | `npm:@tanstack/router-plugin@1.167.38` | 1778527239 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-plugin` | `npm:@tanstack/router-plugin@1.167.41` | 1778527574 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-ssr-query-core` | `npm:@tanstack/router-ssr-query-core@1.168.3` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-ssr-query-core` | `npm:@tanstack/router-ssr-query-core@1.168.6` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-utils` | `npm:@tanstack/router-utils@1.161.11` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-utils` | `npm:@tanstack/router-utils@1.161.14` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-vite-plugin` | `npm:@tanstack/router-vite-plugin@1.166.53` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/router-vite-plugin` | `npm:@tanstack/router-vite-plugin@1.166.56` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-router` | `npm:@tanstack/solid-router@1.169.5` | 1778527239 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-router` | `npm:@tanstack/solid-router@1.169.8` | 1778527574 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-router-devtools` | `npm:@tanstack/solid-router-devtools@1.166.16` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-router-devtools` | `npm:@tanstack/solid-router-devtools@1.166.19` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-router-ssr-query` | `npm:@tanstack/solid-router-ssr-query@1.166.15` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-router-ssr-query` | `npm:@tanstack/solid-router-ssr-query@1.166.18` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-start` | `npm:@tanstack/solid-start@1.167.65` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-start` | `npm:@tanstack/solid-start@1.167.68` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-start-client` | `npm:@tanstack/solid-start-client@1.166.50` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-start-client` | `npm:@tanstack/solid-start-client@1.166.53` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-start-server` | `npm:@tanstack/solid-start-server@1.166.54` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/solid-start-server` | `npm:@tanstack/solid-start-server@1.166.57` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-client-core` | `npm:@tanstack/start-client-core@1.168.5` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-client-core` | `npm:@tanstack/start-client-core@1.168.8` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-fn-stubs` | `npm:@tanstack/start-fn-stubs@1.161.9` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-fn-stubs` | `npm:@tanstack/start-fn-stubs@1.161.12` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-plugin-core` | `npm:@tanstack/start-plugin-core@1.169.23` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-plugin-core` | `npm:@tanstack/start-plugin-core@1.169.26` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-server-core` | `npm:@tanstack/start-server-core@1.167.33` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-server-core` | `npm:@tanstack/start-server-core@1.167.36` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-static-server-functions` | `npm:@tanstack/start-static-server-functions@1.166.44` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-static-server-functions` | `npm:@tanstack/start-static-server-functions@1.166.47` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-storage-context` | `npm:@tanstack/start-storage-context@1.166.38` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/start-storage-context` | `npm:@tanstack/start-storage-context@1.166.41` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/valibot-adapter` | `npm:@tanstack/valibot-adapter@1.166.12` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/valibot-adapter` | `npm:@tanstack/valibot-adapter@1.166.15` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/virtual-file-routes` | `npm:@tanstack/virtual-file-routes@1.161.10` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/virtual-file-routes` | `npm:@tanstack/virtual-file-routes@1.161.13` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-router` | `npm:@tanstack/vue-router@1.169.5` | 1778527239 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-router` | `npm:@tanstack/vue-router@1.169.8` | 1778527574 | 0.95 | aikido, ghsa, osv, rescana, safedep, snyk, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-router-devtools` | `npm:@tanstack/vue-router-devtools@1.166.16` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-router-devtools` | `npm:@tanstack/vue-router-devtools@1.166.19` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-router-ssr-query` | `npm:@tanstack/vue-router-ssr-query@1.166.15` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-router-ssr-query` | `npm:@tanstack/vue-router-ssr-query@1.166.18` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-start` | `npm:@tanstack/vue-start@1.167.61` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-start` | `npm:@tanstack/vue-start@1.167.64` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-start-client` | `npm:@tanstack/vue-start-client@1.166.46` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-start-client` | `npm:@tanstack/vue-start-client@1.166.49` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-start-server` | `npm:@tanstack/vue-start-server@1.166.50` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/vue-start-server` | `npm:@tanstack/vue-start-server@1.166.53` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/zod-adapter` | `npm:@tanstack/zod-adapter@1.166.12` | 1778527239 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |
| `npm:@tanstack/zod-adapter` | `npm:@tanstack/zod-adapter@1.166.15` | 1778527574 | 0.95 | aikido, ghsa, osv, safedep, stepsecurity, tanstack_postmortem, wiz |

### Seed timestamp note

Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one.

## Validation (`split=validation`)

| pid | vid | first_seen_utc | confidence | source ids | first_seen note |
|---|---|---|---|---|---|
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.8` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.9` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.10` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.11` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.12` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.13` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.14` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.15` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.16` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.17` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.18` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@beproduct/nestjs-auth` | `npm:@beproduct/nestjs-auth@0.1.19` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@cap-js/db-service` | `npm:@cap-js/db-service@2.10.1` | 1778583600 | 0.45 | wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@cap-js/postgres` | `npm:@cap-js/postgres@2.2.2` | 1778583600 | 0.45 | wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@cap-js/sqlite` | `npm:@cap-js/sqlite@2.2.2` | 1778583600 | 0.45 | wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@dirigible-ai/sdk` | `npm:@dirigible-ai/sdk@0.6.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@dirigible-ai/sdk` | `npm:@dirigible-ai/sdk@0.6.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftauth/client` | `npm:@draftauth/client@0.2.1` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftauth/client` | `npm:@draftauth/client@0.2.2` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftauth/core` | `npm:@draftauth/core@0.13.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftauth/core` | `npm:@draftauth/core@0.13.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftlab/auth` | `npm:@draftlab/auth@0.24.1` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftlab/auth` | `npm:@draftlab/auth@0.24.2` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftlab/auth-router` | `npm:@draftlab/auth-router@0.5.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftlab/auth-router` | `npm:@draftlab/auth-router@0.5.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftlab/db` | `npm:@draftlab/db@0.16.1` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@draftlab/db` | `npm:@draftlab/db@0.16.2` | 1778528806 | 0.90 | safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mesadev/rest` | `npm:@mesadev/rest@0.28.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mesadev/saguaro` | `npm:@mesadev/saguaro@0.4.22` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mesadev/sdk` | `npm:@mesadev/sdk@0.28.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai` | `npm:@mistralai/mistralai@2.2.2` | 1778457600 | 0.95 | aikido, rescana, safedep, snyk, wiz | Earliest citing source published_utc: snyk (2026-05-11T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai` | `npm:@mistralai/mistralai@2.2.3` | 1778457600 | 0.95 | aikido, rescana, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: snyk (2026-05-11T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai` | `npm:@mistralai/mistralai@2.2.4` | 1778457600 | 0.95 | aikido, rescana, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: snyk (2026-05-11T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai-azure` | `npm:@mistralai/mistralai-azure@1.7.1` | 1778544000 | 0.90 | aikido, rescana, safedep, snyk, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai-azure` | `npm:@mistralai/mistralai-azure@1.7.2` | 1778528806 | 0.95 | aikido, rescana, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai-azure` | `npm:@mistralai/mistralai-azure@1.7.3` | 1778528806 | 0.95 | aikido, rescana, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai-gcp` | `npm:@mistralai/mistralai-gcp@1.7.1` | 1778544000 | 0.90 | aikido, rescana, safedep, snyk, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai-gcp` | `npm:@mistralai/mistralai-gcp@1.7.2` | 1778528806 | 0.95 | aikido, rescana, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@mistralai/mistralai-gcp` | `npm:@mistralai/mistralai-gcp@1.7.3` | 1778528806 | 0.95 | aikido, rescana, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@ml-toolkit-ts/preprocessing` | `npm:@ml-toolkit-ts/preprocessing@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@ml-toolkit-ts/preprocessing` | `npm:@ml-toolkit-ts/preprocessing@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@ml-toolkit-ts/xgboost` | `npm:@ml-toolkit-ts/xgboost@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@ml-toolkit-ts/xgboost` | `npm:@ml-toolkit-ts/xgboost@1.0.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@opensearch-project/opensearch` | `npm:@opensearch-project/opensearch@3.5.3` | 1778529600 | 0.90 | orca, safedep, socket, wiz | Earliest citing source published_utc: socket (2026-05-11T20:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@opensearch-project/opensearch` | `npm:@opensearch-project/opensearch@3.6.2` | 1778528806 | 0.95 | orca, safedep, socket, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@opensearch-project/opensearch` | `npm:@opensearch-project/opensearch@3.7.0` | 1778529600 | 0.90 | orca, safedep, socket, wiz | Earliest citing source published_utc: socket (2026-05-11T20:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@opensearch-project/opensearch` | `npm:@opensearch-project/opensearch@3.8.0` | 1778529600 | 0.90 | orca, safedep, socket, wiz | Earliest citing source published_utc: socket (2026-05-11T20:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airport-data` | `npm:@squawk/airport-data@0.7.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airport-data` | `npm:@squawk/airport-data@0.7.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airport-data` | `npm:@squawk/airport-data@0.7.6` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airport-data` | `npm:@squawk/airport-data@0.7.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airport-data` | `npm:@squawk/airport-data@0.7.8` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airports` | `npm:@squawk/airports@0.6.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airports` | `npm:@squawk/airports@0.6.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airports` | `npm:@squawk/airports@0.6.4` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airports` | `npm:@squawk/airports@0.6.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airports` | `npm:@squawk/airports@0.6.6` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace` | `npm:@squawk/airspace@0.8.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace` | `npm:@squawk/airspace@0.8.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace` | `npm:@squawk/airspace@0.8.3` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace` | `npm:@squawk/airspace@0.8.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace` | `npm:@squawk/airspace@0.8.5` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace-data` | `npm:@squawk/airspace-data@0.5.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace-data` | `npm:@squawk/airspace-data@0.5.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace-data` | `npm:@squawk/airspace-data@0.5.5` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace-data` | `npm:@squawk/airspace-data@0.5.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airspace-data` | `npm:@squawk/airspace-data@0.5.7` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airway-data` | `npm:@squawk/airway-data@0.5.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airway-data` | `npm:@squawk/airway-data@0.5.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airway-data` | `npm:@squawk/airway-data@0.5.6` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airway-data` | `npm:@squawk/airway-data@0.5.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airway-data` | `npm:@squawk/airway-data@0.5.8` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airways` | `npm:@squawk/airways@0.4.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airways` | `npm:@squawk/airways@0.4.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airways` | `npm:@squawk/airways@0.4.4` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airways` | `npm:@squawk/airways@0.4.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/airways` | `npm:@squawk/airways@0.4.6` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fix-data` | `npm:@squawk/fix-data@0.6.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fix-data` | `npm:@squawk/fix-data@0.6.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fix-data` | `npm:@squawk/fix-data@0.6.6` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fix-data` | `npm:@squawk/fix-data@0.6.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fix-data` | `npm:@squawk/fix-data@0.6.8` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fixes` | `npm:@squawk/fixes@0.3.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fixes` | `npm:@squawk/fixes@0.3.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fixes` | `npm:@squawk/fixes@0.3.4` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fixes` | `npm:@squawk/fixes@0.3.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/fixes` | `npm:@squawk/fixes@0.3.6` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flight-math` | `npm:@squawk/flight-math@0.5.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flight-math` | `npm:@squawk/flight-math@0.5.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flight-math` | `npm:@squawk/flight-math@0.5.6` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flight-math` | `npm:@squawk/flight-math@0.5.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flight-math` | `npm:@squawk/flight-math@0.5.8` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flightplan` | `npm:@squawk/flightplan@0.5.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flightplan` | `npm:@squawk/flightplan@0.5.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flightplan` | `npm:@squawk/flightplan@0.5.4` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flightplan` | `npm:@squawk/flightplan@0.5.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/flightplan` | `npm:@squawk/flightplan@0.5.6` | 1778529600 | 0.90 | safedep, socket, wiz | Earliest citing source published_utc: socket (2026-05-11T20:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/geo` | `npm:@squawk/geo@0.4.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/geo` | `npm:@squawk/geo@0.4.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/geo` | `npm:@squawk/geo@0.4.6` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/geo` | `npm:@squawk/geo@0.4.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/geo` | `npm:@squawk/geo@0.4.8` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry` | `npm:@squawk/icao-registry@0.5.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry` | `npm:@squawk/icao-registry@0.5.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry` | `npm:@squawk/icao-registry@0.5.4` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry` | `npm:@squawk/icao-registry@0.5.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry` | `npm:@squawk/icao-registry@0.5.6` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry-data` | `npm:@squawk/icao-registry-data@0.8.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry-data` | `npm:@squawk/icao-registry-data@0.8.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry-data` | `npm:@squawk/icao-registry-data@0.8.6` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry-data` | `npm:@squawk/icao-registry-data@0.8.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/icao-registry-data` | `npm:@squawk/icao-registry-data@0.8.8` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/mcp` | `npm:@squawk/mcp@0.9.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/mcp` | `npm:@squawk/mcp@0.9.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/mcp` | `npm:@squawk/mcp@0.9.3` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/mcp` | `npm:@squawk/mcp@0.9.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/mcp` | `npm:@squawk/mcp@0.9.5` | 1778529600 | 0.90 | safedep, socket, wiz | Earliest citing source published_utc: socket (2026-05-11T20:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaid-data` | `npm:@squawk/navaid-data@0.6.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaid-data` | `npm:@squawk/navaid-data@0.6.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaid-data` | `npm:@squawk/navaid-data@0.6.6` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaid-data` | `npm:@squawk/navaid-data@0.6.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaid-data` | `npm:@squawk/navaid-data@0.6.8` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaids` | `npm:@squawk/navaids@0.4.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaids` | `npm:@squawk/navaids@0.4.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaids` | `npm:@squawk/navaids@0.4.4` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaids` | `npm:@squawk/navaids@0.4.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/navaids` | `npm:@squawk/navaids@0.4.6` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/notams` | `npm:@squawk/notams@0.3.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/notams` | `npm:@squawk/notams@0.3.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/notams` | `npm:@squawk/notams@0.3.8` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/notams` | `npm:@squawk/notams@0.3.9` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/notams` | `npm:@squawk/notams@0.3.10` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedure-data` | `npm:@squawk/procedure-data@0.7.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedure-data` | `npm:@squawk/procedure-data@0.7.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedure-data` | `npm:@squawk/procedure-data@0.7.5` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedure-data` | `npm:@squawk/procedure-data@0.7.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedure-data` | `npm:@squawk/procedure-data@0.7.7` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedures` | `npm:@squawk/procedures@0.5.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedures` | `npm:@squawk/procedures@0.5.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedures` | `npm:@squawk/procedures@0.5.4` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedures` | `npm:@squawk/procedures@0.5.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/procedures` | `npm:@squawk/procedures@0.5.6` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/types` | `npm:@squawk/types@0.8.1` | 1778528806 | 0.90 | safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/types` | `npm:@squawk/types@0.8.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/types` | `npm:@squawk/types@0.8.3` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/types` | `npm:@squawk/types@0.8.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/types` | `npm:@squawk/types@0.8.5` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/units` | `npm:@squawk/units@0.4.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/units` | `npm:@squawk/units@0.4.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/units` | `npm:@squawk/units@0.4.5` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/units` | `npm:@squawk/units@0.4.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/units` | `npm:@squawk/units@0.4.7` | 1778544000 | 0.75 | safedep, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/weather` | `npm:@squawk/weather@0.5.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/weather` | `npm:@squawk/weather@0.5.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/weather` | `npm:@squawk/weather@0.5.8` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/weather` | `npm:@squawk/weather@0.5.9` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@squawk/weather` | `npm:@squawk/weather@0.5.10` | 1778529600 | 0.90 | safedep, socket, wiz | Earliest citing source published_utc: socket (2026-05-11T20:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/cli` | `npm:@supersurkhet/cli@0.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/cli` | `npm:@supersurkhet/cli@0.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/cli` | `npm:@supersurkhet/cli@0.0.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/cli` | `npm:@supersurkhet/cli@0.0.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/cli` | `npm:@supersurkhet/cli@0.0.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/cli` | `npm:@supersurkhet/cli@0.0.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/sdk` | `npm:@supersurkhet/sdk@0.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/sdk` | `npm:@supersurkhet/sdk@0.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/sdk` | `npm:@supersurkhet/sdk@0.0.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/sdk` | `npm:@supersurkhet/sdk@0.0.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/sdk` | `npm:@supersurkhet/sdk@0.0.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@supersurkhet/sdk` | `npm:@supersurkhet/sdk@0.0.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/components` | `npm:@tallyui/components@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/components` | `npm:@tallyui/components@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/components` | `npm:@tallyui/components@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-medusa` | `npm:@tallyui/connector-medusa@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-medusa` | `npm:@tallyui/connector-medusa@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-medusa` | `npm:@tallyui/connector-medusa@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-shopify` | `npm:@tallyui/connector-shopify@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-shopify` | `npm:@tallyui/connector-shopify@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-shopify` | `npm:@tallyui/connector-shopify@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-vendure` | `npm:@tallyui/connector-vendure@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-vendure` | `npm:@tallyui/connector-vendure@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-vendure` | `npm:@tallyui/connector-vendure@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-woocommerce` | `npm:@tallyui/connector-woocommerce@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-woocommerce` | `npm:@tallyui/connector-woocommerce@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/connector-woocommerce` | `npm:@tallyui/connector-woocommerce@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/core` | `npm:@tallyui/core@0.2.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/core` | `npm:@tallyui/core@0.2.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/core` | `npm:@tallyui/core@0.2.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/database` | `npm:@tallyui/database@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/database` | `npm:@tallyui/database@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/database` | `npm:@tallyui/database@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/pos` | `npm:@tallyui/pos@0.1.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/pos` | `npm:@tallyui/pos@0.1.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/pos` | `npm:@tallyui/pos@0.1.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/storage-sqlite` | `npm:@tallyui/storage-sqlite@0.2.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/storage-sqlite` | `npm:@tallyui/storage-sqlite@0.2.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/storage-sqlite` | `npm:@tallyui/storage-sqlite@0.2.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/theme` | `npm:@tallyui/theme@0.2.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/theme` | `npm:@tallyui/theme@0.2.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tallyui/theme` | `npm:@tallyui/theme@0.2.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@taskflow-corp/cli` | `npm:@taskflow-corp/cli@0.1.24` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@taskflow-corp/cli` | `npm:@taskflow-corp/cli@0.1.25` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@taskflow-corp/cli` | `npm:@taskflow-corp/cli@0.1.26` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@taskflow-corp/cli` | `npm:@taskflow-corp/cli@0.1.27` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@taskflow-corp/cli` | `npm:@taskflow-corp/cli@0.1.28` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@taskflow-corp/cli` | `npm:@taskflow-corp/cli@0.1.29` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tolka/cli` | `npm:@tolka/cli@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tolka/cli` | `npm:@tolka/cli@1.0.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tolka/cli` | `npm:@tolka/cli@1.0.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tolka/cli` | `npm:@tolka/cli@1.0.5` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@tolka/cli` | `npm:@tolka/cli@1.0.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/access-policy-sdk` | `npm:@uipath/access-policy-sdk@0.3.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/access-policy-tool` | `npm:@uipath/access-policy-tool@0.3.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/admin-tool` | `npm:@uipath/admin-tool@0.1.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/agent-sdk` | `npm:@uipath/agent-sdk@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/agent-tool` | `npm:@uipath/agent-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/agent.sdk` | `npm:@uipath/agent.sdk@0.0.18` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/aops-policy-tool` | `npm:@uipath/aops-policy-tool@0.3.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/ap-chat` | `npm:@uipath/ap-chat@1.5.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/api-workflow-tool` | `npm:@uipath/api-workflow-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/apollo-core` | `npm:@uipath/apollo-core@5.9.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/apollo-react` | `npm:@uipath/apollo-react@4.24.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/apollo-wind` | `npm:@uipath/apollo-wind@2.16.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/auth` | `npm:@uipath/auth@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/case-tool` | `npm:@uipath/case-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/cli` | `npm:@uipath/cli@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/codedagent-tool` | `npm:@uipath/codedagent-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/codedagents-tool` | `npm:@uipath/codedagents-tool@0.1.12` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/codedapp-tool` | `npm:@uipath/codedapp-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/common` | `npm:@uipath/common@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/context-grounding-tool` | `npm:@uipath/context-grounding-tool@0.1.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/data-fabric-tool` | `npm:@uipath/data-fabric-tool@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/docsai-tool` | `npm:@uipath/docsai-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/filesystem` | `npm:@uipath/filesystem@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/flow-tool` | `npm:@uipath/flow-tool@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/functions-tool` | `npm:@uipath/functions-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/gov-tool` | `npm:@uipath/gov-tool@0.3.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/identity-tool` | `npm:@uipath/identity-tool@0.1.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/insights-sdk` | `npm:@uipath/insights-sdk@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/insights-tool` | `npm:@uipath/insights-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/integrationservice-sdk` | `npm:@uipath/integrationservice-sdk@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/integrationservice-tool` | `npm:@uipath/integrationservice-tool@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/llmgw-tool` | `npm:@uipath/llmgw-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/maestro-sdk` | `npm:@uipath/maestro-sdk@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/maestro-tool` | `npm:@uipath/maestro-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/orchestrator-tool` | `npm:@uipath/orchestrator-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-apiworkflow` | `npm:@uipath/packager-tool-apiworkflow@0.0.19` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-bpmn` | `npm:@uipath/packager-tool-bpmn@0.0.9` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-case` | `npm:@uipath/packager-tool-case@0.0.9` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-connector` | `npm:@uipath/packager-tool-connector@0.0.19` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-flow` | `npm:@uipath/packager-tool-flow@0.0.19` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-functions` | `npm:@uipath/packager-tool-functions@0.1.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-webapp` | `npm:@uipath/packager-tool-webapp@1.0.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-workflowcompiler` | `npm:@uipath/packager-tool-workflowcompiler@0.0.16` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/packager-tool-workflowcompiler-browser` | `npm:@uipath/packager-tool-workflowcompiler-browser@0.0.34` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/platform-tool` | `npm:@uipath/platform-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/project-packager` | `npm:@uipath/project-packager@1.1.16` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/resource-tool` | `npm:@uipath/resource-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/resourcecatalog-tool` | `npm:@uipath/resourcecatalog-tool@0.1.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/resources-tool` | `npm:@uipath/resources-tool@0.1.11` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/robot` | `npm:@uipath/robot@1.3.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/rpa-legacy-tool` | `npm:@uipath/rpa-legacy-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/rpa-tool` | `npm:@uipath/rpa-tool@0.9.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/solution-packager` | `npm:@uipath/solution-packager@0.0.35` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/solution-tool` | `npm:@uipath/solution-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/solutionpackager-sdk` | `npm:@uipath/solutionpackager-sdk@1.0.11` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/solutionpackager-tool-core` | `npm:@uipath/solutionpackager-tool-core@0.0.34` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/tasks-tool` | `npm:@uipath/tasks-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/telemetry` | `npm:@uipath/telemetry@0.0.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/test-manager-tool` | `npm:@uipath/test-manager-tool@1.0.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/tool-workflowcompiler` | `npm:@uipath/tool-workflowcompiler@0.0.12` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/traces-tool` | `npm:@uipath/traces-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/ui-widgets-multi-file-upload` | `npm:@uipath/ui-widgets-multi-file-upload@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/uipath-python-bridge` | `npm:@uipath/uipath-python-bridge@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/vertical-solutions-tool` | `npm:@uipath/vertical-solutions-tool@1.0.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/vss` | `npm:@uipath/vss@0.1.6` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:@uipath/widget.sdk` | `npm:@uipath/widget.sdk@1.2.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:agentwork-cli` | `npm:agentwork-cli@0.1.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:agentwork-cli` | `npm:agentwork-cli@0.1.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cmux-agent-mcp` | `npm:cmux-agent-mcp@0.1.3` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cmux-agent-mcp` | `npm:cmux-agent-mcp@0.1.4` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cmux-agent-mcp` | `npm:cmux-agent-mcp@0.1.5` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cmux-agent-mcp` | `npm:cmux-agent-mcp@0.1.6` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cmux-agent-mcp` | `npm:cmux-agent-mcp@0.1.7` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cmux-agent-mcp` | `npm:cmux-agent-mcp@0.1.8` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cross-stitch` | `npm:cross-stitch@1.1.3` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cross-stitch` | `npm:cross-stitch@1.1.4` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cross-stitch` | `npm:cross-stitch@1.1.5` | 1778544000 | 0.90 | aikido, safedep, snyk, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cross-stitch` | `npm:cross-stitch@1.1.6` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:cross-stitch` | `npm:cross-stitch@1.1.7` | 1778544000 | 0.75 | safedep, snyk, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-branch-selector` | `npm:git-branch-selector@1.3.3` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-branch-selector` | `npm:git-branch-selector@1.3.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-branch-selector` | `npm:git-branch-selector@1.3.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-branch-selector` | `npm:git-branch-selector@1.3.6` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-branch-selector` | `npm:git-branch-selector@1.3.7` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-git-git` | `npm:git-git-git@1.0.8` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-git-git` | `npm:git-git-git@1.0.9` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-git-git` | `npm:git-git-git@1.0.10` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-git-git` | `npm:git-git-git@1.0.11` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:git-git-git` | `npm:git-git-git@1.0.12` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:guardrails-ai` | `npm:guardrails-ai@0.10.1` | 1778583600 | 0.45 | wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:intercom-client` | `npm:intercom-client@7.0.4` | 1778583600 | 0.60 | orca, rescana, wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:lightning` | `npm:lightning@2.6.2` | 1778583600 | 0.45 | orca, wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:lightning` | `npm:lightning@2.6.3` | 1778583600 | 0.45 | orca, wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:mbt` | `npm:mbt@1.2.48` | 1778583600 | 0.45 | wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:mistralai` | `npm:mistralai@2.4.6` | 1778583600 | 0.45 | wiz | Earliest citing source published_utc: wiz (2026-05-12T11:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:ml-toolkit-ts` | `npm:ml-toolkit-ts@1.0.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:ml-toolkit-ts` | `npm:ml-toolkit-ts@1.0.5` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:nextmove-mcp` | `npm:nextmove-mcp@0.1.3` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:nextmove-mcp` | `npm:nextmove-mcp@0.1.4` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:nextmove-mcp` | `npm:nextmove-mcp@0.1.5` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:nextmove-mcp` | `npm:nextmove-mcp@0.1.6` | 1778544000 | 0.90 | aikido, safedep, snyk, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:nextmove-mcp` | `npm:nextmove-mcp@0.1.7` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:safe-action` | `npm:safe-action@0.8.3` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:safe-action` | `npm:safe-action@0.8.4` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:ts-dna` | `npm:ts-dna@3.0.1` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:ts-dna` | `npm:ts-dna@3.0.2` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:ts-dna` | `npm:ts-dna@3.0.3` | 1778544000 | 0.90 | aikido, safedep, snyk, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:ts-dna` | `npm:ts-dna@3.0.4` | 1778528806 | 0.95 | aikido, safedep, snyk, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:ts-dna` | `npm:ts-dna@3.0.5` | 1778544000 | 0.75 | safedep, snyk, wiz | Earliest citing source published_utc: safedep (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:wot-api` | `npm:wot-api@0.8.1` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:wot-api` | `npm:wot-api@0.8.2` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:wot-api` | `npm:wot-api@0.8.3` | 1778544000 | 0.90 | aikido, safedep, wiz | Earliest citing source published_utc: aikido (2026-05-12T00:00:00Z). Not the npm/PyPI publish time — vendors did not give one. |
| `npm:wot-api` | `npm:wot-api@0.8.4` | 1778528806 | 0.95 | aikido, safedep, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `pypi:guardrails-ai` | `pypi:guardrails-ai@0.10.1` | 1778528806 | 0.95 | orca, rescana, safedep, socket, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
| `pypi:mistralai` | `pypi:mistralai@2.4.6` | 1778528806 | 0.95 | orca, safedep, socket, stepsecurity, wiz | Earliest citing source published_utc: stepsecurity (2026-05-11T19:46:46Z). Not the npm/PyPI publish time — vendors did not give one. |
