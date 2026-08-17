/**
 * Patient Zero — wire the existing DOM. No framework.
 * Scrubber is the investigation clock; every panel re-queries at that instant.
 */
(function () {
  "use strict";

  var PZ = window.PZ;
  if (!PZ) {
    console.error("mock.js must load before app.js");
    return;
  }

  var NS = "http://www.w3.org/2000/svg";
  var MARK_NAMED = 180; // 19:26
  var MARK_WORLD = 480; // 19:46
  var DEBOUNCE_MS = 150;
    var BANNER_COPY =
      "These panels are synthetic; no number here is a measurement.";
    var DEGRADED_COPY =
      "API is up but HydraDB is not ready. Panels will be empty until the graph loads.";

  var windowStart = PZ.WORM_START;
  var windowEnd = PZ.T_END;
  var topology = "trust";
  var bannerLocked = false;
  var seenNodes = {};
  var debounceTimer = 0;
  var inflight = 0;
  var blast = { ecosystem: "npm", name: "@tanstack/react-query", version: "5.101.4" };
  var reachSid = "svc:mattermost";
  var pinnedVids = ["npm:@tanstack/react-table@8.10.7", "npm:@tanstack/table-core@8.10.7"];
  var seedPids = [];
  var clockNodes = [];
  var findingVids = [];

  var $ = function (id) {
    return document.getElementById(id);
  };

  function seedsForClock(asOf) {
    if (asOf < PZ.T26) return [];
    if (seedPids.length) return seedPids.slice();
    return PZ.seedsAt(asOf);
  }

  function vidsForClock(asOf) {
    if (PZ.mode === "live") {
      return findingVids
        .filter(function (row) {
          return row && row.vid && (row.at == null || row.at <= asOf);
        })
        .map(function (row) {
          return row.vid;
        });
    }
    return PZ.vidsAt(asOf).concat(pinnedVids);
  }

  function debounceRefresh() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(refresh, DEBOUNCE_MS);
  }

  function scrubToAsOf(s) {
    var t0 = windowStart;
    var t26 = t0 + 360;
    var t46 = t0 + 1560;
    var tend = windowEnd;
    if (s <= MARK_NAMED) return t0 + (s / MARK_NAMED) * 360;
    if (s <= MARK_WORLD) {
      return t26 + ((s - MARK_NAMED) / (MARK_WORLD - MARK_NAMED)) * 1200;
    }
    return t46 + ((s - MARK_WORLD) / (1000 - MARK_WORLD)) * (tend - t46);
  }

  function asOfToScrub(t) {
    var t0 = windowStart;
    var t26 = t0 + 360;
    var t46 = t0 + 1560;
    var tend = windowEnd;
    if (t <= t26) return (Math.max(t, t0) - t0) / 360 * MARK_NAMED;
    if (t <= t46) return MARK_NAMED + ((t - t26) / 1200) * (MARK_WORLD - MARK_NAMED);
    return MARK_WORLD + ((Math.min(t, tend) - t46) / Math.max(tend - t46, 1)) * (1000 - MARK_WORLD);
  }

  function pad(n) {
    return n < 10 ? "0" + n : String(n);
  }

  function utcParts(epoch) {
    var d = new Date(epoch * 1000);
    return {
      h: d.getUTCHours(),
      m: d.getUTCMinutes(),
      s: d.getUTCSeconds(),
      day: d.getUTCDate(),
      mon: d.getUTCMonth(),
      year: d.getUTCFullYear()
    };
  }

  var MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

  function formatClock(epoch) {
    var p = utcParts(epoch);
    return pad(p.h) + ":" + pad(p.m) + ":" + pad(p.s);
  }

  function formatDate(epoch) {
    var p = utcParts(epoch);
    return pad(p.day) + " " + MONTHS[p.mon] + " " + p.year + " · UTC";
  }

  function formatHM(epoch) {
    var p = utcParts(epoch);
    return pad(p.h) + ":" + pad(p.m);
  }

  function phaseFor(asOf) {
    if (asOf >= PZ.T46) return "the world found out";
    if (asOf >= PZ.T26) return "t+6min we would have named them";
    return "worm begins";
  }

  function prettyId(id) {
    if (!id) return "";
    return String(id)
      .replace(/^(mid|rid|wid|svc):/, "")
      .replace(/^(npm|pypi):/, "");
  }

  function ecoOf(id) {
    var s = String(id);
    if (s.indexOf("pypi:") === 0) return "pypi";
    if (s.indexOf("github:") === 0 || s.indexOf("rid:") === 0 || s.indexOf("wid:") === 0) return "gh";
    if (s.indexOf("mid:") === 0 || s.indexOf("npm:tanner") === 0) return "who";
    if (s.indexOf("svc:") === 0) return "svc";
    return "npm";
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function empty(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function noteStub(payloads) {
    var anyStub = false;
    for (var i = 0; i < payloads.length; i++) {
      if (payloads[i] && payloads[i].stub === true) {
        anyStub = true;
        break;
      }
    }
    var banner = $("banner");
    var text = $("banner-text");
    var tag = $("banner-tag");
    if (anyStub) {
      bannerLocked = true;
      if (banner) {
        banner.hidden = false;
        banner.classList.remove("is-degraded");
      }
      if (tag) tag.textContent = "SYNTHETIC";
      if (text) text.textContent = BANNER_COPY;
      document.body.classList.add("is-stub");
      document.body.classList.remove("is-degraded");
    } else {
      bannerLocked = false;
      document.body.classList.remove("is-stub");
      if (PZ.mode === "degraded") {
        if (banner) {
          banner.hidden = false;
          banner.classList.add("is-degraded");
        }
        if (tag) tag.textContent = "DEGRADED";
        if (text) text.textContent = DEGRADED_COPY;
        document.body.classList.add("is-degraded");
      } else {
        if (banner) {
          banner.hidden = true;
          banner.classList.remove("is-degraded");
        }
        document.body.classList.remove("is-degraded");
      }
    }
  }

  function fillQuery(preId, latId, payload) {
    var pre = $(preId);
    var lat = $(latId);
    if (pre) pre.textContent = (payload && payload.cypher) || "—";
    if (lat) {
      if (payload && typeof payload.latency_ms === "number") {
        lat.textContent = payload.latency_ms.toFixed(1) + " ms";
      } else {
        lat.textContent = "";
      }
    }
  }

  function pathRow(parts) {
    var wrap = el("div", "path");
    (parts || []).forEach(function (p, i) {
      if (i) wrap.appendChild(el("span", "path-arrow", "→"));
      var node = el("span", "path-node eco-" + ecoOf(p), prettyId(p));
      wrap.appendChild(node);
    });
    return wrap;
  }

  function isNullish(v) {
    return v == null || v === "" || (typeof v === "number" && !isFinite(v));
  }

  function renderUnmeasured(valueEl, barEl) {
    empty(valueEl);
    valueEl.appendChild(el("span", "ev-dash", "—"));
    valueEl.appendChild(el("span", "ev-unmeasured", "not yet measured"));
    valueEl.classList.add("is-null");
    if (barEl) {
      barEl.style.width = "0%";
      barEl.classList.add("is-null");
      if (barEl.parentElement) barEl.parentElement.classList.add("is-null");
    }
  }

  function renderMeasuredBar(valueEl, barEl, value) {
    empty(valueEl);
    valueEl.classList.remove("is-null");
    valueEl.textContent = typeof value === "number" ? value.toFixed(2) : String(value);
    if (barEl) {
      barEl.classList.remove("is-null");
      if (barEl.parentElement) barEl.parentElement.classList.remove("is-null");
      var pct = Math.max(0, Math.min(100, Number(value) * 100));
      barEl.style.width = pct + "%";
    }
  }

  function updateClock(asOf) {
    var clock = $("clock-time");
    var phase = $("phase");
    var date = $("clock-date");
    var scrub = $("scrub");
    if (clock) clock.textContent = formatClock(asOf);
    if (phase) {
      phase.textContent = phaseFor(asOf);
      phase.classList.remove("is-begin", "is-named", "is-world");
      if (asOf >= PZ.T46) phase.classList.add("is-world");
      else if (asOf >= PZ.T26) phase.classList.add("is-named");
      else phase.classList.add("is-begin");
    }
    if (date) date.textContent = formatDate(asOf);
    if (scrub) {
      scrub.setAttribute("aria-valuetext", formatClock(asOf) + " UTC — " + phaseFor(asOf));
      scrub.setAttribute("aria-valuenow", String(scrub.value));
    }
    document.body.classList.toggle("past-named", asOf >= PZ.T26);
    document.body.classList.toggle("past-world", asOf >= PZ.T46);
    document.body.classList.toggle("topo-trust", topology === "trust");
    document.body.classList.toggle("topo-dep", topology === "dependency");
  }

  function buildScrubMarks() {
    var host = $("scrub-marks");
    if (!host) return;
    empty(host);

    var gap = el("div", "scrub-gap");
    gap.style.left = MARK_NAMED / 10 + "%";
    gap.style.width = (MARK_WORLD - MARK_NAMED) / 10 + "%";
    gap.appendChild(el("span", "", "20 min the world did not know"));
    host.appendChild(gap);

    function mark(frac, label, extra) {
      var m = el("div", "scrub-mark" + (extra ? " " + extra : ""));
      m.style.left = frac + "%";
      m.appendChild(el("i", ""));
      m.appendChild(el("span", "", label));
      host.appendChild(m);
    }

    mark(0, "19:20  worm begins", "is-begin");
    mark(MARK_NAMED / 10, "19:26  we name them", "is-named");
    mark(MARK_WORLD / 10, "19:46  the world found out", "is-world");
    mark(100, formatHM(windowEnd), "is-end");
  }

  function layoutNodes(nodes) {
    var pos = {};
    var npm = nodes.filter(function (n) {
      return n.eco !== "pypi";
    });
    var pypi = nodes.filter(function (n) {
      return n.eco === "pypi";
    });
    npm.forEach(function (n, i) {
      if (n.role === "origin") {
        pos[n.id] = { x: 210, y: 280 };
        return;
      }
      var idx = i;
      var angle = -Math.PI * 0.72 + (idx / Math.max(npm.length - 1, 1)) * Math.PI * 1.44;
      var r = 78 + (idx % 5) * 26;
      pos[n.id] = {
        x: 210 + Math.cos(angle) * r,
        y: 280 + Math.sin(angle) * r * 0.92
      };
    });
    pypi.forEach(function (n, i) {
      pos[n.id] = { x: 560, y: 200 + i * 90 };
    });
    return pos;
  }

  function svgEl(tag, attrs) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) {
      n.setAttribute(k, attrs[k]);
    });
    return n;
  }

  function renderMap(asOf, forecast) {
    var edgeG = $("map-edges");
    var nodeG = $("map-nodes");
    var chrome = $("map-chrome");
    var emptyMsg = $("map-empty");
    var crossing = $("crossing");
    var count = $("map-count");
    if (!edgeG || !nodeG) return;

    empty(edgeG);
    empty(nodeG);
    if (chrome) empty(chrome);

    var liveNodes = clockNodes.length ? clockNodes : ((PZ.GRAPH && PZ.GRAPH.nodes) || []);
    var visible = liveNodes.filter(function (n) {
      return n.at <= asOf;
    });

    var edges = [];
    if (forecast && forecast.predictions) {
      var added = 0;
      forecast.predictions.forEach(function (p) {
        if (added >= 4) return;
        var exists = visible.some(function (n) {
          return n.id === p.pid;
        });
        if (!exists) {
          visible.push({
            id: p.pid,
            eco: p.pid.indexOf("pypi:") === 0 ? "pypi" : "npm",
            label: prettyId(p.pid),
            at: asOf,
            role: "pred"
          });
          added += 1;
        }
      });
      var visibleIds = {};
      visible.forEach(function (n) {
        visibleIds[n.id] = true;
      });
      forecast.predictions.forEach(function (p) {
        var prev = null;
        (p.justification_path || []).forEach(function (id) {
          if (!visibleIds[id]) return;
          if (prev && prev !== id) edges.push({ src: prev, dst: id, kind: "trust" });
          prev = id;
        });
      });
    }
    if (PZ.mode !== "live" && PZ.GRAPH && PZ.GRAPH.edges) {
      edges = edges.concat(PZ.GRAPH.edges);
    }

    if (count) count.textContent = visible.length ? visible.length + (visible.length === 1 ? " node" : " nodes") : "—";
    if (emptyMsg) emptyMsg.hidden = visible.length > 0;

    var hasPypi = visible.some(function (n) {
      return n.eco === "pypi";
    });
    if (crossing) {
      if (hasPypi) crossing.removeAttribute("hidden");
      else crossing.setAttribute("hidden", "");
    }

    if (chrome) {
      chrome.appendChild(
        svgEl("line", { x1: "430", y1: "24", x2: "430", y2: "536", "class": "eco-split" })
      );
      var npmL = svgEl("text", { x: "40", y: "36", "class": "eco-label" });
      npmL.textContent = "npm";
      var pyL = svgEl("text", { x: "448", y: "36", "class": "eco-label eco-label-pypi" });
      pyL.textContent = "PyPI";
      chrome.appendChild(npmL);
      chrome.appendChild(pyL);
    }

    if (!visible.length) return;

    var ids = {};
    visible.forEach(function (n) {
      ids[n.id] = n;
    });
    var pos = layoutNodes(visible);

    edges.forEach(function (e) {
      if (!ids[e.src] || !ids[e.dst]) return;
      var a = pos[e.src];
      var b = pos[e.dst];
      if (!a || !b) return;
      var mx = (a.x + b.x) / 2;
      var my = (a.y + b.y) / 2 - 18;
      var path = svgEl("path", {
        d: "M " + a.x + " " + a.y + " Q " + mx + " " + my + " " + b.x + " " + b.y,
        "class": "map-edge kind-" + e.kind,
        fill: "none"
      });
      edgeG.appendChild(path);
    });

    visible.forEach(function (n) {
      var p = pos[n.id];
      if (!p) return;
      var g = svgEl("g", {
        "class": "map-node role-" + n.role + " eco-" + n.eco,
        transform: "translate(" + p.x + " " + p.y + ")"
      });
      if (!seenNodes[n.id]) {
        g.classList.add("is-new");
        seenNodes[n.id] = true;
      }
      var r = n.role === "origin" ? 11 : n.role === "pred" ? 6 : 8;
      g.appendChild(
        svgEl("circle", {
          r: String(r),
          filter: n.role === "origin" || n.eco === "pypi" ? "url(#glow)" : ""
        })
      );
      var label = svgEl("text", { x: "12", y: "4", "class": "node-label" });
      label.textContent = n.label;
      g.appendChild(label);
      nodeG.appendChild(g);
    });
  }

  function renderRadius(payload, asOf) {
    var body = $("radius-body");
    var chip = $("radius-count");
    fillQuery("radius-cypher", "radius-lat", payload);
    if (!body) return;
    empty(body);
    var services = (payload && payload.services) || [];
    services = services.filter(function (s) {
      return typeof s.exposed_at !== "number" || s.exposed_at <= asOf;
    });
    if (chip) chip.textContent = services.length ? services.length + (services.length === 1 ? " service" : " services") : "—";
    if (!services.length) {
      body.appendChild(
        el(
          "p",
          "empty-line",
          "No reverse dependents in this slice. Lockfile pins are fetch-time, not 19:20."
        )
      );
      return;
    }
    services.forEach(function (s) {
      var row = el("article", "hit");
      var head = el("div", "hit-head");
      head.appendChild(el("strong", "hit-name", s.name || prettyId(s.sid)));
      if (s.exposed_at) head.appendChild(el("time", "hit-time", "exposed " + formatClock(s.exposed_at)));
      row.appendChild(head);
      row.appendChild(pathRow(s.path || []));
      body.appendChild(row);
    });
  }

  function renderForecast(payload) {
    var body = $("forecast-body");
    var chip = $("forecast-count");
    var panel = $("p-forecast");
    fillQuery("forecast-cypher", "forecast-lat", payload);
    if (panel) {
      panel.classList.toggle("is-trust", topology === "trust");
      panel.classList.toggle("is-dep", topology === "dependency");
    }
    if (!body) return;
    empty(body);
    var preds = (payload && payload.predictions) || [];
    var control = payload && payload.stats && payload.stats.is_negative_control;
    if (chip) chip.textContent = preds.length ? preds.length + " ranked" : "—";

    if (control) {
      body.appendChild(
        el("p", "control-note", "Negative control — identical query over dependency edges. Thesis: near-zero.")
      );
    }

    if (!preds.length) {
      var seedCount = payload && payload.stats && payload.stats.seeds;
      body.appendChild(
        el(
          "p",
          "empty-line",
          seedCount
            ? "No forecast paths in this bound."
            : "Seed set still forming. Scrub to 19:26 to name who falls next."
        )
      );
      return;
    }

    preds.forEach(function (p, i) {
      var row = el("article", "hit" + (control ? " is-control" : ""));
      var head = el("div", "hit-head");
      head.appendChild(el("span", "hit-rank", String(i + 1).padStart(2, "0")));
      head.appendChild(el("strong", "hit-name", prettyId(p.pid)));
      var score = el("span", "hit-score");
      score.textContent = typeof p.score === "number" ? p.score.toFixed(2) : "—";
      score.title = "Exclusivity × vector among seed traversals — not precision";
      head.appendChild(score);
      row.appendChild(head);
      row.appendChild(pathRow(p.justification_path || []));
      body.appendChild(row);
    });
  }

  function renderIndex(payload) {
    var body = $("index-body");
    var chip = $("index-count");
    fillQuery("index-cypher", "index-lat", payload);
    if (!body) return;
    empty(body);
    var cands = (payload && payload.candidates) || [];
    if (chip) chip.textContent = cands.length ? cands.length + " candidates" : "—";

    var rank = payload && payload.stats && payload.stats.true_origin_rank;
    if (isNullish(rank)) {
      var note = el("p", "unmeasured-line");
      note.appendChild(el("span", "ev-dash", "—"));
      note.appendChild(document.createTextNode(" true origin rank not yet measured"));
      body.appendChild(note);
    } else {
      body.appendChild(el("p", "verdict-line", "True origin ranked #" + rank));
    }

    if (!cands.length) {
      var obsCount = payload && payload.stats && payload.stats.observed;
      body.appendChild(
        el(
          "p",
          "empty-line",
          obsCount ? "No index-case paths in this bound." : "Not enough observations yet. Scrub to 19:26."
        )
      );
      return;
    }
    cands.forEach(function (c, i) {
      var row = el("article", "hit");
      var head = el("div", "hit-head");
      head.appendChild(el("span", "hit-rank", String(i + 1).padStart(2, "0")));
      head.appendChild(el("span", "kind-tag kind-" + (c.kind || ""), c.kind || "node"));
      head.appendChild(el("strong", "hit-name", prettyId(c.id)));
      var score = el("span", "hit-score");
      score.textContent = typeof c.score === "number" ? c.score.toFixed(2) : "—";
      head.appendChild(score);
      row.appendChild(head);
      row.appendChild(pathRow(c.path_to_observed || []));
      body.appendChild(row);
    });
  }

  function renderReach(payload) {
    var body = $("reach-body");
    var chip = $("reach-count");
    fillQuery("reach-cypher", "reach-lat", payload);
    if (!body) return;
    empty(body);
    var verdicts = (payload && payload.verdicts) || [];
    var stats = (payload && payload.stats) || {};
    var exec = typeof stats.findings_executing === "number" ? stats.findings_executing : verdicts.filter(function (v) {
      return v.tier === "install";
    }).length;
    if (chip) {
      chip.textContent = verdicts.length ? exec + " execute / " + verdicts.length : "—";
    }
    if (!verdicts.length) {
      body.appendChild(
        el(
          "p",
          "empty-line",
          "No install hooks on unpublished IOC tarballs; lockfiles are not live at this instant."
        )
      );
      return;
    }
    if (verdicts.length) {
      body.appendChild(
        el("p", "triage-sum", verdicts.length + " findings → " + exec + " that actually execute (install hook).")
      );
    }
    verdicts.forEach(function (v) {
      var row = el("article", "hit hit-triage tier-" + (v.tier || "none"));
      var head = el("div", "hit-head");
      head.appendChild(el("strong", "hit-name", prettyId(v.vid)));
      var tag = el("span", "tier-tag tier-" + (v.tier || "none"), (v.tier || "none").toUpperCase());
      head.appendChild(tag);
      row.appendChild(head);
      var why = el("p", "why");
      var ev = v.evidence || {};
      if (v.tier === "install") {
        var hooks = (ev.install_hooks || []).join(", ") || "install hook";
        why.textContent = "Runs at install: " + hooks + ".";
      } else {
        why.textContent = "No install hook — listed in the tree, does not execute at install.";
      }
      row.appendChild(why);
      body.appendChild(row);
    });
  }

  function renderEvidence(payload) {
    fillQuery("ev-cypher", "ev-lat", payload);
    var pt = $("ev-pt");
    var pd = $("ev-pd");
    var rt = $("ev-rt");
    var rd = $("ev-rd");
    var verdict = $("ev-verdict");
    var ptBar = $("ev-pt-bar");
    var pdBar = $("ev-pd-bar");

    var pTrust = payload && payload.precision_trust;
    var pDep = payload && payload.precision_dependency;
    var pT = pTrust && pTrust.precision_at_10;
    var pD = pDep && pDep.precision_at_10;

    if (!pt || !pd || !rt || !rd) return;

    if (isNullish(pT)) renderUnmeasured(pt, ptBar);
    else renderMeasuredBar(pt, ptBar, pT);

    if (isNullish(pD)) renderUnmeasured(pd, pdBar);
    else renderMeasuredBar(pd, pdBar, pD);

    function r0(elNode, value) {
      empty(elNode);
      if (isNullish(value)) {
        elNode.appendChild(el("span", "ev-dash", "—"));
        elNode.appendChild(el("span", "ev-unmeasured", "not yet measured"));
        elNode.classList.add("is-null");
      } else {
        elNode.classList.remove("is-null");
        elNode.textContent = Number(value).toFixed(2);
      }
    }
    r0(rt, payload && payload.r0_trust);
    r0(rd, payload && payload.r0_dependency);

    if (verdict) {
      empty(verdict);
      var measured = payload && payload.stats && payload.stats.measured;
      if (!measured) {
        verdict.appendChild(el("span", "ev-dash", "—"));
        verdict.appendChild(el("span", "ev-unmeasured", "not yet measured"));
        verdict.classList.add("is-null");
      } else {
        verdict.classList.remove("is-null");
        verdict.textContent = payload.note || "measured";
      }
    }

    var trustN = $("ctrl-trust-n");
    var depN = $("ctrl-dep-n");
    var ctrlVerdict = $("ctrl-verdict");
    var tPaths = payload && payload.trust_paths;
    var dPaths = payload && payload.control_paths;
    if (trustN) trustN.textContent = isNullish(tPaths) ? "—" : String(tPaths);
    if (depN) depN.textContent = isNullish(dPaths) ? "—" : String(dPaths);
    if (ctrlVerdict) {
      if (isNullish(tPaths) && isNullish(dPaths)) {
        ctrlVerdict.textContent = "Same query. Two topologies.";
      } else if (Number(tPaths) > 0 && Number(dPaths) === 0) {
        ctrlVerdict.textContent =
          "Trust returned " + tPaths + " paths. Dependency returned 0. The worm is visible on trust edges and invisible on dependency edges.";
      } else {
        ctrlVerdict.textContent =
          "Trust " + tPaths + " paths · dependency " + dPaths + " paths. Identical SSpaths, relTypes swapped.";
      }
    }
  }

  function renderLeverage(payload) {
    var body = $("leverage-body");
    var cut = $("leverage-cut");
    fillQuery("leverage-cypher", "leverage-lat", payload);
    if (!body) return;
    empty(body);
    var ranked = (payload && payload.ranked) || [];
    ranked.forEach(function (r) {
      var item = el("div", "lev-item");
      item.appendChild(el("span", "kind-tag kind-" + (r.kind || ""), r.kind || ""));
      item.appendChild(el("strong", "", prettyId(r.id)));
      var n = typeof r.packages_at_risk === "number" ? r.packages_at_risk : r.services_at_risk;
      if (typeof n === "number") {
        item.appendChild(el("span", "lev-n", n + (typeof r.packages_at_risk === "number" ? " pkg" : " svc")));
      }
      body.appendChild(item);
    });
    if (cut) {
      empty(cut);
      var blocked = payload && payload.stats && payload.stats.spread_blocked_pct;
      var reachable = payload && payload.stats && payload.stats.reachable_neighborhood;
      if (reachable == null) {
        reachable = payload && payload.stats && payload.stats.reachable_validation;
      }
      if (isNullish(blocked)) {
        if (reachable === 0) {
          cut.appendChild(el("span", "ev-unmeasured", "greedy cover: 0 packages in the trust neighborhood"));
        } else {
          cut.appendChild(el("span", "ev-unmeasured", "min-cut % not yet measured"));
        }
      } else {
        var method = (payload.stats && payload.stats.cover) || "greedy";
        cut.appendChild(
          el("span", "lev-n", method + " cover " + Math.round(Number(blocked) * 100) + "%")
        );
      }
      (payload.mincut || []).forEach(function (m) {
        var chip = el("span", "lev-cut-chip");
        chip.appendChild(el("b", "", m.action || m.kind));
        chip.appendChild(document.createTextNode(" · " + prettyId(m.id)));
        cut.appendChild(chip);
      });
    }
  }

  function setApiMode() {
    var node = $("api-mode");
    if (!node) return;
    node.classList.remove("is-live", "is-degraded");
    var health = PZ.health || {};
    var n = typeof health.catalog_nodes === "number" ? health.catalog_nodes : null;
    if (PZ.mode === "live") {
      node.textContent = n ? "LIVE · " + n.toLocaleString() + " nodes" : "LIVE";
      node.classList.add("is-live");
    } else if (PZ.mode === "degraded") {
      node.textContent = "DEGRADED";
      node.classList.add("is-degraded");
    } else {
      node.textContent = "MOCK";
    }
  }

  var evidenceOnce = null;
  var leverageOnce = null;

  function loadStablePanels() {
    if (!evidenceOnce) {
      evidenceOnce = PZ.fetchApi("/api/evidence").then(function (evidence) {
        noteStub([evidence]);
        renderEvidence(evidence);
        return evidence;
      }).catch(function (err) {
        evidenceOnce = null;
        console.error("evidence failed", err);
      });
    }
    if (!leverageOnce) {
      leverageOnce = PZ.fetchApi("/api/leverage").then(function (leverage) {
        renderLeverage(leverage);
        return leverage;
      }).catch(function (err) {
        leverageOnce = null;
        console.error("leverage failed", err);
      });
    }
  }

  function refresh() {
    var scrub = $("scrub");
    var asOf = scrubToAsOf(Number(scrub.value));
    updateClock(asOf);
    var seq = ++inflight;
    var seeds = seedsForClock(asOf);
    var vids = vidsForClock(asOf);

    function stillCurrent() {
      return seq === inflight;
    }

    function onPanel(fn) {
      return function (payload) {
        if (!stillCurrent()) return;
        noteStub([payload]);
        setApiMode();
        fn(payload);
      };
    }

    renderMap(asOf, null);

    PZ.fetchApi("/api/blast-radius", {
      method: "POST",
      body: {
        ecosystem: blast.ecosystem || "npm",
        name: blast.name || "@tanstack/react-query",
        version: blast.version || "5.101.4",
        window_start: PZ.WORM_START,
        window_end: asOf,
        max_hops: 6
      }
    }).then(onPanel(function (radius) {
      renderRadius(radius, asOf);
    })).catch(function (err) {
      console.error("blast failed", err);
    });

    PZ.fetchApi("/api/forecast", {
      method: "POST",
      body: { seeds: seeds, as_of: asOf, k: 8, topology: topology }
    }).then(onPanel(function (forecast) {
      renderForecast(forecast);
      renderMap(asOf, forecast);
    })).catch(function (err) {
      console.error("forecast failed", err);
    });

    PZ.fetchApi("/api/index-case", {
      method: "POST",
      body: { observed: seeds, as_of: asOf, k: 5 }
    }).then(onPanel(function (indexCase) {
      renderIndex(indexCase);
    })).catch(function (err) {
      console.error("index-case failed", err);
    });

    PZ.fetchApi("/api/reachability", {
      method: "POST",
      body: { sid: reachSid, finding_vids: vids, as_of: asOf }
    }).then(onPanel(function (reach) {
      renderReach(reach);
    })).catch(function (err) {
      console.error("reachability failed", err);
    });

    loadStablePanels();
  }

  function onScrubInput() {
    var asOf = scrubToAsOf(Number($("scrub").value));
    updateClock(asOf);
    debounceRefresh();
  }

  function stepScrub(dir, fine) {
    var scrub = $("scrub");
    var delta = fine ? 2 : 10;
    var next = Math.max(0, Math.min(1000, Number(scrub.value) + dir * delta));
    scrub.value = String(next);
    onScrubInput();
  }

  function bindForecastToggle() {
    var btns = document.querySelectorAll(".seg-btn");
    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        topology = btn.getAttribute("data-topology") || "trust";
        btns.forEach(function (b) {
          b.classList.toggle("is-on", b.getAttribute("data-topology") === topology);
        });
        document.body.classList.toggle("topo-trust", topology === "trust");
        document.body.classList.toggle("topo-dep", topology === "dependency");
        refresh();
      });
    });
  }

  var playTimer = 0;
  var playing = false;
  var PLAY_STOPS = [0, MARK_NAMED, MARK_WORLD];

  function stopPlay() {
    playing = false;
    clearTimeout(playTimer);
    var btn = $("play-clock");
    if (btn) {
      btn.textContent = "Play 19:20 → 19:46";
      btn.setAttribute("aria-pressed", "false");
    }
  }

  function togglePlay() {
    if (playing) {
      stopPlay();
      return;
    }
    playing = true;
    var btn = $("play-clock");
    if (btn) {
      btn.textContent = "Stop";
      btn.setAttribute("aria-pressed", "true");
    }
    var i = 0;
    function step() {
      if (!playing) return;
      if (i >= PLAY_STOPS.length) {
        stopPlay();
        return;
      }
      var scrub = $("scrub");
      scrub.value = String(PLAY_STOPS[i]);
      onScrubInput();
      i += 1;
      playTimer = setTimeout(step, 1600);
    }
    step();
  }

  function init() {
    buildScrubMarks();
    bindForecastToggle();
    var playBtn = $("play-clock");
    if (playBtn) playBtn.addEventListener("click", togglePlay);

    var scrub = $("scrub");
    scrub.addEventListener("input", onScrubInput);
    scrub.addEventListener("change", onScrubInput);

    document.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight" && e.key !== " ") return;
      var tag = (e.target && e.target.tagName) || "";
      if (tag === "INPUT" && e.target.type === "text") return;
      if (tag === "TEXTAREA") return;
      if (e.key === " ") {
        if (tag === "BUTTON" || tag === "INPUT") return;
        e.preventDefault();
        togglePlay();
        return;
      }
      e.preventDefault();
      stepScrub(e.key === "ArrowRight" ? 1 : -1, e.shiftKey);
    });
    PZ.probeLive().then(function () {
      setApiMode();
      noteStub(PZ.mode === "mock" ? [{ stub: true }] : []);
      return Promise.all([PZ.fetchApi("/api/timeline"), PZ.fetchApi("/api/meta")]);
    }).then(function (pair) {
      var tl = pair[0];
      var meta = pair[1];
      if (tl && typeof tl.window_end === "number") windowEnd = tl.window_end;
      if (tl && typeof tl.window_start === "number") windowStart = tl.window_start;
      if (tl && tl.nodes && tl.nodes.length) clockNodes = tl.nodes;
      if (meta && meta.default_blast) blast = meta.default_blast;
      if (meta && meta.default_sid) reachSid = meta.default_sid;
      if (meta && meta.seed_pids && meta.seed_pids.length) seedPids = meta.seed_pids;
      if (meta && Array.isArray(meta.finding_vids)) findingVids = meta.finding_vids;
      noteStub([tl, meta]);
      buildScrubMarks();
      updateClock(scrubToAsOf(Number(scrub.value)));
      refresh();
    }).catch(function () {
      updateClock(scrubToAsOf(Number(scrub.value)));
      refresh();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
