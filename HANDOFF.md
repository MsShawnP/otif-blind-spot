# OTIF Blind Spot — Handoff Log

Session-by-session state. Updated by /log mid-session and /wrap at
session end.

For durable choices, see DECISIONS.md.
For the current work arc, see PLAN.md.
For things that didn't work, see FAILURES.md.

---

## 2026-05-31 — Project initialized

**Started from:** New project setup via /new-project.

**Did:** Created repo, set up CLAUDE.md/DECISIONS.md/HANDOFF.md/PLAN.md/
FAILURES.md, src/ and tests/ CLAUDE.md files, README.md, .gitignore.
Git initialized, GitHub private remote created, tagged v0.1-foundation.
Project brief (portfolio_project_brief_otif_blind_spot.md) already present.

**State:** Foundation in place. PLAN.md arc defined. Stack TBD — to be
scoped during planning phase. Brief is complete (Section 10 open question
about synthetic Walmart scorecard data remains open).

**Next:** Run /clarify to scope the work, then /ce:brainstorm for the spec.

---

## 2026-05-31 15:30

**What changed:** Completed /clarify, /ce:brainstorm, and /ce:plan — full planning phase done.

**Why:** Building the OTIF Blind Spot portfolio piece from scratch; needed scope, spec, and implementation plan before coding.

**State:** Requirements doc at `docs/brainstorms/otif-blind-spot-requirements.md`, implementation plan at `docs/plans/2026-05-31-001-feat-otif-blind-spot-portfolio-piece-plan.md` (7 units, doc-reviewed). 2 safe-auto fixes applied; 10 proposed fixes and 8 decisions remain open in plan review output. No code written yet.

**Next:** Start /ce:work — resolve the three P1 decisions first (JSON path src/data vs public/data, Observable Plot override of R12, velocity damage formula definition), then implement U2 (data generation pipeline).

---

## 2026-05-31 16:00

**Started from:** New project with only the portfolio brief present. No git, no state files, no plan.

**Did:** Full planning phase — /new-project scaffold, /clarify (stack + scope), /ce:brainstorm (requirements doc), /ce:plan (7-unit implementation plan + headless doc review). 18 doc-review findings: 2 auto-fixed, 10 proposed fixes + 8 decisions outstanding. Pushed and tagged v0.2-planning.

**State:** Planning complete. No application code. `docs/brainstorms/otif-blind-spot-requirements.md` and `docs/plans/2026-05-31-001-feat-otif-blind-spot-portfolio-piece-plan.md` committed and pushed. Key discovery: Cinderhaven has no MABD, no 855 layer, no po_qty column — OTIF data must be fully synthesized in Python.

**Next:** Before /ce:work — resolve 3 P1 plan decisions: (1) add R10 override note in U2 for src/data path, (2) add R12/Key Decisions override note for Observable Plot, (3) define velocity damage formula in otif_config.py. Then start U2 (data generation pipeline).

---

## 2026-05-31 17:41

**What changed:** /ce:work complete — all 7 implementation units shipped (51 tests, build passing, pushed).

**Why:** Full portfolio piece built end-to-end: React/TS/Vite/Cloudflare Workers frontend with Observable Plot charts, Python data pipeline, and complete Lailara Design System v2 styling.

**State:** All application code committed and pushed. Placeholder JSON in `frontend/src/data/` works at build time. Pipeline scripts written but not yet run against the live Cinderhaven DB. `VELOCITY_DAMAGE_PER_UNIT_GAP = 3.50` in `scripts/otif_config.py` is a placeholder — needs tuning after first real pipeline run. Deploy step (U7) is wired but not executed (needs `flyctl proxy` + Cloudflare auth).

**Next:** Start DB proxy (`flyctl proxy 5432 -a cinderhaven-db`), run `cd frontend && npm run pipeline`, check `pytest tests/test_data_integrity.py`, tune `VELOCITY_DAMAGE_PER_UNIT_GAP` if $320K target is off, then `npm run deploy`.

---

## 2026-05-31 18:36

**What changed:** Deployed to Cloudflare Workers; token colors corrected against official design system repo.

**Why:** Arc complete — all 7 definition-of-done criteria met. Two token hex values were wrong vs LAILARA_DESIGN_SYSTEM.md (fail-bg, info-bg); fixed and redeployed.

**State:** Live at otif-blind-spot.msshawnp.workers.dev. 10,201 orders, 18 integrity tests pass, 51 frontend tests pass. All tokens trace to design system. Arc fully shipped.

**Next:** `/ce:review` the diff, then `/ce:compound` to extract pipeline synthesis patterns into docs/solutions/.

---

## 2026-05-31 18:40 — Session close

**Started from:** Planning complete, no code. Three P1 decisions outstanding.

**Did:** Full /ce:work (7 units) — React/TS/Vite/Cloudflare frontend, Python OTIF synthesis pipeline, 5 analytical moves, EDI Audit Sheet. Ran pipeline against live Cinderhaven DB (10,201 orders). Tuned synthesis to hit 95%/86% targets. Fixed 2 token hex errors vs design system. Deployed live.

**State:** Live at otif-blind-spot.msshawnp.workers.dev. All 7 definition-of-done criteria met. 51 frontend + 18 integrity tests pass. No broken states.

**Next:** Fix EDI Audit Sheet horizontal scroll first (columns overflow viewport — needs layout fix), then `/ce:review`, then `/ce:compound`.

---

## 2026-05-31 21:35 — Session close

**Started from:** Post-ship, arc complete. Ran /improve — deferred EDI Audit Sheet scroll fix from previous session was the primary user concern.

**Did:** Full /improve pass (audit + 6 fixes). Fixed EDI Audit Sheet: eliminated all horizontal scrolling (overflow: hidden, table-layout: fixed, colgroup with % widths). Fixed header-clipping regression introduced during the scroll fix (removed white-space: nowrap from .audit-th). Added overflow-wrap: break-word to data cells. Drove colgroup from COLUMNS array (added width field to Column interface). Filled README Stack/How-to-run sections. Fixed DATABASE_URL fallback to fail fast on missing credentials. Removed unused DEMO_DATE export. Updated docs/solutions/ doc to document Strategy B and when to use each approach. npm audit: 0 vulnerabilities. Build passes, 51/51 tests pass.

**State:** Fully clean. All 6 improvement items resolved. No broken states, no deferred items. Unpushed commits on main.

**Next:** Nothing pending on this project. Deploy improvement changes (`npm run deploy` from frontend/) or start next Lailara workstream.

---

## 2026-05-31 23:30 — Session close

**Started from:** Post-ship. Live at otif-blind-spot.msshawnp.workers.dev. One deferred item: EDI Audit Sheet columns overflowing the viewport (page-level horizontal scroll).

**Did:** Fixed EDI Audit Sheet horizontal scroll (`min-width: 0` on flex item, `min-width: 100%` on table — 2 CSS property changes). Ran `/ce:review` (6 reviewers, clean, Ready to merge). Ran `/ce:compound` (Full + session history) — created `docs/solutions/ui-bugs/flex-min-width-table-scroll-bypass-2026-05-31.md`. Updated CLAUDE.md to surface `docs/solutions/` to future agents. Pushed 2 commits.

**State:** Arc fully complete. Live, clean, pushed. `docs/solutions/` initialized. No open bugs, no deferred items.

**Next:** Arc is done — nothing pending. Good starting points: `/improve` on the project, scope the next Lailara workstream, or start a new portfolio piece.

---

## 2026-06-19 20:30 — Session close

**Started from:** Arc complete and shipped. Resumed mid-task from context restore — three UI changes in progress (preset selector, audit sheet nowrap, shared window state). Data pipeline exports and type definitions already done; computeMetrics.ts was next.

**Did:** Created `computeMetrics.ts` (client-side metric recomputation mirroring Python pipeline). Rewrote `App.tsx` with window state, `WindowPresetBar`, computed data flow to both tabs. Fixed EDI Audit Sheet: removed table-layout:fixed/colgroup/width percentages, added white-space:nowrap on date/PO columns, widened container by moving max-width from `.app-main` to `.reconciliation-view`. Built, deployed, committed (`1deaf10`), pushed. Analyzed synthetic OTIF plausibility — 62% in-full is unrealistically low (median shortfall 28% of PO). Flagged data tuning for cinderhaven-data-platform session.

**State:** All features working and deployed at otif.lailarallc.com. Preset buttons (13w/26w/52w/full) filter all figures client-side. Audit sheet uses full page width, no horizontal scroll. Two DECISIONS.md entries superseded (table-layout:fixed and colgroup-driven). Spawned task chip for data platform to tune failure rates.

**Next:** No code work pending on otif-blind-spot. Deferred: (1) CINDERHAVEN_CANONICAL.md update batched with short-ship-cost, (2) README narrative prose awaiting Shawn's replacement text, (3) .env revert to prod is separate deliberate step. Data plausibility fix lives in cinderhaven-data-platform (spawned task). Project due for `/improve` review (last was 2026-05-31, next due 2026-06-30).

---

## 2026-06-23 — Pre-demo verification and exposure scope label

**Started from:** Post data-platform tuning. Canonical figures: 99.2% internal / 84.5% Walmart OTIF / 14.8pt gap / $57K total exposure. Stale figures scattered across README, CLAUDE.md, PLAN.md, index.html meta tags.

**Did:**
1. **Stale figure grep** — found old figures (92%/61%/95%/86%/$55K/$368K/$423K) in README, CLAUDE.md, PLAN.md, index.html meta tags. Data JSON files confirmed matching canonical.
2. **Updated all stale figures** (`86efd1a`) — README tables, headline, root causes, exposure, overlap note. CLAUDE.md and PLAN.md business questions. Meta/OG/Twitter descriptions from 95%/86% to 99%/85%. og:url from workers.dev to otif.lailarallc.com. Removed per-retailer table (no per-retailer data in current pipeline).
3. **Exposure pin and revert** — initially pinned exposure to full-corpus static data (`b81e7a9`) to fix $59K vs $57K discrepancy on 52w default. User requested revert — exposure should float with window. Reverted (`8d02d99`), added scope footnote ("Annualized from last N weeks." / "Annualized from full observation period.") under exposure cards.
4. **Verified** all four presets (13w/26w/52w/full) show internally consistent fines + velocity = total. Scope label updates with each selection.

**State:** All figures canonical across repo. Exposure floats with window preset, scope label communicates the annualization period. Deployed to Cloudflare, pushed to main. No broken states.

**Next:** No code work pending. Deferred: (1) CINDERHAVEN_CANONICAL.md update batched with short-ship-cost, (2) README narrative prose awaiting Shawn's replacement text, (3) .env revert to prod is separate deliberate step. Project due for `/improve` review (last was 2026-05-31, next due 2026-06-30).

---

## 2026-07-30 — Triple-review improvement pass (16 commits, deployed)

**Started from:** Post-ship, live at otif.lailarallc.com. User ran /improve + /ce code review + /ui review. Another session's lailara-frame.css change was in flight — committed as a13d1a6 and pushed at session start.

**Did:** Ran all three reviews (security, correctness, maintainability, testing, kieran-typescript, project-standards + ui-review-skill). Resolved every substantive finding in 16 verified commits, pushed and auto-deployed:
- Windowing consistency: floated headline exposure, Move 4 delta, and Move 5 prose with the selected preset (were hardcoded full-corpus while tiles were windowed — two exposure totals on one screen).
- Pagination: reset audit-sheet page index on rows-prop change (stale page → false "no matches").
- Honesty: relabeled Move 4 "True Fill" from EDI-855 order-trimming to shipping-dock vs receiving-dock fill. The pipeline remaps units_shipped→acknowledged_units, units_received→shipped_units, so the delta is loss between docks, not trimming (data has no ack layer). Fixed audit column headers (Shipped/Received) and CLAUDE.md root-cause list.
- Dead code: otif_fine, retailer_penalty_flag, PlotChart.svgTitle, data-decomp-total, magic-9 decomposition fallback, dead DATABASE_URL/REDACTED branch, duplicate .env loader.
- Quality: RootCauseKey union type; tokens.css hex→var in ReconciliationView.css.
- Tests: computeMetrics.test.ts — Python↔TS parity suite + edge/empty-window + exposure-math value assertions (63 frontend tests, was 50).
- Docs: README stack (Observable Plot/Workers/correct tables), CLAUDE.md TBDs, 84.5%/14.8pt figure alignment.

**State:** Live and clean. tsc + 63 frontend/29 python tests + build all green, security clean. Windowing consistency + Move 4 relabel verified on the live bundle across 52w/13w presets. origin/main = d1ae53c.

**Next:** Deferred — adopt lailara-frame .ll-measure prose classes so the page abides by the brand frame (needs Browser pane displayed for visual sign-off at 1440px + 375px; task chip task_3b7ad9a1). Intentionally skipped: JSON runtime validation in data.ts (parity test is the stronger guard). Housekeeping: next pipeline regen strips the orphaned otif_fine/retailer_penalty_flag keys from audit_rows.json.

---

## 2026-07-30 — lailara-frame prose-measure adoption (deployed)

**Started from:** Sole deferred item from the triple-review pass — adopt the `lailara-frame.css` `.ll-measure` prose classes so the page abides by the brand frame. Deferred because the Browser pane couldn't composite screenshots for visual sign-off. origin/main at `d1ae53c`.

**Did:** Applied frame measure classes to the three running-prose surfaces — `.recon-section__framing` + `.recon-footnote` → `ll-measure` (720px), both `.headline-hook__gap` → `ll-measure-narrow` (560px). Removed the hardcoded `max-width` from each element's component CSS (frame stylesheet loads first, so the component rule was winning the cascade and would have no-op'd the utility class — the conflict the task flagged). Rebased onto an advanced origin/main (+2 commits); one Move 4 conflict resolved by keeping main's floated-figure text plus `ll-measure`. Pushed to main (`8a87996`), Cloudflare deploy green, fast-forwarded the root main worktree.

**State:** Live and clean. `main` = `8a87996`. Build clean, 63 frontend tests pass, no console errors. Verified via computed geometry (screenshots still can't composite this session): measures resolve to 560/720px at 1440px, no horizontal overflow at 375px. Sibling surfaces: all 3 running-prose types checked and converted; non-prose chart labels/captions deliberately excluded as out of scope.

**Next:** No code work pending. Housekeeping carried forward: next pipeline regen strips orphaned `otif_fine`/`retailer_penalty_flag` keys from `audit_rows.json`. Next `/improve` due 2026-08-27.

---
