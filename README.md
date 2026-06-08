# OTIF Blind Spot

A Lailara portfolio diagnostic that reconciles a specialty food brand's internal fill rate against retailer OTIF scorecards — exposing the gap between "96% internal" and "86% Walmart-scored," decomposing it into on-time vs. in-full failures, attributing root causes, and quantifying total exposure (fines + shelf-velocity damage).

## What it does

Brands measure fill rate at their own shipping dock (against acknowledged orders). Retailers measure OTIF at their receiving dock (against original purchase orders). Those two numbers diverge — sometimes by 10+ points — because of order trimming, carrier delays, missed appointment windows, and partial receipts. This diagnostic reconciles the two views, splits the gap into its failure modes, and tells the brand exactly what to fix.

Built on the Cinderhaven Data Platform with synthetic Walmart OTIF scorecard data.

## Data Contract

**Cinderhaven canonical dataset:** 50 SKUs / 5 production lines / 6 retailers.
**Scope:** This tool focuses on Walmart OTIF compliance. It intentionally analyzes a single-retailer subset of the full Cinderhaven dataset. Audits should not flag the absence of other retailers as data drift.

## Stack

- React + TypeScript + Vite + Observable Plot (frontend)
- Python + psycopg2 (data generation pipeline)
- Cloudflare Workers (deployment)
- Lailara Design System v2 (Playfair Display + Source Sans 3, canvas bg, SVG charts)

## How to run

**Prerequisites:** Node 18+, Python 3.11+, `flyctl` (Fly.io CLI), Cloudflare `wrangler` auth.

```bash
# 1. Start the DB proxy (Cinderhaven Postgres on Fly.io)
flyctl proxy 5432 -a cinderhaven-db

# 2. Generate the data (in a second terminal)
cd frontend
npm install
npm run pipeline        # runs Python scripts → writes JSON to src/data/

# 3. Run locally
npm run dev             # http://localhost:5173

# 4. Deploy to Cloudflare Workers
npm run deploy
```

Set `DATABASE_URL` or `POSTGRES_PASSWORD` in a `.env` file in the `scripts/` directory before running the pipeline. See `scripts/otif_config.py` for the full config.

## Data contract

Canonical Cinderhaven conformance — 50 SKUs across 5 product lines and 6 contracted retailers.

## Part of the short-ship workstream

- **OTIF Blind Spot** (this piece) — reveals how bad fill performance actually is and where failures originate
- **The 150 Cases** — quantifies the cost of short-ships
- **Production Demand Forecast** — prevents the short-ships that cause in-full failures

---

Built by [Lailara LLC](https://lailarallc.com) — data hygiene and analytics consulting for specialty food brands scaling into national retail.
