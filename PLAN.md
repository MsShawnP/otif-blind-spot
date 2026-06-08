# OTIF Blind Spot — Current Work Plan

The current arc of work. Updated when the arc changes, not every
session. For session-by-session state, see HANDOFF.md.

---

## Goal

Build an interactive HTML portfolio piece (React + TypeScript + Vite + D3, Cloudflare Workers) that reconciles Cinderhaven's internal fill rate against a synthetic Walmart OTIF scorecard across all 5 analytical moves, delivering the Retailer Reconciliation Matrix and EDI Audit Sheet views in the Lailara Design System.

## Why this arc, why now

Completes the short-ship workstream diagnostic leg — The 150 Cases (cost) and Production Demand Forecast (prevention) are already built or briefed; this is the missing measurement piece that reveals the problem exists and tells the brand exactly what to fix.

## Business question this arc answers

Why does Cinderhaven's internal 95% fill rate diverge from Walmart's 86% OTIF score, which failure modes (on-time vs. in-full) drive the gap, and what is the full financial exposure — fines plus shelf-velocity damage?

## Stack

- React + TypeScript + Vite + D3 (matching retailer-deduction-recovery)
- Static JSON data files in `public/` fetched at app load
- Python data generation scripts (new synthetic OTIF scorecard + 855 layer + MABD fields)
- Deployed to Cloudflare Workers via wrangler
- Lailara Design System: canvas bg, Playfair Display + Source Sans 3, SVG charts, click-to-pin

## Tasks

Work in vertical slices — one section/feature end-to-end before moving
to the next. Visualizations get reviewed in their own slice, not
deferred to a polish phase.

- [x] Run /clarify to scope the work
- [x] Run /ce:brainstorm to write the spec
- [x] Run /ce:plan to research and plan implementation
- [x] Run /ce:work — all 7 implementation units complete (51 tests, build passing)

## Analytical moves (all in scope)

1. **Dual-dock reconciliation** — internal fill rate (fulfillment dock) vs. retailer OTIF (consignee dock)
2. **On-time / in-full decomposition** — split the gap into its two failure modes
3. **Root-cause attribution** — warehouse-late vs. carrier-late vs. production short-ship vs. order trimming
4. **True fill rate** — fill against original 850 PO demand (not acknowledged 855)
5. **Exposure quantification** — OTIF fines (3% COGS) + shelf-velocity damage

## Data work required

- Existing: `fct_retailer_orders`, `fct_retailer_shipments` in Cinderhaven platform
- To generate: synthetic Walmart OTIF scorecard (consignee dock view), 855 acknowledgment layer (showing trimmed quantities), MABD fields, COGS for fine calculation
- Output: static JSON files in `public/data/`

## Out of scope for this arc

- Real-time OTIF monitoring (engagement upsell, separate project #148)
- Fixing the failures themselves (this piece diagnoses; remediation is other pieces)
- Dispute automation (deduction-recovery territory)
- Multi-retailer rule library (Walmart MVP first; other retailers in v2)

## Definition of done for this arc

- [x] All 5 analytical moves visible and accurate in the interactive HTML piece
- [x] Retailer Reconciliation Matrix view complete (internal vs. retailer comparison, on-time/in-full split, root-cause attribution)
- [x] EDI Audit Sheet view complete (transaction-level drill-down)
- [x] Exposure numbers match brief: ~$140K fines + ~$320K velocity damage = ~$460K total
- [x] Lailara Design System applied consistently (matches retailer-deduction-recovery visual standard)
- [x] Deployed to Cloudflare Workers and accessible at a public URL
- [x] Data paranoia: all data is synthetic Cinderhaven, no real client data anywhere

---

## Arc history

### 2026-05-31 — Foundation
- Outcome: Project scaffolded, state files created, GitHub remote initialized
- Tag: v0.1-foundation

### 2026-05-31 — Implementation complete
- Outcome: All 7 units shipped. Live at otif-blind-spot.msshawnp.workers.dev. 10,201 orders, 51 frontend + 18 integrity tests pass.
- Tag: v1.0-shipped

---

## Improvement history

<!-- Entries are added by /improve — don't delete this section -->

### 2026-05-31 — Improvement pass
- **Trigger:** User-initiated post-ship health check
- **What was reviewed:** All workflow files, code quality, tests, dependencies, documentation, git hygiene, security audit (ce-security-sentinel), code review (ce-correctness, ce-testing, ce-kieran-typescript, ce-learnings-researcher)
- **What was fixed:**
  - EDI Audit Sheet: eliminated all horizontal scrolling — `overflow: hidden` + `table-layout: fixed` + `<colgroup>` with proportional column widths
  - EDI Audit Sheet: fixed header clipping bug introduced during scroll fix (removed `white-space: nowrap` from `.audit-th`)
  - EDI Audit Sheet: added `overflow-wrap: break-word` to data cells to prevent token bleed
  - EDI Audit Sheet: drove colgroup from `COLUMNS` array (added `width` field to Column interface) — eliminates hardcoded column count drift risk
  - README: filled in Stack and "How to run" sections (were TBD since scaffold)
  - `scripts/otif_config.py`: DATABASE_URL fallback now raises `EnvironmentError` instead of silently constructing empty-password connection string
  - `domain.ts`: removed unused `DEMO_DATE` export
  - `docs/solutions/flex-min-width-table-scroll-bypass-2026-05-31.md`: updated to document Strategy B (table-layout fixed) and when to use each strategy
  - npm audit: 0 vulnerabilities confirmed
- **Deferred:** None — all findings resolved
- **Next review:** 2026-06-30
