# W4 — Demo / Frontend / Submission

**Read [`HANDOFF.md`](./HANDOFF.md) §3 (disqualification rules), §4 (API contract), §5 (timeline).**
Design detail: [`DESIGN.md`](./DESIGN.md) §7.

**You own:** the split-screen clock UI, the README, the demo video, and **submission mechanics**.
**You are blocked by:** nothing — W2 ships stub endpoints Day 1, mock them until then.
**You block:** nothing. But you own the only *fatal* risk in the register.

---

## You own the fatal risk

Risk #8: missing video, private repo, no license, or late submission = **automatic
disqualification**, regardless of how good the engine is. Everything else on this project is a
scoring risk. Yours is a zero.

**Day 0, before anything else:**
- [ ] Fresh **public** GitHub repo created
- [ ] **Apache-2.0 LICENSE** committed
- [ ] README skeleton committed
- [ ] `ATTRIBUTION.md` started — add every third-party source as it is introduced, not on Day 6

Submission requirements satisfied on day one, not hour 143.

---

## The UI

A triage product, not a notebook. Split-screen with a clock pinned to the real May 11 timestamps.

```
  19:20 ──────────────────────────── 19:26 ──────────────────────── 19:46
  LEFT  │ worm spreads across the TRUST topology
  RIGHT │ t+6min → forecast names the next victims
        │       → blast radius lights up exposed services
        │       → reachability filters to the ones that actually execute
  ─────────────────────────────────────────────────────────────────
  Overlay at 19:46: "The world found out here."
```

The emotional beat is the gap between **19:26** (when we would have named the next victims) and
**19:46** (when the world actually noticed). Build the timeline so that gap is impossible to miss.

**Three panels, driven by the three API endpoints:**
1. **Blast radius** — exposed services with the dependency path that exposed each one, and the
   timestamp it became exposed. Paths must be visible; the path *is* the evidence.
2. **Forecast** — ranked predicted-next packages, each with its **justifying trust path**
   (shared maintainer / repo / workflow / OIDC). An unexplained ranking is not a product.
3. **Reachability** — the alert-triage collapse. Show the tier (`install` / `import` / `call` /
   `none`) for each finding. "3,000 → 4" is only credible if a judge can see *why* each was cut.

**Mock the API from hour one.** Contract is fixed in [`HANDOFF.md`](./HANDOFF.md) §4 and will not
change. W2 ships correctly-shaped stubs on Day 1; swap to the real server on Day 4.

---

## The video — 3 minutes or less, hard limit

| Segment | Time | Content |
|---|---|---|
| Problem | 0:30 | TanStack worm. 42 packages in 6 minutes. 170+ by end of day. It crossed npm→PyPI. |
| Insight | 0:30 | **Radius travels down dependency edges. Forecast travels along CI/maintainer edges.** The npm→PyPI jump is impossible along dependency edges — that is the proof. |
| Demo | 1:30 | The clock. Live, on real data. This is the whole video; the rest is framing. |
| HydraDB + numbers | 0:30 | Native `algo.SSpaths`, three topologies, the real element count, precision@K, the alert-collapse ratio. |

**Rules for the numbers:** every figure spoken is a measured figure. The element count is whatever
W1 actually loaded — *"a 1.8M-element ecosystem slice,"* never *"14M nodes."* If the forecast
underperformed, say the real number. Judges built this database and will know.

**Record Day 5.** Day 6 is for re-recording, not first-recording.

---

## The README — a judging surface, not a formality

Required by the rules: setup instructions, HydraDB integration explanation, license, attribution.

What actually scores:

- **Explain how HydraDB does real work.** The rule says it must not "just sit in the README."
  Name the native procedures used, show a real query, and explain the three topologies.
- **Show you read their benchmarks.** State that the architecture — offline resolution, one
  single-threaded loader, all cleverness at read time — was designed around their measured
  ~225 ops/sec write ceiling and their supernode fanout limits. This is a "use of HydraDB"
  scoring moment that costs one paragraph.
- **Publish the reconciled IOC list** (W3's artifact) as a genuine community contribution.
- **Report results honestly**, including anything that underperformed.

**Day 6: dry-run the setup instructions on a clean machine.** Instructions that only work on the
author's laptop are the most common way a strong project loses "product completeness."

---

## Definition of done

- [ ] Public repo + Apache-2.0 + README skeleton + `ATTRIBUTION.md` (**Day 0**)
- [ ] UI scaffold and clock component against mocked API (**Day 3**)
- [ ] Split-screen wired to real data (**Day 4**)
- [ ] 🔒 **Feature freeze end of Day 4**
- [ ] README complete with real measured numbers (**Day 5**)
- [ ] Video recorded, **≤3:00** (**Day 5**)
- [ ] Setup instructions dry-run on a clean machine (**Day 6**)
- [ ] **Google Form submitted by 2 PM PT Aug 20** (**Day 6**)

## Traps

- Waiting for a real API. Mock it Day 1.
- A video over 3:00. Hard limit — time it.
- Numbers in the video that nobody measured.
- Leaving the repo private until Day 6.
- Submitting at 11:59 PM. The form is a single point of failure and late is fatal.
- Adding features after the Day 4 freeze.

## Suggested skills

`browse` (QA the UI, capture screenshot evidence — **never** `mcp__claude-in-chrome__*`) ·
`frontend-design` or `ui-ux-pro-max` (the demo is a judging surface) ·
`superpowers:verification-before-completion` (before submitting)
