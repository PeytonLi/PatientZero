"""Vendor IOC listings for the May 11 2026 Mini Shai-Hulud / TanStack worm.

Each listing is a TSV of: ecosystem, name, versions (comma-separated).
A package with no versions still counts as a listing (namespace-level name).
This module is the editable source; `ioc_reconcile.py --build-sources`
writes the checked-in `artifacts/ioc_sources.json`.
"""
from __future__ import annotations

SOURCE_CATALOG: dict[str, dict] = {
    "tanstack_postmortem": {
        "url": "https://tanstack.com/blog/npm-supply-chain-compromise-postmortem",
        "published_utc": "2026-05-11T21:00:00Z",
        "title": "Postmortem: TanStack npm supply-chain compromise",
        "notes": (
            "Names 42 @tanstack/* packages, 84 versions, published 19:20:39 and "
            "19:26:14 UTC. Defers the full table to GHSA-g7cv-rxg3-hmpx. "
            "Confirmed-clean: query*, table*, form*, virtual*, store, and the "
            "@tanstack/start meta-package."
        ),
    },
    "ghsa": {
        "url": "https://github.com/advisories/GHSA-g7cv-rxg3-hmpx",
        "published_utc": "2026-05-12T00:12:49Z",
        "title": "GHSA-g7cv-rxg3-hmpx / CVE-2026-45321",
        "notes": "Machine-readable affected products: 42 packages, 84 versions.",
    },
    "osv": {
        "url": "https://osv.dev/vulnerability/GHSA-g7cv-rxg3-hmpx",
        "published_utc": "2026-05-12T00:12:49Z",
        "title": "OSV GHSA-g7cv-rxg3-hmpx",
        "notes": "Same affected set as GHSA. Per-package MAL-* records also exist.",
    },
    "wiz": {
        "url": "https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised",
        "published_utc": "2026-05-12T11:00:00Z",
        "title": "Mini Shai-Hulud Strikes Again (Wiz)",
        "notes": "Full versioned table. Updated 2026-05-12 11:00 UTC and 2026-05-13 02:30 UTC. Includes PyPI.",
    },
    "aikido": {
        "url": "https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised",
        "published_utc": "2026-05-12T00:00:00Z",
        "title": "Mini Shai-Hulud Is Back (Aikido)",
        "notes": "Claims 169 npm names / 373 versions. Appendix is npm-only; no PyPI rows.",
    },
    "snyk": {
        "url": "https://snyk.io/blog/tanstack-npm-packages-compromised/",
        "published_utc": "2026-05-11T00:00:00Z",
        "title": "TanStack npm packages compromised (Snyk)",
        "notes": "Partial explicit table (6 TanStack packages) plus namespace mentions. Claims 170+ in Snyk DB.",
    },
    "orca": {
        "url": "https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/",
        "published_utc": "2026-05-12T15:29:00Z",
        "title": "TanStack and 160+ npm/PyPI packages (Orca)",
        "notes": "Namespace-level scope plus explicit PyPI guardrails-ai@0.10.1 and mistralai@2.4.6.",
    },
    "rescana": {
        "url": "https://www.rescana.com/post/tanstack-npm-supply-chain-attack-detailed-analysis-of-the-may-2026-github-actions-breach-and-multi-ecosystem-impact",
        "published_utc": "2026-05-12T00:00:00Z",
        "title": "TanStack npm supply chain attack (Rescana)",
        "notes": "Secondary source synthesizing TanStack/Snyk/Orca. Partial explicit names.",
    },
    "stepsecurity": {
        "url": "https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem",
        "published_utc": "2026-05-11T19:46:46Z",
        "title": "Mini Shai-Hulud is back (StepSecurity)",
        "notes": "First public detection (issue #7383 at 19:46:46). Blog table grew past the initial 14 packages.",
    },
    "safedep": {
        "url": "https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral",
        "published_utc": "2026-05-12T00:00:00Z",
        "title": "Mass supply chain attack (SafeDep)",
        "notes": "Versioned tables: 170 npm + 2 PyPI = 172 packages, 404 versions.",
    },
    "socket": {
        "url": "https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack",
        "published_utc": "2026-05-11T20:00:00Z",
        "title": "TanStack npm packages compromised (Socket)",
        "notes": "Flagged TanStack artifacts within 6 minutes of publish. PyPI update 2026-05-12 03:05:38 UTC.",
    },
}

# First malicious publish batches (TanStack postmortem, local GitHub/npm timestamps).
SEED_BATCH1_UTC = "2026-05-11T19:20:39Z"
SEED_BATCH2_UTC = "2026-05-11T19:26:14Z"

# TSV: ecosystem \t name \t versions
# GHSA/OSV seed versions are loaded from data/truth/raw at build time.

WIZ = """
npm	@beproduct/nestjs-auth	0.1.2,0.1.3,0.1.4,0.1.5,0.1.6,0.1.7,0.1.8,0.1.9,0.1.10,0.1.11,0.1.12,0.1.13,0.1.14,0.1.15,0.1.16,0.1.17,0.1.18,0.1.19
npm	@cap-js/db-service	2.10.1
npm	@cap-js/postgres	2.2.2
npm	@cap-js/sqlite	2.2.2
npm	@dirigible-ai/sdk	0.6.2,0.6.3
npm	@draftauth/client	0.2.1,0.2.2
npm	@draftauth/core	0.13.1,0.13.2
npm	@draftlab/auth	0.24.1,0.24.2
npm	@draftlab/auth-router	0.5.1,0.5.2
npm	@draftlab/db	0.16.1,0.16.2
npm	@mesadev/rest	0.28.3
npm	@mesadev/saguaro	0.4.22
npm	@mesadev/sdk	0.28.3
npm	@mistralai/mistralai	2.2.2,2.2.3,2.2.4
npm	@mistralai/mistralai-azure	1.7.1,1.7.2,1.7.3
npm	@mistralai/mistralai-gcp	1.7.1,1.7.2,1.7.3
npm	@ml-toolkit-ts/preprocessing	1.0.2,1.0.3
npm	@ml-toolkit-ts/xgboost	1.0.3,1.0.4
npm	@opensearch-project/opensearch	3.5.3,3.6.2,3.7.0,3.8.0
npm	@squawk/airport-data	0.7.4,0.7.5,0.7.6,0.7.7,0.7.8
npm	@squawk/airports	0.6.2,0.6.3,0.6.4,0.6.5,0.6.6
npm	@squawk/airspace	0.8.1,0.8.2,0.8.3,0.8.4,0.8.5
npm	@squawk/airspace-data	0.5.3,0.5.4,0.5.5,0.5.6,0.5.7
npm	@squawk/airway-data	0.5.4,0.5.5,0.5.6,0.5.7,0.5.8
npm	@squawk/airways	0.4.2,0.4.3,0.4.4,0.4.5,0.4.6
npm	@squawk/fix-data	0.6.4,0.6.5,0.6.6,0.6.7,0.6.8
npm	@squawk/fixes	0.3.2,0.3.3,0.3.4,0.3.5,0.3.6
npm	@squawk/flight-math	0.5.4,0.5.5,0.5.6,0.5.7,0.5.8
npm	@squawk/flightplan	0.5.2,0.5.3,0.5.4,0.5.5,0.5.6
npm	@squawk/geo	0.4.4,0.4.5,0.4.6,0.4.7,0.4.8
npm	@squawk/icao-registry	0.5.2,0.5.3,0.5.4,0.5.5,0.5.6
npm	@squawk/icao-registry-data	0.8.4,0.8.5,0.8.6,0.8.7,0.8.8
npm	@squawk/mcp	0.9.1,0.9.2,0.9.3,0.9.4,0.9.5
npm	@squawk/navaid-data	0.6.4,0.6.5,0.6.6,0.6.7,0.6.8
npm	@squawk/navaids	0.4.2,0.4.3,0.4.4,0.4.5,0.4.6
npm	@squawk/notams	0.3.6,0.3.7,0.3.8,0.3.9,0.3.10
npm	@squawk/procedure-data	0.7.3,0.7.4,0.7.5,0.7.6,0.7.7
npm	@squawk/procedures	0.5.2,0.5.3,0.5.4,0.5.5,0.5.6
npm	@squawk/types	0.8.1,0.8.2,0.8.3,0.8.4,0.8.5
npm	@squawk/units	0.4.3,0.4.4,0.4.5,0.4.6,0.4.7
npm	@squawk/weather	0.5.6,0.5.7,0.5.8,0.5.9,0.5.10
npm	@supersurkhet/cli	0.0.2,0.0.3,0.0.4,0.0.5,0.0.6,0.0.7
npm	@supersurkhet/sdk	0.0.2,0.0.3,0.0.4,0.0.5,0.0.6,0.0.7
npm	@tallyui/components	1.0.1,1.0.2,1.0.3
npm	@tallyui/connector-medusa	1.0.1,1.0.2,1.0.3
npm	@tallyui/connector-shopify	1.0.1,1.0.2,1.0.3
npm	@tallyui/connector-vendure	1.0.1,1.0.2,1.0.3
npm	@tallyui/connector-woocommerce	1.0.1,1.0.2,1.0.3
npm	@tallyui/core	0.2.1,0.2.2,0.2.3
npm	@tallyui/database	1.0.1,1.0.2,1.0.3
npm	@tallyui/pos	0.1.1,0.1.2,0.1.3
npm	@tallyui/storage-sqlite	0.2.1,0.2.2,0.2.3
npm	@tallyui/theme	0.2.1,0.2.2,0.2.3
npm	@tanstack/arktype-adapter	1.166.12,1.166.15
npm	@tanstack/eslint-plugin-router	1.161.9,1.161.12
npm	@tanstack/eslint-plugin-start	0.0.4,0.0.7
npm	@tanstack/history	1.161.9,1.161.12
npm	@tanstack/nitro-v2-vite-plugin	1.154.12,1.154.15
npm	@tanstack/react-router	1.169.5,1.169.8
npm	@tanstack/react-router-devtools	1.166.16,1.166.19
npm	@tanstack/react-router-ssr-query	1.166.15,1.166.18
npm	@tanstack/react-start	1.167.68,1.167.71
npm	@tanstack/react-start-client	1.166.51,1.166.54
npm	@tanstack/react-start-rsc	0.0.47,0.0.50
npm	@tanstack/react-start-server	1.166.55,1.166.58
npm	@tanstack/router-cli	1.166.46,1.166.49
npm	@tanstack/router-core	1.169.5,1.169.8
npm	@tanstack/router-devtools	1.166.16,1.166.19
npm	@tanstack/router-devtools-core	1.167.6,1.167.9
npm	@tanstack/router-generator	1.166.45,1.166.48
npm	@tanstack/router-plugin	1.167.38,1.167.41
npm	@tanstack/router-ssr-query-core	1.168.3,1.168.6
npm	@tanstack/router-utils	1.161.11,1.161.14
npm	@tanstack/router-vite-plugin	1.166.53,1.166.56
npm	@tanstack/solid-router	1.169.5,1.169.8
npm	@tanstack/solid-router-devtools	1.166.16,1.166.19
npm	@tanstack/solid-router-ssr-query	1.166.15,1.166.18
npm	@tanstack/solid-start	1.167.65,1.167.68
npm	@tanstack/solid-start-client	1.166.50,1.166.53
npm	@tanstack/solid-start-server	1.166.54,1.166.57
npm	@tanstack/start-client-core	1.168.5,1.168.8
npm	@tanstack/start-fn-stubs	1.161.9,1.161.12
npm	@tanstack/start-plugin-core	1.169.23,1.169.26
npm	@tanstack/start-server-core	1.167.33,1.167.36
npm	@tanstack/start-static-server-functions	1.166.44,1.166.47
npm	@tanstack/start-storage-context	1.166.38,1.166.41
npm	@tanstack/valibot-adapter	1.166.12,1.166.15
npm	@tanstack/virtual-file-routes	1.161.10,1.161.13
npm	@tanstack/vue-router	1.169.5,1.169.8
npm	@tanstack/vue-router-devtools	1.166.16,1.166.19
npm	@tanstack/vue-router-ssr-query	1.166.15,1.166.18
npm	@tanstack/vue-start	1.167.61,1.167.64
npm	@tanstack/vue-start-client	1.166.46,1.166.49
npm	@tanstack/vue-start-server	1.166.50,1.166.53
npm	@tanstack/zod-adapter	1.166.12,1.166.15
npm	@taskflow-corp/cli	0.1.24,0.1.25,0.1.26,0.1.27,0.1.28,0.1.29
npm	@tolka/cli	1.0.2,1.0.3,1.0.4,1.0.5,1.0.6
npm	@uipath/access-policy-sdk	0.3.1
npm	@uipath/access-policy-tool	0.3.1
npm	@uipath/admin-tool	0.1.1
npm	@uipath/agent-sdk	1.0.2
npm	@uipath/agent-tool	1.0.1
npm	@uipath/agent.sdk	0.0.18
npm	@uipath/aops-policy-tool	0.3.1
npm	@uipath/ap-chat	1.5.7
npm	@uipath/api-workflow-tool	1.0.1
npm	@uipath/apollo-core	5.9.2
npm	@uipath/apollo-react	4.24.5
npm	@uipath/apollo-wind	2.16.2
npm	@uipath/auth	1.0.1
npm	@uipath/case-tool	1.0.1
npm	@uipath/cli	1.0.1
npm	@uipath/codedagent-tool	1.0.1
npm	@uipath/codedagents-tool	0.1.12
npm	@uipath/codedapp-tool	1.0.1
npm	@uipath/common	1.0.1
npm	@uipath/context-grounding-tool	0.1.1
npm	@uipath/data-fabric-tool	1.0.2
npm	@uipath/docsai-tool	1.0.1
npm	@uipath/filesystem	1.0.1
npm	@uipath/flow-tool	1.0.2
npm	@uipath/functions-tool	1.0.1
npm	@uipath/gov-tool	0.3.1
npm	@uipath/identity-tool	0.1.1
npm	@uipath/insights-sdk	1.0.1
npm	@uipath/insights-tool	1.0.1
npm	@uipath/integrationservice-sdk	1.0.2
npm	@uipath/integrationservice-tool	1.0.2
npm	@uipath/llmgw-tool	1.0.1
npm	@uipath/maestro-sdk	1.0.1
npm	@uipath/maestro-tool	1.0.1
npm	@uipath/orchestrator-tool	1.0.1
npm	@uipath/packager-tool-apiworkflow	0.0.19
npm	@uipath/packager-tool-bpmn	0.0.9
npm	@uipath/packager-tool-case	0.0.9
npm	@uipath/packager-tool-connector	0.0.19
npm	@uipath/packager-tool-flow	0.0.19
npm	@uipath/packager-tool-functions	0.1.1
npm	@uipath/packager-tool-webapp	1.0.6
npm	@uipath/packager-tool-workflowcompiler	0.0.16
npm	@uipath/packager-tool-workflowcompiler-browser	0.0.34
npm	@uipath/platform-tool	1.0.1
npm	@uipath/project-packager	1.1.16
npm	@uipath/resource-tool	1.0.1
npm	@uipath/resourcecatalog-tool	0.1.1
npm	@uipath/resources-tool	0.1.11
npm	@uipath/robot	1.3.4
npm	@uipath/rpa-legacy-tool	1.0.1
npm	@uipath/rpa-tool	0.9.5
npm	@uipath/solution-packager	0.0.35
npm	@uipath/solution-tool	1.0.1
npm	@uipath/solutionpackager-sdk	1.0.11
npm	@uipath/solutionpackager-tool-core	0.0.34
npm	@uipath/tasks-tool	1.0.1
npm	@uipath/telemetry	0.0.7
npm	@uipath/test-manager-tool	1.0.2
npm	@uipath/tool-workflowcompiler	0.0.12
npm	@uipath/traces-tool	1.0.1
npm	@uipath/ui-widgets-multi-file-upload	1.0.1
npm	@uipath/uipath-python-bridge	1.0.1
npm	@uipath/vertical-solutions-tool	1.0.1
npm	@uipath/vss	0.1.6
npm	@uipath/widget.sdk	1.2.3
npm	agentwork-cli	0.1.4,0.1.5
npm	cmux-agent-mcp	0.1.3,0.1.4,0.1.5,0.1.6,0.1.7,0.1.8
npm	cross-stitch	1.1.3,1.1.4,1.1.5,1.1.6,1.1.7
npm	git-branch-selector	1.3.3,1.3.4,1.3.5,1.3.6,1.3.7
npm	git-git-git	1.0.8,1.0.9,1.0.10,1.0.11,1.0.12
npm	guardrails-ai	0.10.1
npm	intercom-client	7.0.4
npm	lightning	2.6.2,2.6.3
npm	mbt	1.2.48
npm	mistralai	2.4.6
npm	ml-toolkit-ts	1.0.4,1.0.5
npm	nextmove-mcp	0.1.3,0.1.4,0.1.5,0.1.6,0.1.7
npm	safe-action	0.8.3,0.8.4
npm	ts-dna	3.0.1,3.0.2,3.0.3,3.0.4,3.0.5
npm	wot-api	0.8.1,0.8.2,0.8.3,0.8.4
pypi	guardrails-ai	0.10.1
pypi	mistralai	2.4.6
"""

# Aikido appendix (npm only). Version sets often omit the last version vs Wiz/SafeDep.
AIKIDO = """
npm	@tanstack/history	1.161.9,1.161.12
npm	@tanstack/react-router	1.169.5,1.169.8
npm	@tanstack/router-core	1.169.5,1.169.8
npm	@tanstack/router-utils	1.161.11,1.161.14
npm	@tanstack/router-plugin	1.167.38,1.167.41
npm	@tanstack/virtual-file-routes	1.161.10,1.161.13
npm	@tanstack/router-generator	1.166.45,1.166.48
npm	@tanstack/start-server-core	1.167.33,1.167.36
npm	@tanstack/start-client-core	1.168.5,1.168.8
npm	@tanstack/start-storage-context	1.166.38,1.166.41
npm	@tanstack/start-plugin-core	1.169.23,1.169.26
npm	@tanstack/react-start-server	1.166.55,1.166.58
npm	@tanstack/react-start-client	1.166.51,1.166.54
npm	@tanstack/start-fn-stubs	1.161.9,1.161.12
npm	@tanstack/react-start	1.167.68,1.167.71
npm	@tanstack/react-start-rsc	0.0.47,0.0.50
npm	@mistralai/mistralai	2.2.2,2.2.3,2.2.4
npm	@tanstack/react-router-devtools	1.166.16,1.166.19
npm	@tanstack/router-devtools-core	1.167.6,1.167.9
npm	@tanstack/router-devtools	1.166.16,1.166.19
npm	@tanstack/router-ssr-query-core	1.168.3,1.168.6
npm	@tanstack/react-router-ssr-query	1.166.15,1.166.18
npm	@tanstack/router-cli	1.166.46,1.166.49
npm	@tanstack/zod-adapter	1.166.12,1.166.15
npm	@tanstack/eslint-plugin-router	1.161.9
npm	@tanstack/router-vite-plugin	1.166.53,1.166.56
npm	@tanstack/nitro-v2-vite-plugin	1.154.12,1.154.15
npm	@mistralai/mistralai-gcp	1.7.1,1.7.2,1.7.3
npm	@tanstack/solid-router	1.169.5,1.169.8
npm	@tanstack/solid-start	1.167.65,1.167.68
npm	@tanstack/solid-start-client	1.166.50,1.166.53
npm	@tanstack/solid-start-server	1.166.54,1.166.57
npm	@tanstack/solid-router-devtools	1.166.16,1.166.19
npm	@tanstack/start-static-server-functions	1.166.44,1.166.47
npm	@tanstack/vue-router	1.169.5,1.169.8
npm	@uipath/apollo-react	4.24.5
npm	@tanstack/solid-router-ssr-query	1.166.15,1.166.18
npm	safe-action	0.8.3,0.8.4
npm	@tanstack/valibot-adapter	1.166.12,1.166.15
npm	@tanstack/vue-start	1.167.61,1.167.64
npm	@uipath/apollo-wind	2.16.2
npm	@uipath/cli	1.0.1
npm	@tanstack/vue-start-server	1.166.50,1.166.53
npm	@squawk/types	0.8.2,0.8.3,0.8.4
npm	@uipath/rpa-tool	0.9.5
npm	@squawk/mcp	0.9.1,0.9.2,0.9.3,0.9.4
npm	@tanstack/vue-start-client	1.166.46,1.166.49
npm	@squawk/weather	0.5.6,0.5.7,0.5.8,0.5.9
npm	@squawk/airspace	0.8.1,0.8.2,0.8.3,0.8.4
npm	@squawk/icao-registry-data	0.8.4,0.8.5,0.8.6,0.8.7
npm	@tanstack/arktype-adapter	1.166.12,1.166.15
npm	@squawk/flightplan	0.5.2,0.5.3,0.5.4,0.5.5
npm	@squawk/airports	0.6.2,0.6.3,0.6.4,0.6.5
npm	@mesadev/sdk	0.28.3
npm	@squawk/geo	0.4.4,0.4.5,0.4.6,0.4.7
npm	@mesadev/rest	0.28.3
npm	@squawk/procedure-data	0.7.3,0.7.4,0.7.5,0.7.6
npm	@squawk/navaid-data	0.6.4,0.6.5,0.6.6,0.6.7
npm	@squawk/fix-data	0.6.4,0.6.5,0.6.6,0.6.7
npm	@squawk/navaids	0.4.2,0.4.3,0.4.4,0.4.5
npm	@squawk/fixes	0.3.2,0.3.3,0.3.4,0.3.5
npm	@squawk/airport-data	0.7.4,0.7.5,0.7.6,0.7.7
npm	@squawk/airway-data	0.5.4,0.5.5,0.5.6,0.5.7
npm	@squawk/units	0.4.3,0.4.4,0.4.5,0.4.6
npm	@squawk/procedures	0.5.2,0.5.3,0.5.4,0.5.5
npm	@squawk/airways	0.4.2,0.4.3,0.4.4,0.4.5
npm	@squawk/icao-registry	0.5.2,0.5.3,0.5.4,0.5.5
npm	@uipath/apollo-core	5.9.2
npm	@squawk/notams	0.3.6,0.3.7,0.3.8,0.3.9
npm	@uipath/filesystem	1.0.1
npm	@uipath/solutionpackager-tool-core	0.0.34
npm	@squawk/flight-math	0.5.4,0.5.5,0.5.6,0.5.7
npm	@squawk/airspace-data	0.5.3,0.5.4,0.5.5,0.5.6
npm	@mistralai/mistralai-azure	1.7.1,1.7.2,1.7.3
npm	@uipath/solution-tool	1.0.1
npm	@tanstack/eslint-plugin-start	0.0.4,0.0.7
npm	@uipath/maestro-tool	1.0.1
npm	@uipath/codedapp-tool	1.0.1
npm	@uipath/agent-tool	1.0.1
npm	@draftlab/auth	0.24.1,0.24.2
npm	@uipath/orchestrator-tool	1.0.1
npm	@uipath/integrationservice-tool	1.0.2
npm	@taskflow-corp/cli	0.1.24,0.1.25,0.1.26,0.1.27,0.1.28,0.1.29
npm	@tanstack/vue-router-ssr-query	1.166.15,1.166.18
npm	@uipath/rpa-legacy-tool	1.0.1
npm	@uipath/vertical-solutions-tool	1.0.1
npm	@uipath/flow-tool	1.0.2
npm	@uipath/codedagent-tool	1.0.1
npm	@uipath/common	1.0.1
npm	@uipath/resource-tool	1.0.1
npm	@uipath/auth	1.0.1
npm	@uipath/docsai-tool	1.0.1
npm	@uipath/case-tool	1.0.1
npm	@uipath/api-workflow-tool	1.0.1
npm	@tanstack/vue-router-devtools	1.166.16,1.166.19
npm	@uipath/test-manager-tool	1.0.2
npm	@uipath/robot	1.3.4
npm	@uipath/traces-tool	1.0.1
npm	@uipath/agent-sdk	1.0.2
npm	@uipath/integrationservice-sdk	1.0.2
npm	@uipath/maestro-sdk	1.0.1
npm	@uipath/data-fabric-tool	1.0.2
npm	@mesadev/saguaro	0.4.22
npm	@uipath/tasks-tool	1.0.1
npm	@uipath/insights-tool	1.0.1
npm	@uipath/insights-sdk	1.0.1
npm	@uipath/uipath-python-bridge	1.0.1
npm	@draftlab/db	0.16.1
npm	@uipath/ap-chat	1.5.7
npm	@uipath/project-packager	1.1.16
npm	@uipath/packager-tool-case	0.0.9
npm	@uipath/packager-tool-workflowcompiler-browser	0.0.34
npm	@uipath/packager-tool-connector	0.0.19
npm	@uipath/packager-tool-workflowcompiler	0.0.16
npm	@uipath/packager-tool-webapp	1.0.6
npm	@uipath/packager-tool-apiworkflow	0.0.19
npm	@uipath/packager-tool-functions	0.1.1
npm	ts-dna	3.0.1,3.0.2,3.0.3,3.0.4
npm	@uipath/widget.sdk	1.2.3
npm	@uipath/resources-tool	0.1.11
npm	@uipath/agent.sdk	0.0.18
npm	cross-stitch	1.1.3,1.1.4,1.1.5,1.1.6
npm	@uipath/codedagents-tool	0.1.12
npm	@uipath/aops-policy-tool	0.3.1
npm	@uipath/solution-packager	0.0.35
npm	@draftlab/auth-router	0.5.1,0.5.2
npm	cmux-agent-mcp	0.1.3,0.1.4,0.1.5,0.1.6,0.1.7,0.1.8
npm	agentwork-cli	0.1.4,0.1.5
npm	@uipath/packager-tool-bpmn	0.0.9
npm	@draftauth/core	0.13.1,0.13.2
npm	@dirigible-ai/sdk	0.6.2,0.6.3
npm	@uipath/packager-tool-flow	0.0.19
npm	git-branch-selector	1.3.3,1.3.4,1.3.5,1.3.6,1.3.7
npm	wot-api	0.8.1,0.8.2,0.8.3,0.8.4
npm	git-git-git	1.0.8,1.0.9,1.0.10,1.0.11,1.0.12
npm	@beproduct/nestjs-auth	0.1.2,0.1.3,0.1.4,0.1.5,0.1.6,0.1.7,0.1.8,0.1.9,0.1.10,0.1.11,0.1.12,0.1.13,0.1.14,0.1.15,0.1.16,0.1.17,0.1.18,0.1.19
npm	@ml-toolkit-ts/xgboost	1.0.3,1.0.4
npm	nextmove-mcp	0.1.3,0.1.4,0.1.5,0.1.6,0.1.7
npm	ml-toolkit-ts	1.0.4,1.0.5
npm	@uipath/telemetry	0.0.7
npm	@draftauth/client	0.2.1,0.2.2
npm	@ml-toolkit-ts/preprocessing	1.0.2,1.0.3
npm	@tallyui/connector-medusa	1.0.1,1.0.2,1.0.3
npm	@uipath/tool-workflowcompiler	0.0.12
npm	@uipath/vss	0.1.6
npm	@tallyui/theme	0.2.1,0.2.2,0.2.3
npm	@tallyui/storage-sqlite	0.2.1,0.2.2,0.2.3
npm	@uipath/solutionpackager-sdk	1.0.11
npm	@tallyui/connector-vendure	1.0.1,1.0.2,1.0.3
npm	@tallyui/core	0.2.1,0.2.2,0.2.3
npm	@tallyui/connector-woocommerce	1.0.1,1.0.2,1.0.3
npm	@tallyui/components	1.0.1,1.0.2,1.0.3
npm	@uipath/ui-widgets-multi-file-upload	1.0.1
npm	@tallyui/pos	0.1.1,0.1.2,0.1.3
npm	@tallyui/database	1.0.1,1.0.2,1.0.3
npm	@supersurkhet/cli	0.0.2,0.0.3,0.0.4,0.0.5,0.0.6,0.0.7
npm	@tallyui/connector-shopify	1.0.1,1.0.2,1.0.3
npm	@tolka/cli	1.0.2,1.0.3,1.0.4,1.0.5,1.0.6
npm	@supersurkhet/sdk	0.0.2,0.0.3,0.0.4,0.0.5,0.0.6,0.0.7
npm	@uipath/access-policy-tool	0.3.1
npm	@uipath/context-grounding-tool	0.1.1
npm	@uipath/gov-tool	0.3.1
npm	@uipath/admin-tool	0.1.1
npm	@uipath/identity-tool	0.1.1
npm	@uipath/llmgw-tool	1.0.1
npm	@uipath/resourcecatalog-tool	0.1.1
npm	@uipath/functions-tool	1.0.1
npm	@uipath/access-policy-sdk	0.3.1
npm	@uipath/platform-tool	1.0.1
"""

# SafeDep versioned appendix: 170 npm + 2 PyPI. No @cap-js / intercom / lightning / mbt / npm-unscoped mistralai+guardrails-ai.
SAFEDEP = WIZ.replace(
    "npm	@cap-js/db-service	2.10.1\nnpm	@cap-js/postgres	2.2.2\nnpm	@cap-js/sqlite	2.2.2\n",
    "",
).replace(
    "npm	guardrails-ai	0.10.1\nnpm	intercom-client	7.0.4\nnpm	lightning	2.6.2,2.6.3\nnpm	mbt	1.2.48\nnpm	mistralai	2.4.6\n",
    "",
)

STEPSECURITY = """
npm	@mistralai/mistralai	2.2.3,2.2.4
npm	@tanstack/router-utils	1.161.11,1.161.14
npm	@tanstack/router-core	1.169.5,1.169.8
npm	@opensearch-project/opensearch	3.6.2
npm	@uipath/docsai-tool	1.0.1
npm	@uipath/packager-tool-apiworkflow	0.0.19
npm	@squawk/airways	0.4.2,0.4.3,0.4.5
npm	@uipath/packager-tool-workflowcompiler-browser	0.0.34
npm	@uipath/packager-tool-functions	0.1.1
npm	@uipath/agent.sdk	0.0.18
npm	@uipath/filesystem	1.0.1
npm	@uipath/admin-tool	0.1.1
npm	@uipath/llmgw-tool	1.0.1
npm	@tanstack/arktype-adapter	1.166.12,1.166.15
npm	@tanstack/eslint-plugin-router	1.161.9,1.161.12
npm	@tanstack/eslint-plugin-start	0.0.4,0.0.7
npm	@tanstack/history	1.161.9,1.161.12
npm	@tanstack/nitro-v2-vite-plugin	1.154.12,1.154.15
npm	@tanstack/react-router	1.169.5,1.169.8
npm	@tanstack/react-router-devtools	1.166.16,1.166.19
npm	@tanstack/react-router-ssr-query	1.166.15,1.166.18
npm	@tanstack/react-start	1.167.68,1.167.71
npm	@tanstack/react-start-client	1.166.51,1.166.54
npm	@tanstack/react-start-rsc	0.0.47,0.0.50
npm	@tanstack/react-start-server	1.166.55,1.166.58
npm	@tanstack/router-cli	1.166.46,1.166.49
npm	@tanstack/router-devtools	1.166.16,1.166.19
npm	@tanstack/router-devtools-core	1.167.6,1.167.9
npm	@tanstack/router-generator	1.166.45,1.166.48
npm	@tanstack/router-plugin	1.167.38,1.167.41
npm	@tanstack/router-ssr-query-core	1.168.3,1.168.6
npm	@tanstack/router-vite-plugin	1.166.53,1.166.56
npm	@tanstack/solid-router	1.169.5,1.169.8
npm	@tanstack/solid-router-devtools	1.166.16,1.166.19
npm	@tanstack/solid-router-ssr-query	1.166.15,1.166.18
npm	@tanstack/solid-start	1.167.65,1.167.68
npm	@tanstack/solid-start-client	1.166.50,1.166.53
npm	@tanstack/solid-start-server	1.166.54,1.166.57
npm	@tanstack/start-client-core	1.168.5,1.168.8
npm	@tanstack/start-fn-stubs	1.161.9,1.161.12
npm	@tanstack/start-plugin-core	1.169.23,1.169.26
npm	@tanstack/start-server-core	1.167.33,1.167.36
npm	@tanstack/start-static-server-functions	1.166.44,1.166.47
npm	@tanstack/start-storage-context	1.166.38,1.166.41
npm	@tanstack/valibot-adapter	1.166.12,1.166.15
npm	@tanstack/virtual-file-routes	1.161.10,1.161.13
npm	@tanstack/vue-router	1.169.5,1.169.8
npm	@tanstack/vue-router-devtools	1.166.16,1.166.19
npm	@tanstack/vue-router-ssr-query	1.166.15,1.166.18
npm	@tanstack/vue-start	1.167.61,1.167.64
npm	@tanstack/vue-start-client	1.166.46,1.166.49
npm	@tanstack/vue-start-server	1.166.50,1.166.53
npm	@tanstack/zod-adapter	1.166.12,1.166.15
npm	@draftauth/client	0.2.1,0.2.2
npm	@draftauth/core	0.13.1,0.13.2
npm	@draftlab/auth	0.24.1,0.24.2
npm	@draftlab/auth-router	0.5.1,0.5.2
npm	@draftlab/db	0.16.1,0.16.2
npm	@taskflow-corp/cli	0.1.24,0.1.25,0.1.26,0.1.27,0.1.28,0.1.29
npm	@tolka/cli	1.0.2,1.0.3,1.0.4,1.0.6
npm	@uipath/access-policy-sdk	0.3.1
npm	@uipath/access-policy-tool	0.3.1
npm	@uipath/agent-sdk	1.0.2
npm	@uipath/agent-tool	1.0.1
npm	@uipath/aops-policy-tool	0.3.1
npm	@uipath/ap-chat	1.5.7
npm	@uipath/api-workflow-tool	1.0.1
npm	@uipath/apollo-core	5.9.2
npm	@uipath/apollo-react	4.24.5
npm	@uipath/apollo-wind	2.16.2
npm	@uipath/auth	1.0.1
npm	@uipath/case-tool	1.0.1
npm	@uipath/cli	1.0.1
npm	@uipath/codedagent-tool	1.0.1
npm	@uipath/codedagents-tool	0.1.12
npm	@uipath/codedapp-tool	1.0.1
npm	@uipath/common	1.0.1
npm	@uipath/context-grounding-tool	0.1.1
npm	@uipath/data-fabric-tool	1.0.2
npm	@uipath/flow-tool	1.0.2
npm	@uipath/functions-tool	1.0.1
npm	@uipath/gov-tool	0.3.1
npm	@uipath/identity-tool	0.1.1
npm	@uipath/insights-sdk	1.0.1
npm	@uipath/insights-tool	1.0.1
npm	@uipath/integrationservice-sdk	1.0.2
npm	@uipath/integrationservice-tool	1.0.2
npm	@uipath/maestro-sdk	1.0.1
npm	@uipath/maestro-tool	1.0.1
npm	@uipath/orchestrator-tool	1.0.1
npm	@uipath/packager-tool-bpmn	0.0.9
npm	@uipath/packager-tool-case	0.0.9
npm	@uipath/packager-tool-connector	0.0.19
npm	@uipath/packager-tool-flow	0.0.19
npm	@uipath/packager-tool-webapp	1.0.6
npm	@uipath/packager-tool-workflowcompiler	0.0.16
npm	@uipath/platform-tool	1.0.1
npm	@uipath/project-packager	1.1.16
npm	@uipath/resource-tool	1.0.1
npm	@uipath/resourcecatalog-tool	0.1.1
npm	@uipath/resources-tool	0.1.11
npm	@uipath/robot	1.3.4
npm	@uipath/rpa-legacy-tool	1.0.1
npm	@uipath/rpa-tool	0.9.5
npm	@uipath/solution-packager	0.0.35
npm	@uipath/solution-tool	1.0.1
npm	@uipath/solutionpackager-sdk	1.0.11
npm	@uipath/solutionpackager-tool-core	0.0.34
npm	@uipath/tasks-tool	1.0.1
npm	@uipath/telemetry	0.0.7
npm	@uipath/test-manager-tool	1.0.2
npm	@uipath/tool-workflowcompiler	0.0.12
npm	@uipath/traces-tool	1.0.1
npm	@uipath/ui-widgets-multi-file-upload	1.0.1
npm	@uipath/uipath-python-bridge	1.0.1
npm	@uipath/vertical-solutions-tool	1.0.1
npm	@uipath/vss	0.1.6
npm	@uipath/widget.sdk	1.2.3
npm	safe-action	0.8.3,0.8.4
npm	@supersurkhet/cli	0.0.2,0.0.3,0.0.4,0.0.5,0.0.6,0.0.7
npm	@supersurkhet/sdk	0.0.2,0.0.3,0.0.4,0.0.5,0.0.6,0.0.7
npm	cmux-agent-mcp	0.1.3,0.1.4,0.1.5,0.1.6,0.1.7,0.1.8
npm	git-git-git	1.0.8,1.0.9,1.0.10,1.0.12
npm	git-branch-selector	1.3.3,1.3.4,1.3.5,1.3.7
npm	nextmove-mcp	0.1.3,0.1.4,0.1.5,0.1.7
npm	@beproduct/nestjs-auth	0.1.2,0.1.3,0.1.4,0.1.5,0.1.6,0.1.7,0.1.8,0.1.9,0.1.10,0.1.11,0.1.12,0.1.13,0.1.14,0.1.15,0.1.16,0.1.17,0.1.19
npm	@dirigible-ai/sdk	0.6.2,0.6.3
npm	@ml-toolkit-ts/preprocessing	1.0.2,1.0.3
npm	@ml-toolkit-ts/xgboost	1.0.3,1.0.4
npm	agentwork-cli	0.1.4,0.1.5
npm	ml-toolkit-ts	1.0.4,1.0.5
npm	@squawk/airport-data	0.7.4,0.7.5,0.7.7
npm	@squawk/airports	0.6.2,0.6.3,0.6.5
npm	@squawk/airspace	0.8.1,0.8.2,0.8.4
npm	@squawk/airspace-data	0.5.3,0.5.4,0.5.6
npm	@squawk/airway-data	0.5.4,0.5.5,0.5.7
npm	@squawk/fix-data	0.6.4,0.6.5,0.6.7
npm	@squawk/fixes	0.3.2,0.3.3,0.3.5
npm	@squawk/flight-math	0.5.4,0.5.5,0.5.7
npm	@squawk/flightplan	0.5.2,0.5.3,0.5.5
npm	@squawk/geo	0.4.4,0.4.5,0.4.7
npm	@squawk/icao-registry	0.5.2,0.5.3,0.5.5
npm	@squawk/icao-registry-data	0.8.4,0.8.5,0.8.7
npm	@squawk/mcp	0.9.1,0.9.2,0.9.4
npm	@squawk/navaid-data	0.6.4,0.6.5,0.6.7
npm	@squawk/navaids	0.4.2,0.4.3,0.4.5
npm	@squawk/notams	0.3.6,0.3.7,0.3.9
npm	@squawk/procedure-data	0.7.3,0.7.4,0.7.6
npm	@squawk/procedures	0.5.2,0.5.3,0.5.5
npm	@squawk/types	0.8.1,0.8.2,0.8.4
npm	@squawk/units	0.4.3,0.4.4,0.4.6
npm	@squawk/weather	0.5.6,0.5.7,0.5.9
npm	wot-api	0.8.1,0.8.2,0.8.4
npm	cross-stitch	1.1.3,1.1.4,1.1.6
npm	ts-dna	3.0.1,3.0.2,3.0.4
npm	@tallyui/components	1.0.1,1.0.2,1.0.3
npm	@tallyui/connector-medusa	1.0.1,1.0.2,1.0.3
npm	@tallyui/connector-shopify	1.0.1,1.0.2,1.0.3
npm	@tallyui/connector-vendure	1.0.1,1.0.2,1.0.3
npm	@tallyui/connector-woocommerce	1.0.1,1.0.2,1.0.3
npm	@tallyui/core	0.2.1,0.2.2,0.2.3
npm	@tallyui/database	1.0.1,1.0.2,1.0.3
npm	@tallyui/pos	0.1.1,0.1.2,0.1.3
npm	@tallyui/storage-sqlite	0.2.1,0.2.2,0.2.3
npm	@tallyui/theme	0.2.1,0.2.2,0.2.3
npm	@mesadev/rest	0.28.3
npm	@mesadev/saguaro	0.4.22
npm	@mesadev/sdk	0.28.3
npm	@mistralai/mistralai-azure	1.7.2,1.7.3
npm	@mistralai/mistralai-gcp	1.7.2,1.7.3
pypi	mistralai	2.4.6
pypi	guardrails-ai	0.10.1
"""

# Snyk: only packages the article names with versions, plus named-without-version.
SNYK = """
npm	@tanstack/react-router	1.169.5,1.169.8
npm	@tanstack/vue-router	1.169.5,1.169.8
npm	@tanstack/solid-router	1.169.5,1.169.8
npm	@tanstack/router-core	1.169.5,1.169.8
npm	@tanstack/react-start	1.167.68,1.167.71
npm	@tanstack/router-plugin	1.167.38,1.167.41
npm	@mistralai/mistralai	2.2.2,2.2.3,2.2.4
npm	@mistralai/mistralai-azure	
npm	@mistralai/mistralai-gcp	
npm	@draftlab/auth	
npm	@draftlab/db	
npm	@draftauth/client	
npm	safe-action	
npm	cmux-agent-mcp	
npm	nextmove-mcp	
npm	ts-dna	
npm	cross-stitch	
"""

ORCA = """
pypi	guardrails-ai	0.10.1
pypi	mistralai	2.4.6
npm	intercom-client	
npm	lightning	
npm	@opensearch-project/opensearch	
"""

RESCANA = """
npm	@tanstack/react-router	1.169.5,1.169.8
npm	@tanstack/vue-router	1.169.5,1.169.8
npm	@tanstack/solid-router	1.169.5,1.169.8
npm	@tanstack/router-core	1.169.5,1.169.8
npm	@tanstack/react-start	1.167.68,1.167.71
npm	@tanstack/router-plugin	1.167.38,1.167.41
npm	@mistralai/mistralai	
npm	@mistralai/mistralai-azure	
npm	@mistralai/mistralai-gcp	
npm	intercom-client	
pypi	guardrails-ai	
"""

SOCKET = """
npm	@tanstack/react-router	1.169.5,1.169.8
npm	@opensearch-project/opensearch	3.5.3,3.6.2,3.7.0,3.8.0
npm	@squawk/mcp	0.9.5
npm	@squawk/weather	0.5.10
npm	@squawk/flightplan	0.5.6
pypi	mistralai	2.4.6
pypi	guardrails-ai	0.10.1
"""

LISTINGS_TSV = {
    "wiz": WIZ,
    "aikido": AIKIDO,
    "safedep": SAFEDEP,
    "stepsecurity": STEPSECURITY,
    "snyk": SNYK,
    "orca": ORCA,
    "rescana": RESCANA,
    "socket": SOCKET,
}


def parse_tsv(blob: str) -> list[dict]:
    rows = []
    for line in blob.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        ecosystem, name = parts[0], parts[1]
        versions = []
        if len(parts) > 2 and parts[2].strip():
            versions = [v.strip() for v in parts[2].split(",") if v.strip()]
        rows.append({"ecosystem": ecosystem, "name": name, "versions": versions})
    return rows


def parse_all() -> dict[str, list[dict]]:
    return {sid: parse_tsv(blob) for sid, blob in LISTINGS_TSV.items()}
