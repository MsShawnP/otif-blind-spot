# OTIF Blind Spot — Cinderhaven Provisions

Your fill rate says 92%. Your retailers score you at 61%. This tool
shows where the 30-point gap comes from and what it costs.

Cinderhaven Provisions is a fictional ~$25M specialty food brand.
The dataset is synthetic. The methodology is real. Every OTIF score
is computed from platform shipment events, not synthesized to match
a target.

**Live:** https://otif.lailarallc.com

## What it finds

| Metric | Value |
|---|---|
| Internal fill rate (portfolio) | 92.0% |
| Walmart retailer-scored OTIF | 61.4% |
| Gap | 30.6 pts |
| Annual OTIF fines (measured) | $55,002 |
| Annual velocity damage (modeled) | $368,099 |
| Total annual exposure | $423,101 |

The gap is almost entirely in-full (28.9 of 30.6 pts). On-time
performance runs 97–100% across all retailers. The blind spot is
quantity shortfalls: a shipment that ships 95% of its units scores
95% on fill rate but 0% on OTIF.

## Per-retailer breakdown

| Retailer | Brand Fill | OTIF | Gap |
|---|---|---|---|
| Walmart | 89.4% | 61.4% | 28.0 pts |
| Kroger | 90.2% | 66.8% | 23.4 pts |
| Whole Foods | 94.0% | 70.2% | 23.8 pts |
| Sprouts | 93.6% | 72.4% | 21.2 pts |
| Costco | 91.7% | 72.8% | 18.9 pts |
| Regional | 95.0% | 79.1% | 15.9 pts |

Walmart is the weakest — lowest fill, lowest OTIF. Regional Group
is the strongest.

## Root causes (Walmart)

| Cause | Gap pts | % of Gap |
|---|---|---|
| Short-ship | 17.58 | 57.5% |
| Receiving discrepancy | 11.27 | 36.8% |
| Warehouse late | 1.75 | 5.7% |

Receiving discrepancies — where the dock scan disagrees with what
was shipped — account for 37% of Walmart's gap. The brand's
internal metrics never see these. That is the blind spot.

## Measured vs modeled

The tool distinguishes two cost types:

- **Measured** ($55K/yr) — actual compliance fines from platform
  chargebacks (short_ship, late_delivery, receiving_discrepancy).
  These are real dollars deducted from remittances.
- **Modeled** ($368K/yr) — estimated shelf-velocity damage at
  $3.50 per unit of retailer shortfall. This is a rate assumption,
  not a platform-derived figure, and is labeled accordingly in the
  tool.

## Data contract

Consumes the Cinderhaven Data Platform directly:

- `fct_retailer_shipment_lines` — units ordered vs shipped
- `fct_retailer_receipt_lines` — units received vs shipped
  (receiving discrepancies)
- `raw.retailer_chargebacks` where reason in (short_ship,
  late_delivery, receiving_discrepancy)
- `raw.retailer_orders` — delivery timing for on-time scoring

50 SKUs, 6 retailers, 36-month window (2023–2025). Canonical
reference: `CINDERHAVEN_CANONICAL.md`.

**Overlap note:** OTIF fines include $38.7K/yr in short_ship
chargebacks also counted in the short-ship-cost project. The
canonical thesis range counts these once, under short-ship cost.

## Stack

- **Frontend:** React, TypeScript, Vite
- **Charts:** D3 / custom SVG
- **Data pipeline:** Python → JSON from platform Postgres
- **Deployment:** Cloudflare Pages

## Run locally

```bash
cd frontend
npm install
npm run dev
```

To regenerate data from the platform:

```bash
python scripts/00_query_cinderhaven.py
python scripts/01_compute_otif.py
python scripts/02_export_json.py
```

Requires a flyctl proxy to the Cinderhaven database or a local
Docker replica.

## What this replaced

This tool previously synthesized OTIF events and normalized outputs
to match hardcoded targets (95% internal / 86% retailer-scored /
$433K exposure). The normalization layer overrode what the data
actually said. The rebuild stripped it, pointed the pipeline at
platform causal fulfillment events, and let the data produce the
scores. The gap turned out to be 30 points, not 10 — a much more
compelling finding, and the honest one.

---

Built by [Lailara LLC](https://lailarallc.com) — data hygiene and
analytics consulting for specialty food brands scaling into national
retail.

## License

MIT — see [LICENSE](LICENSE).
