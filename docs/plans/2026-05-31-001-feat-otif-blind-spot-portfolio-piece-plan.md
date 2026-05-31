---
date: 2026-05-31
plan_id: 2026-05-31-001
status: active
origin: docs/brainstorms/otif-blind-spot-requirements.md
---

# feat: Build OTIF Blind Spot — interactive diagnostic portfolio piece

## Summary

Build the OTIF Blind Spot portfolio piece end-to-end: a Python data generation pipeline that synthesizes a Walmart OTIF scorecard from the Cinderhaven platform, exports static JSON baked into the frontend at build time, and a React/TypeScript/Observable Plot app with two views — the Retailer Reconciliation Matrix and the EDI Audit Sheet — deployed to Cloudflare Workers.

---

## Problem Frame

Cinderhaven's internal dashboard shows 95% fill rate. Walmart's OTIF scorecard shows 86%. The 9-point gap is real, expensive (~$460K/year), and invisible because the brand has never put both numbers side by side. The gap splits 5/4: five points are on-time failures (logistics) and four points are in-full failures (production short-ships + order trimming). Brands routinely fix the wrong one. This piece reveals the gap, decomposes it, attributes root causes, and prices the full exposure — diagnostic intelligence that redirects remediation from assumption to evidence.

(see origin: `docs/brainstorms/otif-blind-spot-requirements.md` — Problem Frame)

---

## System-Wide Impact

- **Cinderhaven data platform** — read-only access to `fct_retailer_orders`, `fct_retailer_shipments`, `sku_costs`, `product_master`, `retailer_rules`. No schema changes to the platform.
- **Scripts directory** — new `scripts/` at project root. Requires live Cinderhaven PostgreSQL connection (`flyctl proxy 5432 -a cinderhaven-db`) to generate data; all generated artifacts are committed JSON files.
- **Frontend** — new `frontend/` directory, self-contained React app. No server-side logic; pure static assets served via Cloudflare Workers.
- **where-the-money-comes-from** — `PlotChart.tsx` and pattern references copied from this sibling project. Not modified.

---

## High-Level Technical Design

*This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

```
Cinderhaven PostgreSQL (Fly.io)
    │  flyctl proxy 5432 -a cinderhaven-db
    ▼
scripts/00_query_cinderhaven.py
    → reads fct_retailer_orders, fct_retailer_shipments,
      sku_costs × product_master, retailer_rules
    → writes scripts/cache/cinderhaven_snapshot.json
    │
    ▼
scripts/01_synthesize_otif.py
    → reads snapshot, generates:
        - MABD per order (= requested_ship_date + 2 days)
        - on_time_result (delivery_date <= MABD)
        - on_time_root_cause (warehouse_late | carrier_late)
        - acknowledged_qty (po_qty × ack_rate, seeded to trim ~40% of in-full gap)
        - in_full_result (shipped_qty >= acknowledged_qty)
        - in_full_root_cause (short_ship | order_trimming)
        - cogs (units × case_pack_qty × cogs_per_unit)
        - otif_fine (3% × cogs when !on_time || !in_full, Walmart orders only)
    → writes scripts/cache/otif_synthetic.json
    │
    ▼
scripts/02_export_json.py
    → aggregates to 5 data files
    → writes to frontend/src/data/
         summary.json          ← headline numbers + decomposition
         root_causes.json      ← on-time + in-full root cause attribution
         true_fill.json        ← 850 vs 855 fill rate comparison
         exposure.json         ← fines + velocity damage
         audit_rows.json       ← transaction-level rows for EDI Audit Sheet
    │
    ▼
frontend/src/data/*.json  ← imported by TypeScript at Vite build time
    │
    ▼
React App (frontend/src/)
    ├── App.tsx  ── chapter state (1 | 2), data imports, headline hook
    ├── ChapterNav  ── "Reconciliation Matrix" | "EDI Audit Sheet"
    ├── chapters/ReconciliationView/
    │   ├── Headline: 95% vs 86% reveal
    │   ├── DualDockChart (Move 1)     ← Observable Plot bar comparison
    │   ├── DecompositionChart (Move 2) ← Observable Plot stacked/grouped bar
    │   ├── RootCauseChart (Move 3)    ← Observable Plot bar with click-to-pin
    │   ├── TrueFillSection (Move 4)   ← Observable Plot comparison
    │   └── ExposureSection (Move 5)   ← KPI tiles + narrative
    └── chapters/AuditSheetView/
        └── Interactive sortable/filterable table (native HTML <table>)
    │
    ▼
wrangler deploy → otif-blind-spot.msshawnp.workers.dev
```

**Click-to-pin pattern** (applies to RootCauseChart, expandable to any chart):
- `useState<string | null>(null)` for `pinnedId`
- `Object.fromEntries(rows.map(r => [r.id, r]))` for lookup map
- Non-pinned bars: `opacity: 0.3`, `transition: opacity 200ms ease-out`
- Pinned card: dark card (`#1a1a1a` background) above the chart with root-cause detail
- Guard: `pinnedId && barById[pinnedId]` (Record returns `T | undefined`)
- `prefers-reduced-motion`: skip transition, snap to state

(see origin: `docs/brainstorms/otif-blind-spot-requirements.md` — R13; pattern from `published/where-the-money-comes-from/src/components/PlotChart.tsx`)

---

## Output Structure

```
otif-blind-spot/
├── scripts/
│   ├── otif_config.py              # shared constants (RNG seed, date window, Walmart ID)
│   ├── 00_query_cinderhaven.py     # connect + query existing marts → cache/
│   ├── 01_synthesize_otif.py       # generate MABD, 855, OTIF scorecard → cache/
│   ├── 02_export_json.py           # aggregate → frontend/src/data/
│   └── run_pipeline.py             # orchestrate 00 → 01 → 02
├── scripts/cache/                  # gitignored intermediate files
├── tests/
│   └── test_data_integrity.py      # validate JSON shapes + numeric claims
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── App.css                 # global layout + component styles
│   │   ├── index.css               # reset only (html/body/#root margins)
│   │   ├── tokens.css              # all CSS custom properties / design tokens
│   │   ├── vite-env.d.ts
│   │   ├── test-setup.ts
│   │   ├── types.ts
│   │   ├── data.ts
│   │   ├── data/                   # baked JSON (Vite imports at build time)
│   │   │   ├── summary.json
│   │   │   ├── root_causes.json
│   │   │   ├── true_fill.json
│   │   │   ├── exposure.json
│   │   │   └── audit_rows.json
│   │   ├── components/
│   │   │   ├── ChapterNav.tsx
│   │   │   ├── ChapterNav.css
│   │   │   ├── PlotChart.tsx       # copied from where-the-money-comes-from
│   │   │   └── PlotChart.test.tsx
│   │   ├── chapters/
│   │   │   ├── ReconciliationView/
│   │   │   │   ├── ReconciliationView.tsx
│   │   │   │   ├── ReconciliationView.css
│   │   │   │   ├── ReconciliationView.test.tsx
│   │   │   │   └── domain.ts       # shared business logic + constants
│   │   │   └── AuditSheetView/
│   │   │       ├── AuditSheetView.tsx
│   │   │       ├── AuditSheetView.css
│   │   │       └── AuditSheetView.test.tsx
│   │   └── utils/
│   │       ├── format.ts           # formatDollars, formatPercent, formatPts
│   │       └── format.test.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   └── wrangler.jsonc
└── [existing state files: PLAN.md, HANDOFF.md, etc.]
```

---

## Implementation Units

### U1. Frontend scaffold

**Goal:** Create the complete `frontend/` project structure with all config files, design tokens, fonts, and a passing `npm test` / `npm run build` before any feature code exists.

**Requirements:** R14 (self-hosted fonts), R15 (Lailara Design System tokens), R16 (Cloudflare Workers build/deploy)

**Dependencies:** None

**Files:**
- `frontend/package.json`
- `frontend/tsconfig.json`, `frontend/tsconfig.app.json`, `frontend/tsconfig.node.json`
- `frontend/vite.config.ts`
- `frontend/wrangler.jsonc`
- `frontend/src/main.tsx`
- `frontend/src/index.css`
- `frontend/src/tokens.css`
- `frontend/src/App.css`
- `frontend/src/App.tsx` (stub — renders "OTIF Blind Spot" heading)
- `frontend/src/vite-env.d.ts`
- `frontend/src/test-setup.ts`
- `frontend/src/App.test.tsx` (smoke: renders without crash)
- `frontend/public/favicon.svg`

**Approach:**
- `package.json` mirrors `where-the-money-comes-from` scripts: `dev`, `build` (tsc -b && vite build), `test` (vitest run), `preview` (build + wrangler dev), `deploy` (build + wrangler deploy). Add a `pipeline` script and a `prebuild` that runs `cd ../scripts && python run_pipeline.py`.
- Dependencies: `react`, `react-dom`, `@observablehq/plot`, `@fontsource/playfair-display`, `@fontsource/source-sans-3`. Dev: `vite`, `@vitejs/plugin-react`, `@cloudflare/vite-plugin`, `typescript`, `vitest`, `jsdom`, `@testing-library/react`.
- `vite.config.ts`: `plugins: [react(), cloudflare()]`, vitest inline with `environment: "jsdom"`, `setupFiles: ["./src/test-setup.ts"]`. Import from `vitest/config` (not `vite`).
- `wrangler.jsonc`: `name: "otif-blind-spot"`, `compatibility_date: "2026-05-31"`, `assets: { not_found_handling: "single-page-application" }`, `compatibility_flags: ["nodejs_compat"]`, `observability: { enabled: true }`.
- `tsconfig.app.json`: mirror retailer-deduction-recovery — `verbatimModuleSyntax: true`, `erasableSyntaxOnly: true`, `strict: true`, `noUnusedLocals: true`, `noUnusedParameters: true`.
- `tokens.css`: all Lailara Design System v2 CSS custom properties (`--ink`, `--ink-soft`, `--bg`, `--canvas`, `--accent`, `--accent-red`, `--teal-*`, `--serif`, `--sans`, etc.). Verify every hex value against `published/lailara-design-system/LAILARA_DESIGN_SYSTEM.md`. No hex values anywhere except `:root`.
- Fonts imported in `main.tsx` via `@fontsource` (not CSS `@import`).

**Patterns to follow:**
- `published/where-the-money-comes-from/src/tokens.css` for token structure
- `published/retailer-deduction-recovery/frontend/wrangler.jsonc` for Cloudflare config
- `published/retailer-deduction-recovery/frontend/tsconfig.app.json` for TypeScript strictness

**Test scenarios:**
- App stub renders without throwing (smoke)
- `npm run build` exits 0 (TypeScript passes, Vite bundles)
- `npm test` exits 0 with the smoke test passing
- Token file: grep for bare hex values in `src/*.css` returns zero matches outside `:root`

**Verification:** `npm run build` succeeds with no TypeScript errors; `npm test` passes; `wrangler dev` serves the stub on localhost.

---

### U2. OTIF data generation pipeline

**Goal:** Python scripts that query the Cinderhaven platform, synthesize all OTIF-specific data that doesn't exist in the platform (MABD, 855 acknowledgments, OTIF scorecard), and export five static JSON files to `frontend/src/data/`. The exported data must reproduce the brief's exact figures: 95% internal fill, 86% retailer OTIF, 5-point on-time gap, 4-point in-full gap, ~$140K fines, ~$320K velocity damage.

**Requirements:** R8, R9, R10, R17 (see origin: `docs/brainstorms/otif-blind-spot-requirements.md`)

**Dependencies:** None (standalone; Cinderhaven DB must be accessible via `flyctl proxy 5432`)

**Files:**
- `scripts/otif_config.py`
- `scripts/00_query_cinderhaven.py`
- `scripts/01_synthesize_otif.py`
- `scripts/02_export_json.py`
- `scripts/run_pipeline.py`
- `scripts/cache/.gitkeep` (cache dir exists, contents gitignored)
- `tests/test_data_integrity.py`
- `.gitignore` (add `scripts/cache/*.json`)
- `requirements_scripts.txt`

**Approach:**

*`otif_config.py`*: Shared constants — `WALMART_RETAILER_ID`, `RNG_SEED = 100` (matching Cinderhaven platform convention), `WINDOW_START`, `WINDOW_END`, `MABD_WINDOW_DAYS = 2`, `OTIF_FINE_RATE = 0.03`, `TARGET_INTERNAL_FILL = 0.95`, `TARGET_RETAILER_OTIF = 0.86`, `TARGET_ONTIME_GAP_PTS = 5`, `TARGET_INFULL_GAP_PTS = 4`.

*`00_query_cinderhaven.py`*: Connect via `psycopg2` + `DATABASE_URL` from `.env` (same as Cinderhaven scripts). Query `fct_retailer_orders`, `fct_retailer_shipments`, `stg_sku_costs × stg_product_master` for Walmart orders only. Write `scripts/cache/cinderhaven_snapshot.json`. Pattern: `RealDictCursor`, `json.dump(..., default=str)`.

*`01_synthesize_otif.py`*: Pure function layer — reads snapshot, no DB calls. For each Walmart shipment:
- `mabd = requested_ship_date + timedelta(days=MABD_WINDOW_DAYS)`
- `on_time_result = delivery_date <= mabd` (delivery_date from snapshot; may be null → treat as late)
- `on_time_root_cause`: if `asn_sent_late == True` → `"warehouse_late"`, else `"carrier_late"` (carrier absorbed the delay)
- `acknowledged_qty`: for ~35% of orders, set to `po_qty × ack_rate` (0.80–0.95 range, seeded) → models order trimming. Remainder: `acknowledged_qty = po_qty`.
- `in_full_result = shipped_units >= acknowledged_qty`
- `in_full_root_cause`: trimmed orders → `"order_trimming"`; non-trimmed shorts → `"production_short_ship"`
- `cogs = units_ordered × case_pack_qty × cogs_per_unit`
- `otif_fine = cogs × 0.03` when `not on_time_result or not in_full_result`
- Velocity damage per in-full failure: estimated as `(po_qty - shipped_units) × unit_velocity_value` (unit_velocity_value from scan data average or config constant)
- Tune `ack_rate` distribution and `asn_sent_late` threshold via RNG seed until aggregate figures match targets. Write `scripts/cache/otif_synthetic.json`.

*`02_export_json.py`*: Aggregate synthetic data into the five output shapes and write to `frontend/src/data/`. No DB calls. All aggregations in pure Python (no pandas needed — keep dependencies minimal):
- `summary.json` — `{ internal_fill_rate, retailer_otif, gap_pts, ontime_gap_pts, infull_gap_pts, total_shipments, walmart_shipments, window_start, window_end }`
- `root_causes.json` — array of `{ cause, failure_mode, gap_pts, shipment_count, pct_of_gap }` for 4 root causes
- `true_fill.json` — `{ fill_vs_855, fill_vs_850, trimming_gap_pts, orders_with_trimming, pct_orders_trimmed }`
- `exposure.json` — `{ annual_fines, annual_velocity_damage, total_exposure, fines_by_quarter[], velocity_by_sku[] }`
- `audit_rows.json` — array, one object per Walmart shipment: `{ shipment_id, po_number, ship_date, mabd, delivery_date, on_time_result, on_time_root_cause, po_units, acknowledged_units, shipped_units, in_full_result, in_full_root_cause, otif_fine, retailer_penalty_flag }`

*`test_data_integrity.py`*: Load each JSON from `frontend/src/data/`. Assert:
- `summary.internal_fill_rate` within 0.005 of 0.95
- `summary.retailer_otif` within 0.005 of 0.86
- `sum(root_causes where failure_mode == "on_time", gap_pts)` within 0.5 of 5.0
- `sum(root_causes where failure_mode == "in_full", gap_pts)` within 0.5 of 4.0
- `exposure.annual_fines` within 0.05 of 140_000
- `exposure.annual_velocity_damage` within 0.05 of 320_000
- All audit_rows have required keys; no null shipment_id
- `true_fill.fill_vs_855 > true_fill.fill_vs_850` (855 always looks better than 850)

**Patterns to follow:**
- `active datasources/cinderhaven-data-platform/scripts/export_revenue_truth.py` — query + export pattern
- `active datasources/cinderhaven-data-platform/scripts/seed_config.py` — constants module pattern
- `published/channel-profitability-analysis/docs/solutions/best-practices/data-narrative-consistency-validation-2026-05-22.md` — data integrity test pattern

**Test scenarios:**
- `python run_pipeline.py` exits 0 with five JSON files written to `frontend/src/data/`
- `python -m pytest tests/test_data_integrity.py` passes all numeric assertions
- All five JSON files are valid JSON (no null values at root level)
- `audit_rows.json` contains only Walmart shipments (`retailer_id == WALMART_RETAILER_ID`)
- Re-running the pipeline with the same seed produces identical JSON (determinism)
- `true_fill.json`: `fill_vs_850 < fill_vs_855` (order trimming always inflates 855 fill rate)

**Verification:** `python tests/test_data_integrity.py` passes; `frontend/src/data/` contains all five files; `exposure.annual_fines + exposure.annual_velocity_damage ≈ 460_000`.

---

### U3. Data types and loading

**Goal:** Define all TypeScript types matching the five JSON shapes and the typed import pattern so every component has zero `any` casts when consuming data.

**Requirements:** R8, R9, R10 (type safety on the baked JSON)

**Dependencies:** U2 (JSON files must exist to verify import correctness)

**Files:**
- `frontend/src/types.ts`
- `frontend/src/data.ts`
- `frontend/src/utils/format.ts`
- `frontend/src/utils/format.test.ts`

**Approach:**

*`types.ts`*: Flat interface declarations — no generics, no utility types. One interface per JSON file root shape, plus sub-types. `AuditRow` is the richest type (all shipment fields). Use `string | null` for nullable dates. Match field names from JSON exactly.

*`data.ts`*: Static JSON imports using the `as unknown as T` cast pattern (required under `strict` + `verbatimModuleSyntax`):
```
// Directional — not implementation specification
import rawSummary from './data/summary.json'
export const summary = rawSummary as unknown as Summary
```
No `fetch()`, no `useEffect`, no loading states. All data available synchronously at module load time.

*`format.ts`*: `formatDollars(n)` (M/K/raw thresholds), `formatPercent(n, digits?)`, `formatPts(n)` (one decimal + " pts" suffix). Mirror `where-the-money-comes-from/src/utils/format.ts` naming conventions.

**Patterns to follow:**
- `published/where-the-money-comes-from/src/utils/format.ts` — formatter conventions
- Institutional learning: `as unknown as T` for JSON import casts under strict mode

**Test scenarios:**
- `formatDollars(140000)` → `"$140K"`; `formatDollars(460000)` → `"$460K"`; `formatDollars(1200000)` → `"$1.2M"`
- `formatPercent(0.95)` → `"95%"`; `formatPercent(0.864, 1)` → `"86.4%"`
- `formatPts(5)` → `"5.0 pts"`; `formatPts(4)` → `"4.0 pts"`
- TypeScript: `npm run build` passes with no `any` usage in `data.ts` or `types.ts`

**Verification:** `npm test` passes format tests; `npm run build` passes type-check with no errors.

---

### U4. App shell, PlotChart, and headline hook

**Goal:** Wire chapter navigation, root data imports, and the headline "95% vs. 86%" reveal section that appears before any charts.

**Requirements:** R11 (headline hook visible without scrolling), R13 (click-to-pin foundation), AE1 (non-ops visitor legibility)

**Dependencies:** U1, U3

**Files:**
- `frontend/src/App.tsx`
- `frontend/src/App.css` (updated with layout)
- `frontend/src/App.test.tsx`
- `frontend/src/components/ChapterNav.tsx`
- `frontend/src/components/ChapterNav.css`
- `frontend/src/components/ChapterNav.test.tsx`
- `frontend/src/components/PlotChart.tsx` (copied from `published/where-the-money-comes-from/src/components/PlotChart.tsx`)
- `frontend/src/components/PlotChart.test.tsx`

**Approach:**

*`App.tsx`*: Imports all five data objects from `data.ts` (synchronous — no useEffect, no useState for loading). Chapter state: `const [chapter, setChapter] = useState<1 | 2>(1)`. Renders: `<HeadlineHook summary={summary} />` (always visible above nav), `<ChapterNav ... />`, then `{chapter === 1 && <ReconciliationView ... />}` / `{chapter === 2 && <AuditSheetView ... />}`.

*Headline section* (inline in `App.tsx` or a named sub-component): Two large numbers side by side. Left: "95%" labeled "Cinderhaven internal fill rate — measured at the shipping dock". Right: "86%" labeled "Walmart's OTIF score — measured at their receiving dock." The gap ("9 points. Same shipments. Different docks. Different baselines.") in Economist-voice prose beneath. Uses Lailara headline number size (64px Playfair Display). This section is above the fold on desktop and above the chapter nav tabs.

*`ChapterNav`*: Two tabs — `{ id: 1, label: "Reconciliation Matrix" }` and `{ id: 2, label: "EDI Audit Sheet" }`. Active tab has `border-bottom-color: var(--accent-red)`. Mirrors `where-the-money-comes-from/src/components/ChapterNav.tsx`.

*`PlotChart`*: Copied verbatim from `published/where-the-money-comes-from/src/components/PlotChart.tsx`. Do not modify.

**Patterns to follow:**
- `published/where-the-money-comes-from/src/App.tsx` — chapter state pattern
- `published/retailer-deduction-recovery/frontend/src/ChapterNav.tsx` — tab design
- Lailara Design System — headline number: 64px Serif, `letter-spacing: -0.02em`

**Test scenarios:**
- App renders without throwing when all five data modules are imported
- Headline section is present in DOM on initial render (no chapter navigation required to see it)
- Both `95%` and `86%` values are visible as distinct text nodes
- `ChapterNav` renders two tabs; clicking tab 2 shows AuditSheetView placeholder, clicking tab 1 returns to ReconciliationView
- `PlotChart` renders a container div with `data-chart-container="true"`

**Verification:** `npm test` passes; `npm run dev` shows the headline section above the nav tabs on first load.

---

### U5. Retailer Reconciliation Matrix

**Goal:** The full Reconciliation Matrix view — all five analytical moves in one scrollable layout, with click-to-pin on the root cause chart.

**Requirements:** R1–R6, R11–R13, AE1–AE4 (see origin: `docs/brainstorms/otif-blind-spot-requirements.md`)

**Dependencies:** U1, U3, U4

**Files:**
- `frontend/src/chapters/ReconciliationView/ReconciliationView.tsx`
- `frontend/src/chapters/ReconciliationView/ReconciliationView.css`
- `frontend/src/chapters/ReconciliationView/ReconciliationView.test.tsx`
- `frontend/src/chapters/ReconciliationView/domain.ts`
- `frontend/src/chapters/ReconciliationView/domain.test.ts`

**Approach:**

*`domain.ts`*: All business logic and derived constants — no JSX. Exports:
- `deriveDecompositionBars(summary)` — returns `[{ label, pts, pct, failure_mode }]` for the stacked decomposition
- `deriveRootCauseBars(rootCauses)` — returns bars sorted descending by `gap_pts`
- `deriveTrueFillComparison(trueFill)` — returns `{ fill_855_label, fill_855_value, fill_850_label, fill_850_value, delta_label, delta_value }`
- `ROOT_CAUSE_COLORS` — maps each of 4 root causes to a Lailara teal/orange token
- `DEMO_DATE = "2026-05-31"` (frozen date for consistent display)

*Charts* (each uses `<PlotChart render={...} />`):

**Move 1 — Dual-dock comparison**: Two bars (internal fill vs. retailer OTIF) with gap labeled. Observable Plot `barX` mark with custom styling. Economist style: horizontal gridlines only, no axis lines, value labels on bars.

**Move 2 — On-time/in-full decomposition**: Single stacked bar (or two adjacent bars) showing the 9-point gap split: 5 pts on-time (teal) / 4 pts in-full (orange). Observable Plot `barY` or `rect` marks. Text labels on each segment.

**Move 3 — Root cause attribution**: Four bars (warehouse-late, carrier-late, production short-ship, order trimming) with `gap_pts` values. Click-to-pin: `pinnedId` state, non-pinned bars dim to 0.3 opacity. Pinned dark callout card shows cause, point value, and one-line implication. `prefers-reduced-motion`: skip transition.

**Move 4 — True fill reveal**: Two KPI-style tiles (not a chart). Left: "95% — fill rate vs. acknowledged orders (855)". Right: "91% — true fill rate vs. original POs (850)". The delta tile: "4 pts — added by order trimming before acknowledgment." Serif headline numbers, sans labels.

**Move 5 — Exposure quantification**: Two KPI tiles and a total. "$140K — annual OTIF fines (3% of COGS on penalized shipments)". "$320K — estimated velocity damage from empty shelves". "$460K total annual exposure." Velocity damage tile visually larger or more prominent (it's the bigger, less obvious number per R5).

**Patterns to follow:**
- `published/where-the-money-comes-from/src/chapters/Chapter*/` — chapter view structure
- Click-to-pin: institutional learning from `published/where-the-money-comes-from` (see `docs/solutions/`)
- Observable Plot: `@observablehq/plot` `Plot.plot({ marks: [...], style: { ... } })`
- Lailara chart rules: horizontal gridlines only, every segment has text label, SVG output

**Test scenarios:**
- Covers AE1: headline 95% and 86% are visible above the chart section without scrolling
- Covers AE2: decomposition renders two labeled segments summing to 9 pts
- Covers AE2 (click-to-pin): clicking a root-cause bar sets `pinnedId`; non-pinned bars have `opacity: 0.3`; callout card appears; clicking the same bar clears the pin and restores full opacity
- Covers AE3: both fill-rate values (fill_vs_855 and fill_vs_850) visible in the true fill section; a delta value is labeled "order trimming"
- Covers AE4: both $140K and $320K are present in the exposure section; the velocity damage value is visually prominent
- Covers AE6 (R13 click-to-pin dismiss): clicking outside the pinned element clears pin and restores opacity
- `domain.ts` unit tests: `deriveRootCauseBars` sorts descending; `ROOT_CAUSE_COLORS` has entries for all 4 causes; `deriveTrueFillComparison` returns `fill_855_value > fill_850_value` always
- Observable Plot: `PlotChart` container div is non-empty after render

**Verification:** `npm test` passes; `npm run dev` shows all five analytical moves scrolling without horizontal overflow; click-to-pin works on root cause bars; `prefers-reduced-motion` collapses to snap.

---

### U6. EDI Audit Sheet

**Goal:** A sortable, filterable transaction-level table showing one row per Walmart shipment, enabling a visitor to drill into any OTIF failure and trace its root cause.

**Requirements:** R7, AE5 (see origin: `docs/brainstorms/otif-blind-spot-requirements.md`)

**Dependencies:** U1, U3, U4

**Files:**
- `frontend/src/chapters/AuditSheetView/AuditSheetView.tsx`
- `frontend/src/chapters/AuditSheetView/AuditSheetView.css`
- `frontend/src/chapters/AuditSheetView/AuditSheetView.test.tsx`

**Approach:**

Native `<table>` (no third-party table library). State: `sortKey: keyof AuditRow | null`, `sortDir: "asc" | "desc"`, `filterMode: "all" | "on_time_fail" | "in_full_fail" | "both_fail" | "clean"`.

Filter bar above the table: five buttons (All / On-time failures / In-full failures / Both / Clean). Active button gets a border or filled style via CSS. Clicking a button sets `filterMode` and resets sort.

Column headers are clickable — clicking once sorts ascending, again descending, third time returns to unsorted. Sorted column header shows a chevron icon (▲/▼ via CSS or Unicode).

Columns (in order):
1. PO # (po_number)
2. Ship date (ship_date)
3. MABD (mabd) — "Must Arrive By"
4. Delivery date (delivery_date)
5. On-time? (on_time_result) — Yes/No chip
6. Root cause (on_time_root_cause | "—")
7. PO units (po_units)
8. Acknowledged (acknowledged_units)
9. Shipped (shipped_units)
10. In-full? (in_full_result) — Yes/No chip
11. Root cause (in_full_root_cause | "—")
12. OTIF fine ($) (otif_fine — formatted or "—" if 0)

Rows where `on_time_result === false || in_full_result === false` get a subtle left border in `--accent-red`. Rows where both fail get a stronger red border.

Pagination: if `audit_rows.json` has >200 rows, show 50 per page with simple prev/next controls.

**Patterns to follow:**
- Native `<table>` with `<thead>` / `<tbody>` — no library needed
- Lailara: `border-radius: 2px`, font `--sans`, `12px` for table cell text
- `published/retailer-deduction-recovery/frontend/src/cohort/CohortTableView.tsx` — table layout reference

**Test scenarios:**
- Covers AE5: clicking "On-time failures" filter shows only rows where `on_time_result === false`
- Covers AE5: clicking a sortable column header sorts the visible rows by that column (ascending first)
- Covers AE5: a row with both failures has a distinct visual indicator (red border) distinguishable from a single-failure row
- All 12 columns are present in the rendered `<thead>`
- "Clean" filter shows only rows where both `on_time_result === true && in_full_result === true`
- Filter selection persists correctly across sort changes
- OTIF fine column shows "—" for rows with `otif_fine === 0`

**Verification:** `npm test` passes; `npm run dev` shows table with all 12 columns, all 5 filter buttons, column sort working.

---

### U7. Deployment and end-to-end verification

**Goal:** Configure wrangler for final deployment, wire `prebuild` to run the data pipeline, and verify the full round-trip: Python generates JSON → Vite bakes it → Cloudflare Workers serves it.

**Requirements:** R16, success criteria (live public URL, matches retailer-deduction-recovery quality)

**Dependencies:** U1–U6 (all implementation complete)

**Files:**
- `frontend/wrangler.jsonc` (final review — name, OG meta)
- `frontend/package.json` (prebuild script wired)
- `frontend/index.html` (meta description, OG tags, title)
- `tests/test_data_integrity.py` (final run before deploy)

**Approach:**

*Prebuild wiring*: In `frontend/package.json`, add `"prebuild": "cd .. && python scripts/run_pipeline.py"`. This runs the full data generation pipeline every time `npm run build` is called, so JSON is always fresh before bundling.

*`index.html`*: Title `"OTIF Blind Spot — Cinderhaven"`. Meta description: "Cinderhaven thinks it ships at 95% fill rate. Walmart scores it at 86% OTIF. An interactive reconciliation of the gap." OG image and Twitter card pointing to deployed URL.

*Final wrangler.jsonc*: Confirm `name: "otif-blind-spot"` (→ `otif-blind-spot.msshawnp.workers.dev`), `compatibility_date` set to today.

*Smoke test sequence*:
1. `python tests/test_data_integrity.py` — passes
2. `cd frontend && npm run build` — exits 0
3. `cd frontend && npm run preview` — serve locally, verify headline visible, both views load, click-to-pin works
4. `cd frontend && npm run deploy` — deploys to Cloudflare Workers
5. Visit live URL, verify render in browser

**Patterns to follow:**
- `published/short-ship-cost/web/index.html` — OG meta pattern
- `published/retailer-deduction-recovery/frontend/wrangler.jsonc` — deploy config

**Test scenarios:**
- Test expectation: none — this is deployment configuration and smoke testing; covered by manual verification steps above
- End-to-end: `npm run build` after fresh `python run_pipeline.py` produces a dist with all five JSON files baked in
- Live URL renders: headline numbers visible, ReconciliationView loads, AuditSheetView loads, click-to-pin on root cause chart works

**Verification:** Live URL at `otif-blind-spot.msshawnp.workers.dev` shows the complete piece end-to-end. All five analytical moves visible. EDI Audit Sheet loads and filters work.

---

## Scope Boundaries

- Real-time OTIF monitoring — the diagnostic is historical; live monitoring is the retainer/upsell (separate project #148)
- Dispute automation — the EDI Audit Sheet makes fines dispute-ready; automating dispute filings is deduction-recovery territory
- Multi-retailer rules library — Walmart MVP only; Target, Kroger, and others are v2
- Fixing the failures diagnosed — remediation belongs to Production Demand Forecast and carrier management
- Downloadable export from the EDI Audit Sheet — in-app table only

### Deferred to Follow-Up Work

- Velocity damage attribution by SKU — `exposure.json` includes a `velocity_by_sku[]` array placeholder; the breakdown view is not built in this arc
- `prefers-reduced-motion` audit across all animated interactions — R13 specifies it for click-to-pin; expand to any future animation
- `docs/solutions/` entries for OTIF patterns — capture after first milestone via `/ce:compound`
- Multi-retailer rule library (v2) — `otif_config.py` can hold per-retailer MABD windows; the synthesis script should be structured to accept a `retailer_id` parameter even if only Walmart is seeded now

---

## Key Technical Decisions

- **Observable Plot over direct D3** — Observable Plot handles coordinate scales, axes, and layout; the implementing agent uses it as a math + layout library and passes the resulting SVG element to `PlotChart`. Direct D3 would require 60–80% more chart scaffolding for no portfolio benefit. Both produce SVG (satisfies R12).

- **Vite-import baked JSON over runtime fetch** — JSON files in `src/data/` are imported at build time. No loading states, no `useEffect` for data, no race conditions. The `prebuild` script ensures data is always fresh before bundling. Eliminates the skeleton/loading-state UI entirely.

- **Standalone Python scripts over new dbt models** — The Cinderhaven platform's dbt project is for the platform's own marts. OTIF synthesis is portfolio-local work; adding new dbt models to the platform creates a dependency that must be maintained. Standalone scripts in `scripts/` keep OTIF self-contained and follow the established `export_revenue_truth.py` pattern.

- **MABD synthesized as `requested_ship_date + 2 days`** — Real Walmart MABDs are set by Walmart on each PO (not derivable from existing platform data). The 2-day window is a documented Walmart delivery standard and produces realistic on-time failure patterns when combined with the existing `delivery_date` values.

- **Native `<table>` for EDI Audit Sheet, no library** — A sortable/filterable table with 12 columns and 50 rows/page is ~100 lines of React. A table library adds a dependency for a use case this project has exactly once.

- **`PlotChart.tsx` copied verbatim from `where-the-money-comes-from`** — The component is stable, tested, and exactly right. Copying instead of importing avoids a cross-project dependency; any future improvements can be backported.

(see origin: `docs/brainstorms/otif-blind-spot-requirements.md` — Key Decisions)

---

## Dependencies / Assumptions

- Cinderhaven PostgreSQL is accessible via `flyctl proxy 5432 -a cinderhaven-db` during data generation (not required at runtime)
- `fct_retailer_orders`, `fct_retailer_shipments`, `stg_sku_costs`, `stg_product_master` exist and are materialized in the Cinderhaven platform — verified during planning
- `WALMART_RETAILER_ID` value confirmed from `raw.retailers` table before seeding (read from platform at script init, not hardcoded)
- Synthetic numbers ($140K fines, $320K velocity, 5/4 split) must align with figures in the short-ship-cost piece — validate against `published/short-ship-cost/web/public/data/` before deploy
- Observable Plot version should match `published/where-the-money-comes-from/package.json` to avoid API divergence
- `wrangler` authenticated to the `msshawnp` Cloudflare account before deploy

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Seeded RNG doesn't converge to target figures (5/4 split, $140K/$320K) | Medium | High | `test_data_integrity.py` catches this immediately; adjust `ack_rate` range or MABD window in `otif_config.py` |
| Cinderhaven DB unavailable during pipeline run | Low | Medium | Script fails fast with clear error; generated JSON already committed can be used as fallback |
| Observable Plot API changes between versions | Low | Medium | Pin version in `package.json`; match `where-the-money-comes-from` exactly |
| CSS token drift (hex values hardcoded outside `:root`) | Medium | Low | Run hex grep audit before each milestone commit |
| Numbers don't match short-ship-cost | Medium | Medium | Cross-check before deploy; shared Cinderhaven data foundation should keep them consistent |

---

## Deferred Implementation Notes

- Exact velocity damage calculation method — the per-in-full-failure velocity value (revenue lost per empty-shelf event) is not in the platform. An approximation using average POS velocity × days-out-of-stock is the intended approach, but the exact formula is implementation-time work.
- Observable Plot `style` overrides for Economist chart defaults — the exact Plot API calls for removing chart borders, setting gridline colors to `#d9d9d9`, and forcing the canvas background will require checking Observable Plot docs during implementation.
- Audit Sheet pagination threshold — 50 rows/page is the plan-time default; adjust based on actual `audit_rows.json` row count after data generation.
