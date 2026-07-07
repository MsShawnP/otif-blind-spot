# OTIF Blind Spot — Cinderhaven Provisions

Your fill rate says 99%. Walmart scores you at 85%. This tool shows where the 15-point gap comes from and what it costs.

**Live:** https://otif.lailarallc.com

Cinderhaven Provisions is a fictional ~$25M specialty food brand. The dataset is synthetic. The methodology is real. Every OTIF score is computed from platform shipment events, not synthesized to match a target.

## What it does

Reconciles a brand's internal fulfillment metrics against retailer-scored OTIF (On Time In Full), decomposes the gap into root causes, and prices the exposure:

| Metric | Value |
|---|---|
| Internal fill rate (portfolio) | 99.2% |
| Walmart retailer-scored OTIF | 84.5% |
| Gap | 14.8 pts |
| Annual OTIF fines (measured) | $23,697 |
| Annual velocity damage (modeled) | $33,500 |
| Total annual exposure | $57,197 |

The gap is almost entirely in-full (12.7 of 14.8 pts). On-time performance is strong. The blind spot is quantity shortfalls: a shipment that ships 99% of its units scores 99% on fill rate but 0% on OTIF.

**Root causes (Walmart):**

| Cause | Gap pts | % of Gap |
|---|---|---|
| Short-ship | 10.66 | 72.1% |
| Warehouse late | 2.12 | 14.3% |
| Receiving discrepancy | 2.00 | 13.5% |

Short-ships drive 72% of the gap. Receiving discrepancies — where the dock scan disagrees with what was shipped — account for 14%. The brand's internal metrics never see these. That is the blind spot.

The tool distinguishes two cost types:

- **Measured** ($24K/yr) — actual compliance fines from platform chargebacks (short_ship, late_delivery, receiving_discrepancy). Real dollars deducted from remittances.
- **Modeled** ($34K/yr) — estimated shelf-velocity damage at $3.50 per unit of retailer shortfall. A rate assumption, not a platform-derived figure, and labeled accordingly in the tool.

## Why it matters

Brands manage to the metric they can see — internal fill rate — while retailers fine and delist against the metric they score — OTIF. A brand can believe it is a 99% performer while its largest customer scores it in penalty territory. The fines are the visible cost; the compounding cost is shelf-velocity damage and the deauthorization conversation that follows a bad scorecard. Making the gap visible, attributable, and priced turns "Walmart says we're failing" from a dispute into a fixable operations list, ranked by dollar impact.

## Quick start

```bash
cd frontend
npm install
npm run dev
```

To regenerate data from the platform (requires a flyctl proxy to the Cinderhaven database or a local Docker replica):

```bash
flyctl proxy 5432 -a cinderhaven-db   # in another terminal
python scripts/run_pipeline.py        # runs 00_query_cinderhaven.py then 02_export_json.py
```

## Tech stack

- **Frontend:** React, TypeScript, Vite
- **Charts:** D3 / custom SVG
- **Data pipeline:** Python → JSON from platform Postgres
- **Deployment:** Cloudflare Pages

## Data contract

Consumes the Cinderhaven Data Platform directly:

- `fct_retailer_shipment_lines` — units ordered vs shipped
- `fct_retailer_receipt_lines` — units received vs shipped (receiving discrepancies)
- `raw.retailer_chargebacks` where reason in (short_ship, late_delivery, receiving_discrepancy)
- `raw.retailer_orders` — delivery timing for on-time scoring

50 SKUs, 6 retailers, 36-month window (2023–2025). Canonical reference: `CINDERHAVEN_CANONICAL.md`.

**Overlap note:** Some short_ship failures surfaced here also appear in the short-ship-cost project (~$39.6K/yr in short_ship chargebacks). The canonical thesis range counts that overlap once, under short-ship cost.

## What this replaced

This tool previously synthesized OTIF events and normalized outputs to match hardcoded targets (95% internal / 86% retailer-scored / $433K exposure). The normalization layer overrode what the data actually said. The rebuild stripped it, pointed the pipeline at platform causal fulfillment events, and let the data produce the scores. The gap turned out to be 15 points, not 10 — still a significant finding, and the honest one.

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Lailara LLC](https://lailarallc.com) — data hygiene and analytics consulting for specialty food brands scaling into national retail.
