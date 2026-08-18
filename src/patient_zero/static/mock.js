/**
 * Patient Zero — mock API + fetchApi.
 *
 * Default is mock so file:// and a static folder work with no server.
 * If window.PZ_API is set, or a health ping to :8080 / same-origin succeeds,
 * fetchApi talks to the live API. Health JSON `ready` distinguishes LIVE
 * from DEGRADED (API up, HydraDB missing or unloaded). Mock is only used
 * when no API answers.
 *
 * Precision@K and R0 stay null. Forecast scores are mock propagation, not precision.
 */
(function (global) {
  "use strict";

  var WORM_START = 1778527200; // 2026-05-11T19:20:00Z
  var SENTINEL_VALID_TO = 4102444800;
  var T26 = WORM_START + 360;
  var T46 = WORM_START + 1560;
  var T_CROSS = WORM_START + 1620; // 19:47 — first PyPI node, after "the world found out"
  var T_END = WORM_START + 30600;
  var LIVE_DEFAULT = "http://127.0.0.1:8080";
  var expandedPackages = {};

  // --- published-record seed names (HANDOFF §5). Compromise times are synthetic ticks. ---
  var SEED_PACKAGES = [
    { pid: "npm:@tanstack/react-query", at: WORM_START + 0 },
    { pid: "npm:@tanstack/query-core", at: WORM_START + 28 },
    { pid: "npm:@tanstack/react-query-devtools", at: WORM_START + 55 },
    { pid: "npm:@tanstack/react-table", at: WORM_START + 90 },
    { pid: "npm:@tanstack/table-core", at: WORM_START + 120 },
    { pid: "npm:@tanstack/react-router", at: WORM_START + 155 },
    { pid: "npm:@tanstack/router-core", at: WORM_START + 190 },
    { pid: "npm:@tanstack/react-virtual", at: WORM_START + 225 },
    { pid: "npm:@tanstack/virtual-core", at: WORM_START + 255 },
    { pid: "npm:@tanstack/react-form", at: WORM_START + 290 },
    { pid: "npm:@tanstack/form-core", at: WORM_START + 320 },
    { pid: "npm:@tanstack/react-store", at: WORM_START + 345 },
    { pid: "npm:@tanstack/store", at: WORM_START + 360 }
  ];

  var LATER_HITS = [
    { pid: "npm:@tanstack/react-query-persist-client", at: WORM_START + 900, role: "hit" },
    { pid: "npm:@tanstack/query-sync-storage-persister", at: WORM_START + 1100, role: "hit" },
    { pid: "npm:@tanstack/history", at: T46 + 20, role: "hit" },
    { pid: "pypi:stub-tanstack", at: T_CROSS, role: "hit" },
    { pid: "npm:stub-maintainer-neighbour-a", at: T46 + 240, role: "hit" },
    { pid: "npm:stub-maintainer-neighbour-b", at: T46 + 480, role: "hit" }
  ];

  var GRAPH = {
    nodes: SEED_PACKAGES.map(function (p, i) {
      return {
        id: p.pid,
        eco: "npm",
        label: p.pid.replace(/^npm:/, ""),
        at: p.at,
        role: i === 0 ? "origin" : "hit"
      };
    }).concat(
      LATER_HITS.map(function (p) {
        return {
          id: p.pid,
          eco: p.pid.indexOf("pypi:") === 0 ? "pypi" : "npm",
          label: p.pid.replace(/^(npm|pypi):/, ""),
          at: p.at,
          role: p.role
        };
      })
    ),
    edges: [
      ["npm:@tanstack/react-query", "npm:@tanstack/query-core", "trust"],
      ["npm:@tanstack/query-core", "npm:@tanstack/react-query-devtools", "trust"],
      ["npm:@tanstack/react-query", "npm:@tanstack/react-table", "trust"],
      ["npm:@tanstack/react-table", "npm:@tanstack/table-core", "trust"],
      ["npm:@tanstack/react-query", "npm:@tanstack/react-router", "trust"],
      ["npm:@tanstack/react-router", "npm:@tanstack/router-core", "trust"],
      ["npm:@tanstack/react-query", "npm:@tanstack/react-virtual", "trust"],
      ["npm:@tanstack/react-virtual", "npm:@tanstack/virtual-core", "trust"],
      ["npm:@tanstack/react-query", "npm:@tanstack/react-form", "trust"],
      ["npm:@tanstack/react-form", "npm:@tanstack/form-core", "trust"],
      ["npm:@tanstack/react-query", "npm:@tanstack/react-store", "trust"],
      ["npm:@tanstack/react-store", "npm:@tanstack/store", "trust"],
      ["npm:@tanstack/react-query", "npm:@tanstack/react-query-persist-client", "trust"],
      ["npm:@tanstack/query-core", "npm:@tanstack/query-sync-storage-persister", "trust"],
      ["npm:@tanstack/react-router", "npm:@tanstack/history", "trust"],
      ["npm:@tanstack/query-core", "pypi:stub-tanstack", "cross"],
      ["pypi:stub-tanstack", "npm:stub-maintainer-neighbour-a", "trust"],
      ["npm:@tanstack/store", "npm:stub-maintainer-neighbour-b", "trust"]
    ].map(function (e) {
      return { src: e[0], dst: e[1], kind: e[2] };
    })
  };

  var TRUST_FORECAST = [
    {
      pid: "npm:@tanstack/react-query-persist-client",
      score: 0.91,
      path: ["npm:@tanstack/react-query", "mid:npm:tannerlinsley", "npm:@tanstack/react-query-persist-client"],
      from: T26
    },
    {
      pid: "npm:@tanstack/query-sync-storage-persister",
      score: 0.84,
      path: ["npm:@tanstack/query-core", "rid:github:TanStack/query", "npm:@tanstack/query-sync-storage-persister"],
      from: T26
    },
    {
      pid: "npm:@tanstack/history",
      score: 0.77,
      path: ["npm:@tanstack/react-router", "wid:github:TanStack/router/.github/workflows/publish.yml", "npm:@tanstack/history"],
      from: T26
    },
    {
      pid: "pypi:stub-tanstack",
      score: 0.71,
      path: ["npm:@tanstack/query-core", "mid:npm:tannerlinsley", "pypi:stub-tanstack"],
      from: T26
    },
    {
      pid: "npm:stub-maintainer-neighbour-a",
      score: 0.64,
      path: ["npm:@tanstack/react-query", "mid:npm:tannerlinsley", "npm:stub-maintainer-neighbour-a"],
      from: T26
    },
    {
      pid: "npm:stub-maintainer-neighbour-b",
      score: 0.58,
      path: ["npm:@tanstack/store", "mid:npm:tannerlinsley", "npm:stub-maintainer-neighbour-b"],
      from: T26
    },
    {
      pid: "npm:stub-oidc-neighbour",
      score: 0.49,
      path: ["npm:@tanstack/react-query", "wid:github:TanStack/query/.github/workflows/release.yml", "npm:stub-oidc-neighbour"],
      from: T26
    },
    {
      pid: "npm:stub-email-domain-neighbour",
      score: 0.41,
      path: ["mid:npm:tannerlinsley", "mid:npm:stub-shared-domain", "npm:stub-email-domain-neighbour"],
      from: T26
    }
  ];

  var DEP_FORECAST = [
    { pid: "npm:stub-dependent-0", score: 0.04, path: ["npm:@tanstack/react-query", "npm:stub-dependent-0"], from: T26 },
    { pid: "npm:stub-dependent-1", score: 0.03, path: ["npm:@tanstack/query-core", "npm:stub-dependent-1"], from: T26 },
    { pid: "npm:stub-dependent-2", score: 0.02, path: ["npm:@tanstack/react-table", "npm:stub-dependent-2"], from: T26 },
    { pid: "npm:stub-dependent-3", score: 0.01, path: ["npm:@tanstack/react-query", "npm:stub-dependent-3"], from: T26 },
    { pid: "npm:stub-dependent-4", score: 0.0, path: ["npm:@tanstack/store", "npm:stub-dependent-4"], from: T26 }
  ];

  var SERVICES = [
    {
      sid: "svc:stub-storefront",
      name: "stub-storefront",
      exposed_at: WORM_START + 180,
      path: ["npm:@tanstack/react-query@5.0.1", "npm:stub-ui-kit@2.4.0", "npm:stub-storefront@1.9.3"]
    },
    {
      sid: "svc:stub-billing",
      name: "stub-billing",
      exposed_at: WORM_START + 540,
      path: ["npm:@tanstack/react-query@5.0.1", "npm:stub-forms@1.1.0", "npm:stub-billing@0.8.2"]
    },
    {
      sid: "svc:stub-admin",
      name: "stub-admin",
      exposed_at: T26 + 120,
      path: ["npm:@tanstack/react-table@8.0.0", "npm:stub-grid@3.2.1", "npm:stub-admin@0.4.0"]
    }
  ];

  var FINDINGS = [
    {
      vid: "npm:@tanstack/react-query@5.0.1",
      at: WORM_START,
      tier: "install",
      evidence: { has_install_script: true, install_hooks: ["postinstall"] }
    },
    {
      vid: "npm:stub-ui-kit@2.4.0",
      at: WORM_START + 180,
      tier: "install",
      evidence: { has_install_script: true, install_hooks: ["preinstall", "postinstall"] }
    },
    {
      vid: "npm:stub-forms@1.1.0",
      at: WORM_START + 540,
      tier: "none",
      evidence: { has_install_script: false, install_hooks: [] }
    },
    {
      vid: "npm:stub-grid@3.2.1",
      at: T26 + 120,
      tier: "none",
      evidence: { has_install_script: false, install_hooks: [] }
    },
    {
      vid: "npm:stub-logger@0.3.2",
      at: WORM_START,
      tier: "none",
      evidence: { has_install_script: false, install_hooks: [] }
    }
  ];

  function seedsAt(asOf) {
    return SEED_PACKAGES.filter(function (p) {
      return p.at <= asOf;
    }).map(function (p) {
      return p.pid;
    });
  }

  function vidsAt(asOf) {
    return FINDINGS.filter(function (f) {
      return f.at <= asOf;
    }).map(function (f) {
      return f.vid;
    });
  }

  function radiusCypher(maxHops, limit) {
    return (
      "CALL algo.SSpaths({\n" +
      "  sourceLabel: 'Version', sourceProperty: 'vid', sourceValues: $compromised,\n" +
      "  relTypes: ['DEPENDS_ON','PINS'], relDirection: 'incoming',\n" +
      "  maxLen: " +
      maxHops +
      ", resultLimit: " +
      limit +
      "\n" +
      "}) YIELD path\n" +
      "WHERE all(r IN relationships(path) WHERE r.valid_from <= $as_of < r.valid_to)\n" +
      "RETURN path"
    );
  }

  function forecastCypher(topology, maxHops, limit) {
    var relTypes =
      topology === "trust"
        ? "['MAINTAINS','PUBLISHED_FROM','HAS_WORKFLOW','PUBLISHES_VIA_OIDC','SHARES_EMAIL_DOMAIN']"
        : "['DEPENDS_ON','PINS']";
    return (
      "// topology=" +
      topology +
      "  <- the negative control is this one parameter\n" +
      "CALL algo.SSpaths({\n" +
      "  sourceLabel: 'Package', sourceProperty: 'pid', sourceValues: $seeds,\n" +
      "  relTypes: " +
      relTypes +
      ", relDirection: 'outgoing',\n" +
      "  maxLen: " +
      maxHops +
      ", resultLimit: " +
      limit +
      "\n" +
      "}) YIELD path\n" +
      "WITH last(nodes(path)) AS candidate, path\n" +
      "WHERE NOT candidate.pid IN $seeds\n" +
      "RETURN candidate.pid AS pid, count(DISTINCT path) AS support, collect(path)[0] AS justification\n" +
      "ORDER BY support DESC LIMIT $k"
    );
  }

  function indexCaseCypher(maxHops, limit) {
    return (
      "// same primitive, walked backward: given the symptoms, find the index case\n" +
      "CALL algo.SSpaths({\n" +
      "  sourceLabel: 'Package', sourceProperty: 'pid', sourceValues: $observed,\n" +
      "  relTypes: ['MAINTAINS','PUBLISHED_FROM','HAS_WORKFLOW','PUBLISHES_VIA_OIDC'],\n" +
      "  relDirection: 'incoming',\n" +
      "  maxLen: " +
      maxHops +
      ", resultLimit: " +
      limit +
      "\n" +
      "}) YIELD path\n" +
      "WITH last(nodes(path)) AS origin, count(DISTINCT head(nodes(path))) AS covered, path\n" +
      "RETURN origin, covered,\n" +
      "       coalesce(origin.uses_pull_request_target, false) AS vector_match,\n" +
      "       coalesce(origin.has_oidc_publish, false) AS oidc_publish, path\n" +
      "ORDER BY covered DESC, vector_match DESC LIMIT $k"
    );
  }

  var REACHABILITY_CYPHER =
    "// Leg 3 Tier 1: a property predicate, not a traversal\n" +
    "MATCH (s:Service {sid: $sid})-[p:PINS]->(v:Version)\n" +
    "WHERE v.vid IN $finding_vids AND p.valid_from <= $as_of < p.valid_to\n" +
    "RETURN v.vid AS vid, v.has_install_script AS install, v.install_hooks AS hooks";

  function leverageCypher(maxHops, limit) {
    return (
      "// Leg 4: forward from nothing — as if each credential were already stolen\n" +
      "MATCH (m:Maintainer)\n" +
      "CALL algo.SSpaths({\n" +
      "  sourceLabel: 'Maintainer', sourceProperty: 'mid', sourceValues: [m.mid],\n" +
      "  relTypes: ['MAINTAINS','PUBLISHED_FROM','HAS_WORKFLOW','PUBLISHES_VIA_OIDC','DEPENDS_ON','PINS'],\n" +
      "  relDirection: 'outgoing',\n" +
      "  maxLen: " +
      maxHops +
      ", resultLimit: " +
      limit +
      "\n" +
      "}) YIELD path\n" +
      "WITH m, [n IN nodes(path) WHERE n:Service] AS hit, path\n" +
      "RETURN m.mid AS id, count(DISTINCT hit) AS services_at_risk, collect(path)[0] AS path\n" +
      "ORDER BY services_at_risk DESC LIMIT $k"
    );
  }

  var EVIDENCE_CYPHER =
    "// the control: identical forecast, relTypes swapped, scored against the same IOC set\n" +
    "// precision@K and R0 are computed in the scorer over both result sets; see DESIGN.md §6\n" +
    "CALL algo.SSpaths({ /* forecast, relTypes: T2 */ }) YIELD path\n" +
    "UNION\n" +
    "CALL algo.SSpaths({ /* forecast, relTypes: T1 */ }) YIELD path";

  var TIMELINE_CYPHER =
    "MATCH (v:Version)\n" +
    "WHERE v.published_at >= $window_start AND v.published_at < $window_end\n" +
    "RETURN v.ecosystem AS ecosystem, v.published_at AS at, count(*) AS versions\n" +
    "ORDER BY at";

  function latency(seed) {
    return Math.round((6 + (seed % 17) + (seed % 5) * 0.3) * 1000) / 1000;
  }

  function envelope(cypher, body, seed) {
    body.cypher = cypher;
    body.latency_ms = latency(seed || cypher.length);
    body.stub = true;
    return body;
  }

  function pathOf(url) {
    try {
      if (url.charAt(0) === "/") return url.split("?")[0];
      var u = new URL(url, "http://127.0.0.1");
      return u.pathname;
    } catch (e) {
      return String(url).split("?")[0];
    }
  }

  function mockHandle(path, method, body) {
    var p = pathOf(path);
    var b = body || {};
    var asOf = typeof b.as_of === "number" ? b.as_of : T26;
    var k = typeof b.k === "number" ? b.k : 8;
    var maxHops = typeof b.max_hops === "number" ? b.max_hops : 6;
    var limit = typeof b.limit === "number" ? b.limit : 500;

    if (p === "/api/health") {
      return envelope("", { ok: true, hydradb_connected: false }, 3);
    }

    if (p === "/api/blast-radius") {
      var cutoff = typeof b.window_end === "number" ? b.window_end : asOf;
      var vid =
        (b.ecosystem || "npm") + ":" + (b.name || "@tanstack/react-query") + "@" + (b.version || "5.0.1");
      var hops = typeof b.max_hops === "number" ? b.max_hops : 6;
      var services = SERVICES.filter(function (s) {
        return s.exposed_at <= cutoff;
      }).map(function (s) {
        var copy = {
          sid: s.sid,
          name: s.name,
          exposed_at: s.exposed_at,
          path: s.path.slice()
        };
        copy.path[0] = vid;
        return copy;
      });
      return envelope(radiusCypher(hops, limit), {
        services: services,
        stats: {
          source_vid: vid,
          services_exposed: services.length,
          paths_returned: services.length,
          max_hops: hops,
          result_limit: limit,
          as_of: cutoff
        }
      }, 11);
    }

    if (p === "/api/forecast") {
      var topology = b.topology === "dependency" ? "dependency" : "trust";
      var trust = topology === "trust";
      var hopsF = typeof b.max_hops === "number" ? b.max_hops : 3;
      var seeds = Array.isArray(b.seeds) ? b.seeds : seedsAt(asOf);
      var src = trust ? TRUST_FORECAST : DEP_FORECAST;
      var preds = [];
      if (asOf >= T26 && seeds.length) {
        src.forEach(function (row) {
          if (row.from <= asOf && preds.length < k) {
            preds.push({
              pid: row.pid,
              score: row.score,
              justification_path: row.path.slice()
            });
          }
        });
      }
      return envelope(forecastCypher(topology, hopsF, limit), {
        predictions: preds,
        stats: {
          topology: topology,
          is_negative_control: !trust,
          seeds: seeds.length,
          k: k,
          max_hops: hopsF,
          result_limit: limit,
          as_of: asOf,
          precision_at_k: null,
          rank: b.rank === "popularity" ? "popularity" : "rarity"
        }
      }, trust ? 21 : 22);
    }

    if (p === "/api/index-case") {
      var hopsI = typeof b.max_hops === "number" ? b.max_hops : 4;
      var observed = Array.isArray(b.observed) ? b.observed : seedsAt(asOf);
      var kinds = [
        {
          kind: "workflow",
          id: "github:TanStack/query/.github/workflows/release.yml",
          score: 0.88,
          path: [
            "github:TanStack/query/.github/workflows/release.yml",
            "rid:github:TanStack/query",
            observed[0] || "npm:@tanstack/react-query"
          ]
        },
        {
          kind: "maintainer",
          id: "npm:tannerlinsley",
          score: 0.69,
          path: ["npm:tannerlinsley", "npm:@tanstack/query-core", observed[0] || "npm:@tanstack/react-query"]
        },
        {
          kind: "repo",
          id: "github:TanStack/query",
          score: 0.5,
          path: ["github:TanStack/query", "npm:@tanstack/react-query", observed[0] || "npm:@tanstack/react-query"]
        }
      ];
      var candidates = asOf >= T26 && observed.length ? kinds.slice(0, k) : [];
      return envelope(indexCaseCypher(hopsI, limit), {
        candidates: candidates.map(function (c) {
          return {
            id: c.id,
            kind: c.kind,
            score: c.score,
            path_to_observed: c.path
          };
        }),
        stats: {
          observed: observed.length,
          k: k,
          max_hops: hopsI,
          result_limit: limit,
          as_of: asOf,
          true_origin_rank: null
        }
      }, 31);
    }

    if (p === "/api/reachability") {
      var sid = b.sid || "svc:stub-storefront";
      var inVids = b.finding_vids && b.finding_vids.length ? b.finding_vids : vidsAt(asOf);
      var verdicts = FINDINGS.filter(function (f) {
        return f.at <= asOf && inVids.indexOf(f.vid) !== -1;
      }).map(function (f) {
        return { vid: f.vid, tier: f.tier, evidence: f.evidence };
      });
      if (!verdicts.length && asOf >= WORM_START) {
        verdicts = FINDINGS.filter(function (f) {
          return f.at <= asOf;
        }).map(function (f) {
          return { vid: f.vid, tier: f.tier, evidence: f.evidence };
        });
      }
      return envelope(REACHABILITY_CYPHER, {
        verdicts: verdicts,
        stats: {
          sid: sid,
          findings_in: verdicts.length,
          findings_executing: verdicts.filter(function (v) {
            return v.tier === "install";
          }).length,
          as_of: asOf
        }
      }, 41);
    }

    if (p === "/api/leverage") {
      var hopsL = typeof b.max_hops === "number" ? b.max_hops : 4;
      var kL = typeof b.k === "number" ? b.k : 5;
      var ranked = [
        {
          id: "npm:tannerlinsley",
          kind: "maintainer",
          services_at_risk: 12,
          path: ["npm:tannerlinsley", "npm:@tanstack/react-query", "svc:stub-storefront"]
        },
        {
          id: "github:TanStack/query/.github/workflows/release.yml",
          kind: "workflow",
          services_at_risk: 10,
          path: [
            "github:TanStack/query/.github/workflows/release.yml",
            "npm:@tanstack/query-core",
            "svc:stub-billing"
          ]
        },
        {
          id: "npm:stub-maintainer-0",
          kind: "maintainer",
          services_at_risk: 8,
          path: ["npm:stub-maintainer-0", "npm:stub-package", "svc:stub-storefront"]
        },
        {
          id: "github:TanStack/router/.github/workflows/publish.yml",
          kind: "workflow",
          services_at_risk: 6,
          path: ["github:TanStack/router/.github/workflows/publish.yml", "npm:@tanstack/react-router", "svc:stub-admin"]
        },
        {
          id: "npm:stub-maintainer-1",
          kind: "workflow",
          services_at_risk: 4,
          path: ["npm:stub-maintainer-1", "npm:stub-package", "svc:stub-storefront"]
        }
      ].slice(0, kL);
      return envelope(leverageCypher(hopsL, limit), {
        ranked: ranked,
        mincut: [
          { id: "npm:tannerlinsley", kind: "maintainer", action: "enforce 2FA" },
          {
            id: "github:TanStack/query/.github/workflows/release.yml",
            kind: "workflow",
            action: "drop pull_request_target"
          }
        ],
        stats: {
          k: kL,
          max_hops: hopsL,
          result_limit: limit,
          spread_blocked_pct: 1,
          cover: "greedy",
          cover_universe: "forecast_neighborhood",
          reachable_neighborhood: 12,
          reachable_validation: 0
        }
      }, 51);
    }

    if (p === "/api/evidence") {
      var unmeasured = {
        precision_at_10: null,
        precision_at_50: null,
        precision_at_100: null,
        recall_at_100: null,
        measured: false
      };
      return envelope(EVIDENCE_CYPHER, {
        precision_trust: Object.assign({}, unmeasured, { topology: "trust" }),
        precision_dependency: Object.assign({}, unmeasured, {
          topology: "dependency",
          role: "negative control"
        }),
        r0_trust: null,
        r0_dependency: null,
        trust_paths: 12,
        control_paths: 0,
        control_note: "identical SSpaths, relTypes swapped",
        note: "STUB: no validation has been run. Nulls are literal, not zeros.",
        stats: { measured: false, ioc_set_loaded: false }
      }, 61);
    }

    if (p === "/api/incident") {
      return envelope("// incident fixture, not a traversal", {
        id: "may11-tanstack",
        title: "TanStack / Mini Shai-Hulud",
        window_start: WORM_START,
        window_end: T_END,
        named_at: T26,
        world_found_out_at: T46,
        true_origin: { id: "npm:tannerlinsley", kind: "maintainer" },
        default_blast: {
          ecosystem: "npm",
          name: "@tanstack/react-query",
          version: "5.101.4"
        },
        default_sid: "svc:mattermost",
        ticks: [
          { at: WORM_START, label: "worm begins" },
          { at: T26, label: "42 @tanstack/* packages compromised (seed set)" },
          { at: T46, label: "first public detection (StepSecurity)" }
        ]
      }, 6);
    }

    if (p === "/api/identity") {
      var raw = String(path).split("?")[1] || "";
      var id = "";
      raw.split("&").forEach(function (pair) {
        var kv = pair.split("=");
        if (decodeURIComponent(kv[0] || "") === "id") {
          id = decodeURIComponent(kv[1] || "");
        }
      });
      var known = {
        "npm:tannerlinsley": {
          kind: "maintainer",
          name: "tannerlinsley",
          packages: [
            { pid: "npm:@tanstack/react-query", name: "@tanstack/react-query", ecosystem: "npm" },
            { pid: "npm:@tanstack/store", name: "@tanstack/store", ecosystem: "npm" }
          ],
          registries: ["npm"],
          packages_at_risk: 12,
          action: "revoke",
          path: ["npm:@tanstack/react-query", "npm:tannerlinsley", "npm:@tanstack/store"]
        }
      };
      var hit = known[id];
      if (!hit) {
        return envelope("// catalog join plus leverage neighborhood, not a new traversal", {
          found: false,
          id: id,
          packages: []
        }, 9);
      }
      var extras = expandedPackages[id] || [];
      return envelope("// catalog join plus leverage neighborhood, not a new traversal", Object.assign({
        found: true,
        id: id
      }, hit, {
        packages: hit.packages.concat(extras)
      }), 12);
    }

    if (p === "/api/expand") {
      var expandId = b.id || "";
      if (expandId !== "npm:tannerlinsley") {
        return envelope("// catalog merge from maintainer search, not a traversal", {
          found: false,
          id: expandId,
          added: 0,
          packages: []
        }, 8);
      }
      var extra = {
        pid: "npm:@tanstack/query-core",
        name: "@tanstack/query-core",
        ecosystem: "npm"
      };
      var current = expandedPackages[expandId] || [];
      var added = 0;
      if (!current.some(function (row) { return row.pid === extra.pid; })) {
        current = current.concat([extra]);
        expandedPackages[expandId] = current;
        added = 1;
      }
      return envelope("// catalog merge from maintainer search, not a traversal", {
        found: true,
        id: expandId,
        added: added,
        packages: [
          { pid: "npm:@tanstack/react-query", name: "@tanstack/react-query", ecosystem: "npm" },
          { pid: "npm:@tanstack/store", name: "@tanstack/store", ecosystem: "npm" }
        ].concat(current)
      }, 18);
    }

    if (p === "/api/timeline") {
      return envelope(TIMELINE_CYPHER, {
        events: [
          { at: WORM_START, label: "worm begins", packages: 1, source: "published record" },
          {
            at: T26,
            label: "42 @tanstack/* packages compromised (seed set)",
            packages: 42,
            source: "published record"
          },
          {
            at: T46,
            label: "first public detection (StepSecurity)",
            packages: 42,
            source: "published record"
          },
          { at: T_CROSS, label: "npm -> PyPI crossing", packages: null, source: "stub" },
          { at: T_END, label: "end of day: 170+ packages", packages: 170, source: "published record" }
        ],
        window_start: WORM_START,
        window_end: T_END,
        nodes: GRAPH.nodes,
        stats: { ticks: 5, counts_are_stub: true }
      }, 71);
    }

    if (p === "/api/meta") {
      return envelope("// catalog lookup, not a traversal", {
        default_blast: {
          ecosystem: "npm",
          name: "@tanstack/react-query",
          version: "5.101.4"
        },
        default_sid: "svc:mattermost",
        seed_pids: SEED_PACKAGES.map(function (s) { return s.pid; }),
        finding_vids: FINDINGS.map(function (f) {
          return { vid: f.vid, at: f.at };
        })
      }, 8);
    }

    return envelope("", { error: "unknown mock path", path: p, stub: true }, 99);
  }

  var nativeFetch = global.fetch ? global.fetch.bind(global) : null;
  var liveBase = null;
  var probed = false;
  var probePromise = null;

  function withTimeout(ms) {
    var ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
    var t = setTimeout(function () {
      if (ctrl) ctrl.abort();
    }, ms);
    return { signal: ctrl ? ctrl.signal : undefined, clear: function () { clearTimeout(t); } };
  }

  function probeLive() {
    if (probed) return Promise.resolve(liveBase);
    if (probePromise) return probePromise;
    probePromise = (function () {
      var candidates;
      if (typeof global.PZ_API === "string" && global.PZ_API.length) {
        candidates = [global.PZ_API.replace(/\/$/, "")];
      } else {
        candidates = ["", LIVE_DEFAULT];
      }
      if (!nativeFetch) {
        probed = true;
        PZ.mode = "mock";
        return Promise.resolve(null);
      }
      var i = 0;
      function next() {
        if (i >= candidates.length) {
          probed = true;
          liveBase = null;
          PZ.mode = "mock";
          PZ.base = null;
          return Promise.resolve(null);
        }
        var base = candidates[i++];
        var to = withTimeout(350);
        return nativeFetch(base + "/api/health", { signal: to.signal })
          .then(function (r) {
            to.clear();
            if (!r.ok) return next();
            return r.json().then(function (body) {
              if (!body || typeof body.hydradb_connected === "undefined") {
                return next();
              }
              liveBase = base || (global.location && global.location.origin ? global.location.origin : LIVE_DEFAULT);
              probed = true;
              PZ.health = body;
              PZ.mode = body.ready ? "live" : "degraded";
              PZ.base = liveBase;
              return liveBase;
            });
          })
          .catch(function () {
            to.clear();
            return next();
          });
      }
      return next();
    })();
    return probePromise;
  }

  function fetchApi(path, opts) {
    opts = opts || {};
    var method = (opts.method || "GET").toUpperCase();
    var body = opts.body;
    return probeLive().then(function (base) {
      if (base && nativeFetch) {
        var headers = {};
        var payload;
        if (body !== undefined && method !== "GET") {
          headers["Content-Type"] = "application/json";
          payload = JSON.stringify(body);
        }
        return nativeFetch(base + path, { method: method, headers: headers, body: payload }).then(function (r) {
          if (!r.ok) {
            return r.text().then(function (text) {
              throw new Error((r.status || 0) + " " + path + " " + text.slice(0, 180));
            });
          }
          return r.json();
        });
      }
      return Promise.resolve(mockHandle(path, method, body));
    });
  }

  var PZ = {
    WORM_START: WORM_START,
    SENTINEL_VALID_TO: SENTINEL_VALID_TO,
    T26: T26,
    T46: T46,
    T_CROSS: T_CROSS,
    T_END: T_END,
    GRAPH: GRAPH,
    SEED_PACKAGES: SEED_PACKAGES,
    FINDINGS: FINDINGS,
    seedsAt: seedsAt,
    vidsAt: vidsAt,
    fetchApi: fetchApi,
    mockHandle: mockHandle,
    probeLive: probeLive,
    mode: "mock",
    base: null,
    health: null
  };

  global.PZ = PZ;
  global.fetchApi = fetchApi;
})(typeof window !== "undefined" ? window : this);
