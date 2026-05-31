# Portfolio Project Brief: OTIF Blind Spot

**Working title:** *"You Think Your Fill Rate Is 96%. Walmart Says It's 86%."*

**Repo (recommended):** `otif-blind-spot`

**Status:** Brainstorm / Brief stage
**Tier:** Curated backlog #8 (high-value — the measurement/visibility piece of the short-ship workstream)
**Priority:** Build within the short-ship cluster. Completes the trio: this one *reveals* the OTIF problem, Production Demand Forecast *prevents* it, The 150 Cases *quantifies the cost* of it.

---

### 1. The Pain

A specialty food brand's internal dashboard says it ships 96% of orders complete. The brand feels good about that number. Then a Walmart OTIF fine arrives, and the supplier scorecard says the brand's On-Time In-Full performance is 86%. The CEO is confused: how can we be at 96% and 86% at the same time?

The answer is that they're two different numbers measured at two different docks, and the brand has only ever looked at one of them.

**The brand measures fill rate at the Fulfillment Dock** (its own shipping dock) — what it shipped against what it *acknowledged* it would ship. **The retailer measures OTIF at the Consignee Dock** (its receiving dock) — what actually arrived, on time and complete, against the *original* purchase order. Those numbers diverge, sometimes badly, because of everything that happens between the two docks: order lines the brand quietly trimmed before acknowledging, late carrier deliveries that missed the must-arrive-by-date, missed delivery appointment windows, partial receipts, substitutions. Every one of those widens the gap between "what we think our fill rate is" and "what the retailer is scoring us on."

The most insidious of these is order trimming. When the warehouse is short on stock, the sales or ops team quietly cancels or reduces line items on the incoming order *before* sending the EDI 855 (Purchase Order Acknowledgment). The internal fill rate is then calculated against that trimmed 855 baseline — and looks great. But the retailer scores against the original EDI 850 PO. The brand has, in effect, graded itself against a test it edited. Measuring true fill against the 850 exposes the self-deception immediately.

That gap is the blind spot. And it's expensive:

- **OTIF fines are material.** Walmart fines 3% of COGS on shipments that miss the threshold. Target, Kroger, and others run comparable programs. For a brand doing meaningful volume, that's six figures a year.
- **The scorecard affects survival, not just fines.** A poor OTIF score damages the brand's standing at category review. Buyers cut chronic OTIF offenders. The fine is the visible cost; the lost shelf position is the existential one.
- **The brand is often fixing the wrong thing.** OTIF failures are either "on-time" failures (delivery was late) or "in-full" failures (shipped short) or both. Without decomposing them, the brand throws resources at logistics when the real problem is production short-ships — or vice versa. They're fixing blind.
- **The rules are opaque.** Each retailer measures OTIF differently — what counts as on-time (appointment windows, MABD), what counts as in-full (line fill vs. case fill vs. unit fill), how the threshold is calculated. The brand is being graded against rules it has never read.

**Who feels it:**
- **$3M–$10M:** Just entering retailers with OTIF programs. Doesn't know the rules, gets the first fines, panics, and has no framework for what's actually happening.
- **$10M–$15M:** OTIF fines are now material. The ops lead reacts to each fine without seeing the pattern. The internal fill-rate number looks fine, so the team doesn't understand why the retailer keeps penalizing them.
- **$15M–$20M:** OTIF is a board-level concern. Walmart's scorecard affects category standing. The brand needs to systematically reconcile its own view against the retailer's — and can't, because nobody owns the retailer scorecard data.

**How it compounds:** OTIF sits on the short-ship doom loop. An "in-full" failure is a short-ship — which triggers the OTIF fine AND empties the shelf, suppressing velocity, corrupting the forecast, and causing the next short-ship. The OTIF fine is the visible penalty; the velocity damage from the same empty shelf is the larger, invisible one. The brand sees the fine and never connects it to the velocity erosion sitting right next to it.

#### The Status Quo

The brand watches its internal fill rate (measured at its own dock) and feels fine. OTIF fines arrive and get absorbed or contested case by case, with no systematic reconciliation against the retailer's scorecard. Nobody pulls the supplier scorecard data, decomposes the failures, or reconciles the two views. So the brand keeps trusting the optimistic internal number and keeps getting penalized against the pessimistic real one — never seeing the gap, never knowing whether the problem is logistics or production.

---

### 2. Why This Piece

**It reveals the gap nobody measures.** The "you think 96%, they say 86%" reframe is the hook — it exposes a blind spot the brand didn't know it had, on a metric that's costing them six figures and threatening their shelf position. That's the kind of "stop and rethink your business" moment a portfolio piece needs.

**It completes the short-ship workstream.** The practice has built around the short-ship doom loop. This is the missing measurement piece:
- **OTIF Blind Spot** *reveals* how bad fill performance actually is and where the failures come from (diagnosis).
- **Production Demand Forecast** *prevents* the short-ships that cause in-full failures (forward-looking).
- **The 150 Cases** *quantifies the cost* of the short-ships (financial impact).
Three pieces, one loop, three angles. This one is the diagnostic that tells you whether you even have the problem — and most brands do, they just can't see it.

**It separates the two failure modes — which tells the brand what to fix.** The single most useful output is the decomposition: of your OTIF gap, how much is on-time (logistics) and how much is in-full (production)? Brands routinely fix the wrong one because they've never split them. Splitting them redirects the brand's effort to the actual problem.

**It connects a compliance metric to financial outcomes.** OTIF is usually treated as an ops compliance chore. This piece ties it to dollars — fines AND velocity damage — which moves it from the ops queue to the CFO's and CEO's attention.

**All-tier.** Every brand shipping to a retailer with an OTIF program faces this. The $5M brand getting its first Walmart fines and the $20M brand managing a portfolio of retailer scorecards have the same blind spot at different scale.

---

### 3. The Analysis — What It Reveals

The heart of the piece: reconciling the two numbers and decomposing the gap.

**Move 1 — Reconcile the two docks (the Dual-Dock framework).**
Pull the retailer's OTIF scorecard (from the supplier portal) and reconcile it against the brand's own internal fulfillment logs. The Fulfillment Dock (brand internal, measured against acknowledged 855s) vs. the Consignee Dock (retailer receiving, measured against original 850s). Surface the headline gap: internal fill rate vs. retailer-measured OTIF. This single comparison — "you think 96%, they score you at 86%" — is the reveal. Most brands have never put the two numbers side by side.

**Move 2 — Decompose the gap into on-time vs. in-full.**
Split the OTIF shortfall into its two components. How much of the gap is "on-time" failures (late deliveries, missed must-arrive-by-dates, missed appointment windows)? How much is "in-full" failures (shipped short, partial receipts)? This is the move that tells the brand whether its problem is logistics or production — the single most actionable output.

**Move 3 — Attribute failures to root causes.**
Within each component, attribute to specific causes: in-full failures to production short-ships vs. *intentional order trimming in the ERP* vs. data errors; on-time failures to warehouse-late-departure vs. transit bottleneck vs. missed appointment. The on-time attribution is derived independently from EDI timestamps — the 856 (ASN, when it actually shipped) and the carrier 214 (Transportation Status, where it was in transit) — so a late delivery can be pinned to *the brand's warehouse leaving late* vs. *the carrier moving slow*. That distinction matters: one fires the warehouse, the other fires the carrier, and getting it wrong wastes the fix. Each root cause points to a different owner.

**Move 4 — Compute true fill rate (the honest number).**
The brand's internal fill rate is measured against *acknowledged* orders — after the brand has already trimmed lines it knew it couldn't fill. Compute fill against the *original demand* (the original PO), which is what the retailer measures against. The difference between "fill rate against what we acknowledged" and "fill rate against what they ordered" is the order-trimming blind spot — a number most brands have never seen.

**Move 5 — Quantify the exposure.**
Two numbers: the OTIF fine exposure (3% of COGS on affected shipments, retailer by retailer) and the velocity damage (the revenue lost from the empty shelves that the in-full failures created). The fine is the visible cost; the velocity damage is usually larger and always invisible. Putting both on the table is what moves OTIF from an ops chore to a CFO priority.

#### The Output

- **The Retailer Reconciliation Matrix:** the internal-vs-retailer comparison, retailer by retailer, charting the brand's fulfillment metrics against verified scorecard performance, with the on-time/in-full decomposition and root-cause attribution.
- **The EDI Audit Sheet:** a transaction-level ledger comparing the brand's EDI dispatch and carrier timestamps (856 + 214) against the retailer's penalty file — dispute-ready documentation that turns the piece into an independent *Retailer Audit Engine* rather than a passive scorecard mirror.

Together they show the brand, for the first time, how bad its fill performance actually is, exactly where the failures originate, and where the retailer's own number can be challenged.

#### The Margin Math

For a $25M brand with a 10-point gap between internal fill rate and retailer-scored OTIF:

| Failure Category | Impact | Annual Profit Leak | Corrective Action |
|------------------|--------|:------------------:|-------------------|
| On-time logistics lag | ~5-point score drop | $100K–$200K | Optimize carrier routing, adjust ship leads |
| In-full product shortages | ~4-point score drop | $60K–$120K | Production forecast guardrails (→ Production Demand Forecast) |
| Hidden shelf velocity loss | empty shelves | $200K–$500K | Recover lost distribution, protect shelf position |
| **Total exposure** | **10-point blind spot** | **$360K–$800K** | **Turn ops metrics into retained profit** |

- **Fines are the visible cost; velocity damage is the larger, invisible one.** The OTIF fine (3% of COGS on affected shipments) is real but usually smaller than the revenue lost from the empty shelves the in-full failures created.
- **Misdirected remediation is pure waste.** Brands fixing the wrong failure mode (logistics when it's production, or vice versa) burn the remediation budget entirely. The decomposition redirects it to the actual problem.
- **Category-standing risk** is unquantifiable but existential — a chronic OTIF offender risks delisting at the next review.

**Total quantifiable exposure: $360K–$800K/year** at a $25M brand, most of it in the velocity damage the brand never attributes to OTIF — plus the un-priced risk to shelf position.

#### Before / After

- **Before:** Internal dashboard says 96% fill. The team feels fine. OTIF fines arrive and get absorbed. The ops lead throws resources at logistics. Fines continue, because more than half the problem was production short-ships nobody decomposed. The brand trusts the wrong number and fixes the wrong thing.

- **After:** The reconciliation shows the real OTIF is 86%. The decomposition shows 4 of the 10 points are production short-ships, not logistics. The brand redirects effort to production, closes the in-full gap, and watches both the fines and the velocity damage fall. The CFO sees OTIF as a $500K problem, not a compliance footnote.

#### Who Else Sees This?

- **Primary:** COO / VP Ops (owns fulfillment), CFO (owns the fine line and now sees the velocity damage), the ops/logistics lead (gets told which failure mode to actually fix).
- **Secondary:** CEO (OTIF as a shelf-position risk, not just a fine), the retailer's buyer (a brand that proactively fixes its OTIF is a better-regarded vendor).
- **How it gets shared:** The ops lead brings the reconciliation to the COO: "We've been fixing logistics, but 4 of our 10 points are production." That single decomposition reorganizes the remediation plan. The CFO sees the velocity-damage number and reprioritizes.

---

### 4. Technical Notes (kept light)

The piece reconciles two sources the brand already has but never joins: the retailer OTIF scorecard (from the supplier portal) and the brand's own shipping/EDI data. The analytical substance is in the reconciliation logic and the on-time/in-full decomposition, not the tooling. Computing true on-time performance can be done precisely from EDI timestamps (the 856 ASN and delivery records) rather than relying on the retailer's summary score — which is itself a differentiator, since it lets the brand verify the retailer's number rather than just accept it. Runs on the Cinderhaven Data Platform alongside the shipment and EDI marts. Delivered as a diagnostic view plus a reconciliation workbook. Specifics scoped later.

---

### 5. Skills Demonstrated

- **Cross-system reconciliation** — joining the retailer's scorecard to the brand's shipping data and explaining the divergence. This is the core skill and the core value.
- **OTIF domain fluency** — MABD, appointment windows, line-fill vs. case-fill vs. unit-fill definitions, retailer-specific scoring rules, the 3%-of-COGS fine structure. Specialized compliance knowledge that signals deep retail expertise.
- **Failure decomposition** — splitting a single compliance number into on-time vs. in-full and attributing to root causes. The decomposition is what makes the analysis actionable.
- **Computing true OTIF from EDI timestamps** — deriving on-time performance independently from the 856/delivery records rather than trusting the retailer's summary. Lets the brand audit the retailer's number.

---

### 6. Foot-in-the-Door Offering

- **Offering name:** OTIF Reconciliation Diagnostic
- **Format:** Fixed-fee 2–3 week engagement
- **Price range:** $15K–$25K
- **What the client gets:**
  1. Reconciliation of internal fill rate against retailer OTIF scorecards, retailer by retailer
  2. Decomposition of the gap into on-time vs. in-full
  3. Root-cause attribution within each component
  4. True fill rate against original demand (the order-trimming blind spot exposed)
  5. Dual exposure quantified — fines plus velocity damage
  6. A remediation priority that points at the *actual* failure mode, not the assumed one
- **Why this piece sells it:** The reframe — "you think 96%, they score you at 86%" — is a claim the brand can immediately test against their own scorecard, and it's almost always true. Once they see the gap, they want the decomposition that tells them what to fix. The dual-exposure number (fines + velocity) justifies the fee several times over.

#### Client Lift

- **What the client provides:** Access to the retailer supplier scorecards (Walmart Retail Link OTIF reports, etc.), shipping/EDI data (856 ASNs, delivery confirmations), and original PO data. The scorecard access is sometimes the friction — the brand has the portal login but has never pulled the OTIF detail. One kickoff plus portal access.

#### The DIY Defense

- **The two numbers live in two places nobody joins.** The retailer scorecard is in the supplier portal; the brand's fill data is in its ERP/EDI. Reconciling them — and explaining the divergence line by line — is the work nobody internal has done because it spans ops, logistics, and the retailer relationship.
- **The decomposition requires knowing the retailer's rules.** Splitting on-time from in-full correctly means knowing how each retailer defines and measures each — MABD windows, appointment scheduling, fill calculation. Get the rules wrong and the decomposition is wrong.
- **Computing true OTIF from EDI timestamps is specialized.** Deriving on-time performance from the 856 and delivery records — to verify rather than trust the retailer's score — requires EDI fluency most internal teams lack.

---

### 7. Competitor / Existing Content Scan

- **What exists:**
  - **OTIF/supply-chain compliance software** (SPS Commerce, TrueCommerce analytics, Vendor Performance tools) — some surface scorecard data, but they rarely reconcile it against the brand's own shipping data or decompose root causes; they report the retailer's number back, they don't audit it.
  - **3PL/logistics dashboards** — show the brand's shipping performance, not the retailer's scorecard, and never the gap between them.
  - **Walmart/retailer vendor guides** — document the OTIF rules but don't help the brand measure or decompose its own performance.
  - **Generic "improve your OTIF" content** — trade tips. Not diagnostic, not reconciled, not decomposed.
- **What's missing:** A diagnostic that reconciles the brand's view against the retailer's scorecard, decomposes the gap into on-time vs. in-full, attributes root causes, and prices both the fines and the velocity damage — for the mid-market specialty food brand.
- **Your angle:** The reconciliation (two docks, one truth) + the on-time/in-full decomposition + the dual exposure + computing true OTIF from EDI to audit the retailer's number. Nobody serves this band with that combination.

---

### 8. Cinderhaven Integration

Cinderhaven's internal dashboards show a 95% fill rate. Walmart's supplier scorecard shows 86% OTIF. The reconciliation reveals:

- **The 9-point gap splits 5/4:** ~5 points are on-time failures (the carrier missing must-arrive-by-date appointment windows) and ~4 points are in-full failures (production short-ships).
- **The brand had been fixing logistics** — but nearly half the problem was production. The remediation effort was aimed at the wrong failure mode.
- **True fill against original demand is lower still:** Cinderhaven trims order lines it can't fill before acknowledging, so its "95%" is measured against a reduced base. Against the original POs, true fill is ~91%.
- **Exposure:** ~$140K/year in OTIF fines, plus an estimated ~$320K/year in velocity damage from the empty-shelf periods the in-full failures created.

Headline: **Cinderhaven thought it was at 95% and fixing the right problem. It was at 86%, fixing the wrong one, and the OTIF blind spot was a ~$460K/year problem hiding behind a number measured at the wrong dock.**

Runs on the existing Cinderhaven Data Platform — joins the shipment, EDI, and PO marts, plus a synthetic Walmart OTIF scorecard layer. Consistent with the short-ship figures in The 150 Cases and the OOS events in Production Demand Forecast and Competitive Shelf Intelligence.

---

### 9. Tactical Notes

- **Lead with the two numbers.** "You think 96%, they score you at 86%" is the entire hook. Open with it. The gap is the blind spot; everything else is explaining and pricing it.
- **The on-time/in-full decomposition is the most actionable output — make it prominent.** Telling a brand "your OTIF is bad" is useless. Telling them "4 of your 10 points are production short-ships, not logistics" redirects their entire remediation effort. That split is the deliverable that earns the fee.
- **Connect to velocity damage, not just fines.** The fines are real but often the smaller number. The empty-shelf velocity damage from the in-full failures is larger and invisible. Pricing both is what moves OTIF from an ops chore to a CFO priority — and ties this piece to the doom-loop theme running through the portfolio.
- **The order-trimming blind spot is the subtle, credible finding.** Brands inflate their fill rate by trimming order lines they can't fill before acknowledging — so their internal number is measured against a base they've already shrunk. Surfacing "your true fill against the original PO is lower than your reported fill" is the kind of precise, slightly uncomfortable insight that signals the analysis is real.
- **Computing true OTIF from EDI timestamps is the trust play.** Reconciling against the retailer's score is good; being able to *derive* on-time performance independently from the 856 and delivery records — and verify or challenge the retailer's number — is what makes the brand trust the diagnostic and what makes it dispute-ready.

#### The Credibility Marker

Knowing that "fill rate" and "OTIF" are measured at different docks against different baselines — the brand measures shipped-vs-acknowledged at its own dock; the retailer measures received-on-time-and-complete-vs-original-PO at theirs — and that the gap between them is manufactured by order trimming, MABD misses, appointment scheduling, and partial receipts. The deeper marker: knowing that you can compute true on-time performance from EDI 856 and delivery timestamps to *audit* the retailer's scorecard rather than just accept it, and that Walmart's OTIF rules (MABD windows, the 3%-of-COGS fine, the in-full calculation) differ from Target's and Kroger's in specific, measurable ways. Generic "OTIF is important" is not the signal; "here's exactly why your internal number and their scorecard diverge, and here's how to compute the truth independently" is.

#### Data Paranoia / Security

OTIF scorecards and fill performance expose the brand's operational weaknesses and retailer relationships. Cinderhaven's data is synthetic. Engagement uses NDA; analysis runs on the brand's own data and scorecard exports with nothing retained.

---

### 10. Open Questions

- [x] ~~**Fold in #46 (EDI: True OTIF from EDI timestamps)?**~~ Resolved: Yes, absorbed into Moves 2–3. Deriving on-time performance independently from EDI 856 + carrier 214 timestamps is what makes this an independent Retailer Audit Engine rather than a scorecard mirror.
- [x] ~~**Relationship to #148 (Real-time OTIF monitoring)?**~~ Resolved: Keep separate. This diagnostic is historical; continuous real-time monitoring is the retainer/upsell.
- [x] ~~**Single retailer or multi-retailer at launch?**~~ Resolved: Walmart MVP (clearest rules, most famous program). Design the data models modularly so Target, Kroger, etc. plug in as extensions later.
- [ ] **Real or synthetic scorecard data for Cinderhaven?** Synthetic Walmart OTIF scorecard, seeded to produce the 5/4 on-time/in-full split and the exposure figures described.

---

### 11. Build Estimate

- **Effort level:** Medium. The reconciliation logic and the on-time/in-full decomposition are the work. The true-OTIF-from-EDI computation adds some depth. Runs on the existing platform.
- **Time estimate:** To be scoped, but comparable to the other diagnostic pieces (~2–3 weeks). The retailer-rules knowledge (how each defines on-time and in-full) is the long pole, not the code.

#### Out of Scope

- **Real-time OTIF monitoring.** The diagnostic reveals the problem on historical data; continuous live monitoring is the upsell (#148).
- **Fixing the failures.** The piece tells the brand whether to fix logistics or production; the actual remediation (carrier management, production planning) is engagement or other-piece territory (Production Demand Forecast for the in-full side).
- **Dispute automation.** The piece makes OTIF fines dispute-ready by computing true performance; automating the disputes is deduction-recovery territory.
- **Multi-retailer rule library at launch.** Walmart MVP; other retailers' rules in v2.

---

### Relationship to Existing Inventory

| Project | Relationship |
|---------|-------------|
| The 150 Cases You Didn't Ship (#6, built) | **Short-ship workstream sibling.** 150 Cases quantifies the cost of short-ships; this reveals how bad the in-full failures actually are via the retailer scorecard. |
| Production Demand Forecast (#4 backlog, briefed) | **Short-ship workstream sibling.** This reveals the in-full failure rate; Production Demand Forecast prevents the short-ships causing it. Diagnosis ↔ prevention. |
| Retailer Deduction Recovery (#4, built) | OTIF fines are a deduction category; this computes true OTIF to make the fines dispute-ready, recovery handles the disputing. |
| EDI Pre-flight (#5, built) | EDI timestamps (856) feed the true-OTIF computation; Pre-flight validates the 856s upstream. |
| Chargeback Prediction Model (#5 backlog, briefed) | OTIF fines are a predictable chargeback type; this decomposes them, the prediction model forecasts them. |
| Brainstorm #46 EDI: True OTIF from EDI timestamps (31) | **Absorbed** — the independent on-time computation (856 + 214) and the Retailer Audit Engine trust play (Moves 2–3). |
| Brainstorm #148 Real-time OTIF monitoring (26) | **Keep separate** — the live-monitoring version, the engagement upsell / retainer. |
| Umbrella (#3, built) | Maps to a decision in the ten-decision framework — "are operational bottlenecks quietly killing our repeat retailer orders?" |

---

*Brief complete when open questions are resolved.*
