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

### 2026-05-31 — Synthetic OTIF data ships against acknowledged_qty, not original PO qty
- **Why:** Cinderhaven WMS ships against the 855 acknowledgment, not the 850 PO. Shipping against po_qty produces fill_vs_855 > 100%, which is nonsensical. The 855 quantity is the contractual shipment obligation.
- **Scope:** `01_synthesize_otif.py` — all synthetic shipment quantity calculations
- **Do not:** Set `synthetic_shipped_qty = po_qty` for non-short-ship orders. Use `acknowledged_qty` as the base.

### 2026-05-31 — Internal fill rate (95%) is hardcoded, not derived from Cinderhaven data
- **Why:** Cinderhaven seed data has `units_shipped = total_units` everywhere (100% fill). The "95% internal fill" is a portfolio claim representing what a real brand would report — it cannot be derived from the synthetic platform data without introducing artificial defects that would corrupt the OTIF simulation.
- **Scope:** `02_export_json.py` `build_summary()` — `internal_fill_rate` field only
- **Do not:** Attempt to compute internal_fill_rate from `total_shipped / total_ack` or `total_shipped / total_po` in the current synthesis. Both give incorrect results (> 100% or reflecting the short-ship rate, not the portfolio claim).

### 2026-05-31 — COGS_MULTIPLIER scales Cinderhaven seed COGS to match brief's brand magnitude
- **Why:** Cinderhaven seed COGS averages ~$616/order (50 SKUs × average 70 units × ~$2.20/unit). The brief assumes a $3M–$20M specialty food brand with proportionally larger COGS. Without scaling, annual fines compute to ~$8K instead of ~$140K. The multiplier (currently 14.0) is a documented, tunable constant — not a hidden fudge factor.
- **Scope:** `01_synthesize_otif.py` — all COGS and fine calculations
- **Do not:** Remove the multiplier to "use real COGS." The real COGS represent the seed's arbitrary scale, not a real brand. The multiplier is what makes the portfolio numbers coherent.

---

## UI & Layout

### 2026-05-31 — EDI Audit Sheet uses table-layout:fixed with no scroll (Strategy B)
- **Why:** User requirement is zero horizontal scrolling — no page-level scroll, no scoped wrapper scroll. Strategy A (`min-width: 0` + `overflow-x: auto`) scopes the scroll but doesn't eliminate it. Strategy B (`overflow: hidden` + `table-layout: fixed` + `<colgroup>` with percentage widths) forces the table into its container with no overflow possible. The 12 columns fit at the 900px content max-width with the current column proportions (7–13%).
- **Scope:** `AuditSheetView.css` and `AuditSheetView.tsx` — table wrapper and column layout only
- **Do not:** Switch back to `overflow-x: auto` or `min-width: 0` on `.audit-table-wrap`. Do not add `overflow-x: scroll` or `overflow-x: auto` to any ancestor of the audit table. See `docs/solutions/ui-bugs/flex-min-width-table-scroll-bypass-2026-05-31.md` for the Strategy A vs B comparison.

### 2026-05-31 — AuditSheetView colgroup must be driven from the COLUMNS array
- **Why:** The `<colgroup>` has one `<col>` per column. Hardcoding 12 `<col>` elements creates a count that must be manually kept in sync with `COLUMNS.length`. If a column is added or removed, the browser silently misapplies widths. Driving the colgroup from `COLUMNS.map()` (with a `width` field on the `Column` interface) makes the count structurally impossible to drift.
- **Scope:** `AuditSheetView.tsx` — `<colgroup>` rendering only
- **Do not:** Replace the `COLUMNS.map()` colgroup with hardcoded `<col>` elements. Do not set column widths via `<th style>` or `.audit-th` CSS — the `<col>` approach keeps layout separate from header presentation.

---

## Reversed / Superseded

When a decision is overturned:
1. Strike through the original entry above (don't delete)
2. Add a new entry below with the replacement decision
3. Note the link in both directions
