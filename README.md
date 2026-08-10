# OTIF Blind Spot — Cinderhaven Provisions

Your fill rate says 99%. Walmart scores you at 84%. This tool shows where the 14.8-point gap comes from and what it costs.

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

The hero defaults to the last-52-weeks view (~$59K exposure); the $57,197 figure is the full-corpus (2023–2025) total.

The gap is almost entirely in-full (12.7 of 14.8 pts). On-time performance is strong. The blind spot is quantity shortfalls: a shipment that ships 99% of its units scores 99% on fill rate but 0% on OTIF.

**Root causes (Walmart):**

| Cause | Gap pts | % of Gap |
|---|---|---|
| Short-ship | 10.66 | 72.1% |
| Warehouse late | 2.12 | 14.3% |
| Receiving discrepancy | 2.00 | 13.5% |

Short-ships drive 72% of the gap. Receiving discrepancies — where the dock scan disagrees with what was shipped — account for 14%. The brand's internal metrics never see these. That is the blind spot.

The tool distinguishes two cost types:

- **Measured** ($23.7K/yr) — actual compliance fines from platform chargebacks (short_ship, late_delivery, receiving_discrepancy). Real dollars deducted from remittances.
- **Modeled** ($33.5K/yr) — estimated shelf-velocity damage at $3.50 per unit of retailer shortfall. A rate assumption, not a platform-derived figure, and labeled accordingly in the tool.

## Why it matters

Brands manage to the metric they can see — internal fill rate — while retailers fine and delist against the metric they score — OTIF. A brand can believe it is a 99% performer while its largest customer scores it in penalty territory. The fines are the visible cost; the compounding cost is shelf-velocity damage and the deauthorization conversation that follows a bad scorecard. Making the gap visible, attributable, and priced turns "Walmart says we're failing" from a dispute into a fixable operations list, ranked by dollar impact.

## Run

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

## Stack

- **Frontend:** React, TypeScript, Vite
- **Charts:** Observable Plot (SVG)
- **Data pipeline:** Python → JSON from platform Postgres
- **Deployment:** Cloudflare Workers

## Data contract

Consumes the Cinderhaven Data Platform directly:

- `fct_retailer_shipments` / `fct_retailer_orders` — shipment timing and PO context for on-time scoring
- `fct_retailer_shipment_lines` — units ordered vs shipped (fill data)
- `fct_retailer_receipt_lines` — units received vs shipped (receiving discrepancies)
- `fct_chargebacks` where reason in (short_ship, late_delivery, receiving_discrepancy)

50 SKUs, 6 retailers, 36-month window (2023–2025). Canonical reference: `CINDERHAVEN_CANONICAL.md`.

**Overlap note:** Some short_ship failures surfaced here also appear in the short-ship-cost project (~$39.6K/yr in short_ship chargebacks). The canonical thesis range counts that overlap once, under short-ship cost.

## What this replaced

This tool previously synthesized OTIF events and normalized outputs to match hardcoded targets (95% internal / 86% retailer-scored / $433K exposure). The normalization layer overrode what the data actually said. The rebuild stripped it, pointed the pipeline at platform causal fulfillment events, and let the data produce the scores. The gap turned out to be 14.8 points, not 10 — still a significant finding, and the honest one.

## Client engagement use

The demo renders the committed Cinderhaven dataset (full corpus by default). To
analyze a **client's own OTIF scorecard** in place — validated, never committed,
never deployed — use client mode (see [INPUT-SPEC.md](INPUT-SPEC.md)):

```bash
pip install -e ../engagement-template/lib      # the shared lailara_engagement scaffold
python client_mode.py --config engagement.yml --input client-data/otif.csv \
    --out client-output [--final]
```

It computes the internal-fill vs retailer-OTIF gap, the on-time/in-full failure
split, and the fines exposure (annualized on the config window); velocity damage
is disclosed as a modeled figure the scorecard can't produce. Output to
`client-output/` (gitignored): a branded, provenance-footed, DRAFT-watermarked
`otif-gap-summary.html` + `summary.json`, or a Data Readiness Report if a required
column is missing. The demo app is never edited (golden-locked).

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Lailara LLC](https://lailarallc.com) — data hygiene and analytics consulting for specialty food brands scaling into national retail.
