# OTIF Blind Spot — Decisions Log

Permanent record of choices that should survive session turnover.
If a decision is reversed, strike it through and add the replacement
below — don't delete.

---

## Format

Each entry:
- **Date** — when decided
- **Decision** — one sentence, imperative voice
- **Why** — the reasoning, including what was tried and rejected
- **Scope** — what this applies to (file, chunk, deliverable, or "global")
- **Do not** — explicit anti-instructions, if any

---

## Architecture & Pipeline

### 2026-05-31 — Portfolio data generation lives in project-local scripts, not Cinderhaven dbt
- **Why:** The Cinderhaven dbt project is the platform's own source of truth. Adding portfolio-specific dbt models creates a cross-project dependency that must be maintained separately. Standalone scripts in `scripts/` following the `export_revenue_truth.py` pattern keep portfolio projects self-contained and independently deployable. Alternatives rejected: new dbt models (platform coupling), hardcoded frontend constants (not traceable to source data).
- **Scope:** All Lailara portfolio pieces deriving synthetic data from Cinderhaven
- **Do not:** Add portfolio-specific dbt models to `active datasources/cinderhaven-data-platform/`. Use standalone psycopg2 scripts querying existing marts and exporting JSON.

### 2026-07-30 — Require the full DATABASE_URL; never assemble a connection string inline from POSTGRES_PASSWORD
- **Why:** The gitleaks pre-commit rule (`postgres-url-with-password`) blocks any Postgres connection URL that carries an inline password — literal OR variable-interpolated, and even when the shape appears inside a comment. Building the URL inline from a password both trips that rule and duplicates connection config that `.env` already owns. `.env.example` documents `DATABASE_URL` as the mechanism, and `00_query_cinderhaven.py` reads it directly.
- **Scope:** `scripts/otif_config.py` and any pipeline DB-connection code.
- **Do not:** Interpolate `POSTGRES_PASSWORD` into a connection string in Python source, and do not spell that URL-with-inline-password shape out in a comment either (gitleaks flags the comment too). Require `DATABASE_URL` and raise `EnvironmentError` when it is unset.

### 2026-05-31 — Use Vite-import baked JSON over runtime fetch for portfolio data
- **Why:** JSON imported at build time (`src/data/`) eliminates loading states, useEffect data fetching, and race conditions. `where-the-money-comes-from` established this as the newer, cleaner pattern. Runtime fetch (`public/data/`) is the older pattern from `retailer-deduction-recovery` and requires loading state handling. The `prebuild` script ensures data is always fresh before bundling.
- **Scope:** All new Lailara portfolio pieces that use static data; applies to this project's five JSON data files
- **Do not:** Use `public/data/` + runtime `fetch()` for new portfolio pieces. Do not add loading spinners or skeleton states for data available at build time. Supersedes R10's `public/data/` specification in `docs/brainstorms/otif-blind-spot-requirements.md`.

---

## Data & Schema

[Decisions about data sources, schemas, transformations]

---

## Visualization

### 2026-05-31 — Use Observable Plot for all chart work; not raw D3
- **Why:** Observable Plot produces identical SVG output to hand-rolled D3 while eliminating ~60–80% of chart scaffolding (scale setup, axis boilerplate, layout math). Confirmed by institutional learnings from `where-the-money-comes-from`. The requirements-level D3 specification (R12) targeted the SVG-output constraint (no canvas), not D3 specifically — Observable Plot satisfies R12's intent. Alternatives rejected: raw D3 (more code, same output), Recharts (canvas-capable, design system incompatible).
- **Scope:** All Lailara portfolio chart work; future requirements docs should specify "SVG charts, no canvas" rather than "D3 SVG rendering"
- **Do not:** Use Recharts or any canvas-based charting library. Do not interpret "D3 SVG rendering" in older requirements docs as requiring raw D3 — Observable Plot is the approved implementation. Supersedes R12's D3-specific language in `docs/brainstorms/otif-blind-spot-requirements.md`.

---

## Output Formats

[Decisions about deliverable formats, structure, organization]

---

## Writing & Voice

### 2026-05-31 — Use Economist style throughout
- **Why:** Lailara portfolio standard; the audience is COO/CFO level — sober, declarative, data-forward is the right register
- **Scope:** All written deliverables, chart titles, insight lines, footnotes
- **Do not:** Use marketing voice ("leverage," "synergy") or hedge real findings

### ~~2026-05-31 — Synthetic OTIF data ships against acknowledged_qty, not original PO qty~~ SUPERSEDED 2026-06-14
- ~~**Why:** Cinderhaven WMS ships against the 855 acknowledgment, not the 850 PO. Shipping against po_qty produces fill_vs_855 > 100%, which is nonsensical. The 855 quantity is the contractual shipment obligation.~~
- ~~**Scope:** `01_synthesize_otif.py` — all synthetic shipment quantity calculations~~
- **Superseded by:** 084675b — the synthesis step was deleted. `00_query_cinderhaven.py` now pulls `units_ordered` / `units_shipped` from the platform's causal fulfillment tables; nothing is synthesized, so there is no shipment-quantity base to choose.

### ~~2026-05-31 — Internal fill rate (95%) is hardcoded, not derived from Cinderhaven data~~ SUPERSEDED 2026-06-14
- ~~**Why:** Cinderhaven seed data has `units_shipped = total_units` everywhere (100% fill). The "95% internal fill" is a portfolio claim representing what a real brand would report — it cannot be derived from the synthetic platform data without introducing artificial defects that would corrupt the OTIF simulation.~~
- ~~**Scope:** `02_export_json.py` `build_summary()` — `internal_fill_rate` field only~~
- ~~**Do not:** Attempt to compute internal_fill_rate from `total_shipped / total_ack` or `total_shipped / total_po` in the current synthesis.~~
- **Superseded by:** 084675b — `TARGET_INTERNAL_FILL` is gone. `02_export_json.py:152` computes `internal_fill = total_shipped / total_ordered` from platform data; the published figure is 0.9923, not 0.95. The old "Do not" now forbids what the code does.

### ~~2026-05-31 — COGS_MULTIPLIER scales Cinderhaven seed COGS to match brief's brand magnitude~~ SUPERSEDED 2026-06-14
- ~~**Why:** Cinderhaven seed COGS averages ~$616/order. The brief assumes a $3M–$20M specialty food brand with proportionally larger COGS. Without scaling, annual fines compute to ~$8K instead of ~$140K. The multiplier (currently 14.0) is a documented, tunable constant — not a hidden fudge factor.~~
- ~~**Scope:** `01_synthesize_otif.py` — all COGS and fine calculations~~
- **Superseded by:** 084675b — `COGS_MULTIPLIER` no longer exists anywhere in the codebase. Fines are computed from platform COGS with no scaling factor.

---

## UI & Layout

### ~~2026-05-31 — EDI Audit Sheet uses table-layout:fixed with no scroll (Strategy B)~~ SUPERSEDED 2026-06-19
- ~~**Why:** User requirement is zero horizontal scrolling — no page-level scroll, no scoped wrapper scroll. Strategy A (`min-width: 0` + `overflow-x: auto`) scopes the scroll but doesn't eliminate it. Strategy B (`overflow: hidden` + `table-layout: fixed` + `<colgroup>` with percentage widths) forces the table into its container with no overflow possible. The 12 columns fit at the 900px content max-width with the current column proportions (7–13%).~~
- **Superseded by:** "EDI Audit Sheet uses auto layout at full page width" below.

### ~~2026-05-31 — AuditSheetView colgroup must be driven from the COLUMNS array~~ SUPERSEDED 2026-06-19
- ~~**Why:** The `<colgroup>` has one `<col>` per column. Hardcoding 12 `<col>` elements creates a count that must be manually kept in sync with `COLUMNS.length`. If a column is added or removed, the browser silently misapplies widths.~~
- **Superseded by:** Colgroup removed entirely — no longer needed with auto table layout.

### 2026-06-19 — EDI Audit Sheet uses auto layout at full page width
- **Why:** Adding `white-space: nowrap` on date/PO columns made the 12-column table exceed the 900px content cap. Instead of forcing the table back into 900px (which caused horizontal scroll), the fix moves `max-width: 900px` from `.app-main` to `.reconciliation-view` only. The audit table gets the full viewport width (~1160px at 1440px), fitting all columns with no scroll. Removed `table-layout: fixed`, `<colgroup>`, and percentage widths — the browser's auto layout handles column sizing naturally.
- **Scope:** `AuditSheetView.css`, `AuditSheetView.tsx`, `App.css`, `ReconciliationView.css`
- **Do not:** Add `max-width` back to `.app-main` — that constrains the audit table. Do not add `table-layout: fixed` — auto layout with nowrap on key columns is the correct approach. The Reconciliation Matrix has its own `max-width: 900px`.

### 2026-06-19 — Client-side window recomputation via computeMetrics.ts
- **Why:** Date-range preset buttons (13w/26w/52w/full) require all figures to recompute for the selected window. Rather than re-running the Python pipeline, `computeMetrics.ts` mirrors the pipeline's summary/root-cause/true-fill/exposure logic in TypeScript, operating on per-shipment and per-chargeback data exported as JSON. The "full corpus" preset short-circuits to precomputed static data to avoid rounding drift between Python and JS.
- **Scope:** `computeMetrics.ts`, `App.tsx`, `data.ts`, `types.ts`, `02_export_json.py` (new exports)
- **Do not:** Add a server-side API for window filtering — this is a static portfolio piece. Do not remove the "full corpus" shortcut — it ensures the full-window figures match the Python pipeline exactly.

### 2026-07-30 — Every displayed figure derives from the selected window's props; no hardcoded metrics in components
- **Why:** The date-range presets (13w/26w/52w/all) recompute all metrics client-side. Any figure hardcoded in a component or its prose contradicts the windowed tiles on non-default presets — which shipped live in the headline exposure and the Move 4/Move 5 framing prose until the 2026-07-30 pass floated them.
- **Scope:** `App.tsx` headline, all `ReconciliationView` framing prose, and every exposure/gap/true-fill display.
- **Do not:** Write a metric value (dollar total, gap points, delta) as a literal in a component or its prose. Derive it from the `summary`/`exposure`/`trueFill` props via the `format*` helpers so it floats with the window.

### 2026-07-30 — Move 4 "True Fill" measures shipping-dock vs receiving-dock fill, not EDI-855 order trimming
- **Why:** `02_export_json.py` build_audit_rows remaps `units_shipped→acknowledged_units` and `units_received→shipped_units`, so `computeTrueFill`'s `fill_vs_855` = shipped/ordered (brand shipping-dock fill), `fill_vs_850` = received/ordered (retailer receiving-dock fill), and the delta = shipped − received = units lost between the two docks. The data has no 850/855 acknowledgment layer (acknowledged == po). The original "Walmart trims POs via EDI 855 / order trimming" framing described a mechanism the data does not contain — a supply-chain-literate reader would catch it.
- **Scope:** Move 4 tiles/prose, EDI Audit Sheet Shipped/Received columns, and any doc naming the fourth root cause. The `trimming_gap_pts` / `fill_vs_855` / `fill_vs_850` / `acknowledged_units` field NAMES are legacy — do not read EDI semantics into them.
- **Do not:** Reintroduce "order trimming" or "EDI 855 acknowledgment" language in Move 4, and do not list "order trimming" as a root cause — the four causes are `warehouse_late`, `carrier_late`, `short_ship`, `receiving_discrepancy`.

### 2026-07-30 — Running prose uses lailara-frame `.ll-measure` classes, not per-block hardcoded max-widths
- **Why:** `lailara-frame.css` defines the brand's canonical prose measures (`--ll-body-max-width` 720px, `--ll-body-max-width-narrow` 560px) and the `.ll-measure` / `.ll-measure-narrow` utility classes. Body prose reads at the 720px measure *inside* the 900px `.reconciliation-view` container — the container width is for charts/tables, not line length. Hardcoding a per-block `max-width` (660px on framing, 580px on the hero gap, etc.) drifts from the frame and re-triggers the "unused frame classes" standards flag. Cascade note: `lailara-frame.css` is imported before the component CSS in `main.tsx`, so a component `max-width` on the same element wins source-order and silently no-ops the utility class — apply the class in JSX **and** delete the component `max-width`.
- **Scope:** All running-prose blocks — `.recon-section__framing`, `.recon-footnote` (`ll-measure`), and `.headline-hook__gap` (`ll-measure-narrow`). Non-prose chart labels, KPI captions, and pin-card text are excluded — they are labels/captions, not running text.
- **Do not:** Re-add a hardcoded `max-width` to a prose element's component CSS, and do not hand-pick prose widths in `ch`/`rem` (the frame comment explains why both mislead). Use the frame measure classes.

---

## Reversed / Superseded

When a decision is overturned:
1. Strike through the original entry above (don't delete)
2. Add a new entry below with the replacement decision
3. Note the link in both directions
