---
date: 2026-05-31
topic: otif-blind-spot
---

# OTIF Blind Spot — Requirements

## Summary

An interactive HTML portfolio piece built in React/TypeScript/Vite/D3 that reconciles Cinderhaven's internal fill rate against a synthetic Walmart OTIF scorecard, executes all five analytical moves from the project brief, and delivers two views — the Retailer Reconciliation Matrix and the EDI Audit Sheet — in the Lailara Design System, deployed to Cloudflare Workers.

---

## Problem Frame

A specialty food brand's internal dashboard shows 95% fill rate. Walmart's supplier scorecard shows 86% OTIF. The CEO is confused: how can both numbers be true?

They're measured at different docks against different baselines. The brand measures fill at its own shipping dock against the orders it acknowledged — after it has already quietly trimmed lines it knew it couldn't fill. The retailer measures OTIF at its receiving dock against the original purchase orders. That divergence, compounded by order trimming, carrier timing misses, and production short-ships, produces a 9-point gap that the brand cannot explain because it has never put the two numbers side by side.

The blind spot is expensive. Walmart fines 3% of COGS on affected shipments — roughly $140K/year for Cinderhaven. The shelf-velocity damage from the empty shelves those in-full failures create is larger and invisible: an estimated $320K/year. Together: ~$460K/year the brand is paying without knowing why, or even that the problem exists.

The deeper failure is misdirected remediation. Without decomposing the gap into on-time failures (logistics) and in-full failures (production), the brand throws resources at the wrong problem. The decomposition — not the headline number — is the piece's most actionable output.

---

## Actors

- A1. **Portfolio visitor** — reads the piece, interacts with charts and drill-downs; expects a clear finding without needing to know what "EDI 856" or "MABD" means
- A2. **Shawn** — builds and deploys the piece as a Lailara portfolio showcase; primary client-facing signal of OTIF domain fluency
- A3. **Cinderhaven data platform** — source of synthetic shipment, order, retailer, and EDI data that feeds data generation
- A4. **Python data generation scripts** — consume Cinderhaven mart models, generate synthetic OTIF scorecard + 855 acknowledgment data, export static JSON

---

## Key Flows

- F1. **Primary read path**
  - **Trigger:** Visitor arrives at the app URL
  - **Actors:** A1
  - **Steps:**
    1. Visitor sees the headline hook: "Cinderhaven thinks its fill rate is 95%. Walmart scores it at 86%."
    2. Scrolls into the Retailer Reconciliation Matrix — internal vs. retailer comparison with the gap labeled
    3. Sees the on-time / in-full decomposition: 5 points on-time, 4 points in-full
    4. Clicks a root-cause bar (e.g., "Order trimming — 2.1 pts") → dark callout card pins with detail; non-selected bars dim
    5. Scrolls to the true fill rate reveal: internal fill (vs. acknowledged 855) vs. true fill (vs. original 850)
    6. Scrolls to exposure quantification: $140K fines, $320K velocity damage, $460K total
  - **Outcome:** Visitor understands what the gap is, where it comes from, and what it costs — without needing domain knowledge
  - **Covered by:** R1, R2, R3, R4, R5, R11, R12, R13

- F2. **EDI Audit Sheet drill-down**
  - **Trigger:** Visitor clicks to the EDI Audit Sheet view
  - **Actors:** A1
  - **Steps:**
    1. App renders a transaction-level table: one row per shipment, columns for 856 ship date, MABD, actual delivery, on-time result, units ordered (850), units acknowledged (855), units shipped, in-full result, retailer penalty flag
    2. Visitor sorts by failure type (on-time / in-full / both / clean)
    3. Visitor filters to a specific time window or SKU
    4. Visitor reads a specific row to see exactly why that shipment was penalized
  - **Outcome:** Visitor can trace any OTIF fine back to its root cause at the transaction level
  - **Covered by:** R6, R7

- F3. **Data generation pipeline**
  - **Trigger:** Shawn runs the Python generation script(s) before building the frontend
  - **Actors:** A2, A3, A4
  - **Steps:**
    1. Scripts read from Cinderhaven mart models (`fct_retailer_orders`, `fct_retailer_shipments`, `sku_costs`, `retailer_rules`)
    2. Scripts generate synthetic Walmart OTIF scorecard (consignee-dock view, MABD-based on-time measurement)
    3. Scripts generate 855 acknowledgment layer (with order-trimming events seeded in)
    4. Scripts compute all five analytical move outputs and write static JSON files to `frontend/public/data/`
  - **Outcome:** All data the React app needs is available as static JSON; no live database connection needed at runtime
  - **Covered by:** R8, R9, R10, R17

---

## Requirements

**Analytical moves**

- R1. The app reconciles internal fill rate (fulfillment dock, measured against acknowledged 855 orders) against retailer OTIF (consignee dock, measured against original 850 POs), displaying both numbers side by side with the gap explicitly labeled.
- R2. The app decomposes the OTIF gap into on-time failures and in-full failures, showing each as a point count and share of the total gap.
- R3. The app attributes on-time failures to root causes (warehouse-late departure vs. carrier-late transit) and in-full failures to root causes (production short-ship vs. intentional order trimming). Each root cause displays its point contribution to the gap.
- R4. The app computes and displays true fill rate against original 850 PO demand, contrasted with the internal fill rate measured against the acknowledged 855 baseline. The difference — the order-trimming blind spot — is labeled explicitly.
- R5. The app quantifies total exposure in two labeled components: OTIF fines (~$140K, computed as 3% of COGS on affected shipments) and shelf-velocity damage (~$320K, revenue lost from empty-shelf periods). Both are shown; the velocity number is visually prominent because it is the larger, less obvious cost.

**Views**

- R6. The Retailer Reconciliation Matrix view presents the dual-dock comparison (R1), decomposition (R2), root-cause attribution (R3), true fill reveal (R4), and exposure summary (R5) in a single scrollable layout.
- R7. The EDI Audit Sheet view presents a transaction-level, sortable and filterable table with one row per shipment. Columns include: 856 ship date, MABD, actual delivery date, on-time result, units on original 850 PO, units on acknowledged 855, units shipped, in-full result, and retailer penalty flag. Visitor can sort any column and filter by failure type.

**Data generation**

- R8. Python generation scripts produce synthetic Walmart OTIF scorecard data seeded to the brief's target figures: 95% internal fill rate, 86% retailer-scored OTIF, a 5-point on-time / 4-point in-full gap split, ~$140K in annual OTIF fines, ~$320K in shelf-velocity damage.
- R9. Python generation scripts produce a synthetic 855 acknowledgment layer showing order lines the brand trimmed before acknowledging, making true fill rate computable as fill against original 850 demand vs. fill against the acknowledged 855 baseline.
- R10. All generated data is written as static JSON files in `frontend/public/data/` and fetched by the React app at load time. No live database connection at runtime.

**Opening hook**

- R11. The piece opens with the headline reveal — Cinderhaven's internal number vs. Walmart's scorecard number and the gap — before presenting any charts or detail. This is the primary hook; it must be legible to a non-ops reader at a glance.

**Design and interaction**

- R12. All charts use D3 SVG rendering (no canvas). Gridlines are horizontal-only in `#d9d9d9`. No gradients, 3D effects, or decorative elements. Every data series has a text label.
- R13. Interactive chart elements use click-to-pin behavior: clicking pins a dark callout card above the chart with detail; clicking again dismisses. Non-selected elements dim to 0.2–0.3 opacity with a 200ms ease-out transition. Respects `prefers-reduced-motion` (snap, no animation).
- R14. Playfair Display and Source Sans 3 are self-hosted via @fontsource. No Google Fonts CDN calls.
- R15. All color tokens, typography sizes, spacing, border radius, and chart conventions follow the Lailara Design System v2 (`lailara-design-system/LAILARA_DESIGN_SYSTEM.md`). The piece should be visually indistinguishable in system from retailer-deduction-recovery.

**Deployment**

- R16. The app deploys to Cloudflare Workers via wrangler, following the same `build → wrangler deploy` pattern as short-ship-cost and retailer-deduction-recovery.

**Data integrity**

- R17. No real client data appears anywhere in the app, in scripts, or in committed JSON files. All Cinderhaven data is synthetic.

---

## Acceptance Examples

- AE1. **Covers R1, R11.** Given a visitor who has never heard of OTIF, when they arrive at the app, they immediately see two numbers — "95%" and "86%" — with a label making clear one is Cinderhaven's own measure and one is Walmart's. They do not need to scroll to find this.

- AE2. **Covers R2, R3.** Given the Retailer Reconciliation Matrix is visible, when a visitor reads the decomposition, they can answer "how much of the gap is logistics vs. production?" without clicking anything. When they click a root-cause bar, a callout card names the specific cause and its point contribution.

- AE3. **Covers R4.** Given the true fill rate section is visible, when a visitor reads it, they see two distinct fill-rate numbers — one measured against the acknowledged 855, one against the original 850 — with an explicit label on the difference ("order trimming adds X pts to the gap").

- AE4. **Covers R5.** Given the exposure section is visible, when a visitor reads it, they see two dollar figures ($140K fines, $320K velocity damage) and a total ($460K), with the velocity number visually distinguished as the larger, less obvious cost.

- AE5. **Covers R7.** Given the EDI Audit Sheet is open, when a visitor clicks the "on-time failure" filter, the table reduces to only shipments that missed their MABD. When they click a column header, the table re-sorts. Each row clearly shows why that shipment was penalized (which column triggered the failure).

- AE6. **Covers R13.** Given any interactive chart element is pinned, when a visitor clicks elsewhere on the chart (not the pinned element), the callout card dismisses and all elements return to full opacity.

---

## Success Criteria

- A non-ops reader (e.g., a CFO or category buyer) can read the piece and answer: "What is Cinderhaven's real OTIF score, what's causing the gap, and what does it cost?" — without knowing what MABD, EDI 856, or in-full means.
- The on-time/in-full decomposition is the most prominent finding after the headline reveal — a visitor can identify the primary failure mode without drill-down.
- The $460K exposure total is visible without scrolling past the main chart layer; the velocity-damage component ($320K) is clearly labeled as the larger, less obvious cost.
- The piece is visually and interactively consistent with retailer-deduction-recovery — a visitor who has seen both would not identify a design-system gap.
- All five analytical moves are present and independently traceable to source data (i.e., a planner or reviewer can verify the numbers without trusting a black box).

---

## Scope Boundaries

- Real-time OTIF monitoring — the diagnostic is historical; live monitoring is the retainer/upsell (separate project #148)
- Dispute automation — the EDI Audit Sheet makes fines dispute-ready; automating dispute filings is deduction-recovery territory
- Multi-retailer rules library — Walmart MVP only; Target, Kroger, and others are v2 extensions
- Fixing the failures the piece diagnoses — remediation belongs to Production Demand Forecast (in-full) and carrier management work (on-time)
- Downloadable export from the EDI Audit Sheet — it is an in-app table, not a workbook download

---

## Key Decisions

- **EDI Audit Sheet is an in-app sortable/filterable table, not a downloadable workbook.** The brief described it as "dispute-ready documentation," but a workbook download adds build complexity with low portfolio return; an in-app table demonstrates the same analytical depth and is consistent with the interactive format of the other pieces.
- **D3 for all charts, not Recharts.** retailer-deduction-recovery is the implementation reference; it uses D3 + custom SVG, which is required by the design system's SVG-only chart rule. short-ship-cost used Recharts and is the older pattern.
- **Data is static JSON generated by Python scripts, not hardcoded frontend constants.** Separating generation from rendering means data changes don't require React code changes, and the generation scripts can be shown as portfolio artifacts in their own right.
- **Walmart MVP only.** The brief's retailer-rules extensibility goal is a v2 concern; the data model can be structured to support it without building the multi-retailer logic now.

---

## Dependencies / Assumptions

- `fct_retailer_orders` and `fct_retailer_shipments` exist in the Cinderhaven platform and are the starting point for data generation — verified during /clarify
- `retailer_rules` table exists (verified in platform listing) and may contain Walmart MABD window definitions — needs inspection during planning
- `sku_costs` table exists and can provide COGS per SKU for fine calculation — needs inspection during planning
- The synthetic numbers ($140K fines, $320K velocity damage, 5/4 split) must be internally consistent with figures already published in The 150 Cases (short-ship-cost) and referenced in Production Demand Forecast
- retailer-deduction-recovery (`frontend/`) is the primary implementation reference for project structure, wrangler config, D3 patterns, @fontsource setup, and Lailara Design System token usage

---

## Outstanding Questions

### Resolve Before Planning

*(None — all scope-shaping decisions are resolved.)*

### Deferred to Planning

- **[Affects R8, R5][Needs research]** Does `fct_retailer_shipments` or `sku_costs` carry a COGS field, or does COGS need to be derived (units × cost per unit from `sku_costs`)? Affects fine calculation in the generation scripts.
- **[Affects R3][Needs research]** Does the `retailer_rules` table have Walmart-specific MABD window definitions? If not, MABD windows need to be seeded as part of data generation.
- **[Affects R16][Technical]** What worker subdomain should this deploy to? Other pieces follow `<project>.msshawnp.workers.dev` — confirm `otif-blind-spot.msshawnp.workers.dev` is available and consistent with the portfolio URL pattern.
- **[Affects R8, R9][Technical]** Should the Python generation scripts extend the Cinderhaven dbt project (new models) or be standalone scripts that query the existing marts and write JSON directly? Standalone is simpler; dbt integration maintains platform consistency.
