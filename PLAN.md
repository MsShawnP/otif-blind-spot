# OTIF Blind Spot — Current Work Plan

The current arc of work. Updated when the arc changes, not every
session. For session-by-session state, see HANDOFF.md.

---

## Goal

Build an interactive HTML portfolio piece (React + TypeScript + Vite + D3, Cloudflare Workers) that reconciles Cinderhaven's internal fill rate against a synthetic Walmart OTIF scorecard across all 5 analytical moves, delivering the Retailer Reconciliation Matrix and EDI Audit Sheet views in the Lailara Design System.

## Why this arc, why now

Completes the short-ship workstream diagnostic leg — The 150 Cases (cost) and Production Demand Forecast (prevention) are already built or briefed; this is the missing measurement piece that reveals the problem exists and tells the brand exactly what to fix.

## Business question this arc answers

Why does Cinderhaven's internal 96% fill rate diverge from Walmart's 86% OTIF score, which failure modes (on-time vs. in-full) drive the gap, and what is the full financial exposure — fines plus shelf-velocity damage?

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

- [ ] All 5 analytical moves visible and accurate in the interactive HTML piece
- [ ] Retailer Reconciliation Matrix view complete (internal vs. retailer comparison, on-time/in-full split, root-cause attribution)
- [ ] EDI Audit Sheet view complete (transaction-level drill-down)
- [ ] Exposure numbers match brief: ~$140K fines + ~$320K velocity damage = ~$460K total
- [ ] Lailara Design System applied consistently (matches retailer-deduction-recovery visual standard)
- [ ] Deployed to Cloudflare Workers and accessible at a public URL
- [ ] Data paranoia: all data is synthetic Cinderhaven, no real client data anywhere

---

## Arc history

### 2026-05-31 — Foundation
- Outcome: Project scaffolded, state files created, GitHub remote initialized
- Tag: v0.1-foundation

---

## Improvement history

<!-- Entries are added by /improve — don't delete this section -->
