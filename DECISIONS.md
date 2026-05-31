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

---

## Reversed / Superseded

When a decision is overturned:
1. Strike through the original entry above (don't delete)
2. Add a new entry below with the replacement decision
3. Note the link in both directions
