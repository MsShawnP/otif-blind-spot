# INPUT-SPEC — otif-blind-spot (client mode)

What to hand the tool in a client engagement. One OTIF scorecard file (one row
per shipment), CSV or XLSX. Derived from the fields the engine consumes
(`frontend/src/computeMetrics.ts`, `audit_rows.json`), not the README.

## Required columns

| Canonical | Type | Used for |
|---|---|---|
| `shipment_id` | identifier (text, unique) | Row key. §1 |
| `ship_date` | date | Windowing + fines annualization. §1 |
| `on_time_result` | true/false | On-time pass/fail (accepts true/false, yes/no, pass/fail, on-time/late). §1 |
| `in_full_result` | true/false | In-full pass/fail (accepts true/false, yes/no, pass/fail, in-full/short). §1 |
| `po_units` | number ≥ 0 | Units ordered on the PO (internal-fill denominator). §1 |
| `shipped_units` | number ≥ 0 | Units shipped (internal-fill numerator). §1 |

## Optional columns

| Canonical | Type | Unlocks |
|---|---|---|
| `otif_fine` | number ≥ 0 | Per-shipment OTIF fine → fines exposure (total + annualized). Absent → disclosed, fines omitted. |
| `retailer` | string | Which retailer's scorecard. |

## What it computes

- **Internal fill rate** = Σ shipped_units / Σ po_units (fill at your dock).
- **Retailer OTIF** = share of shipments both on time and in full (their dock).
- **Gap** = internal fill − retailer OTIF, in points, computed from the raw rates.
- **On-time / in-full failure rates**, and **fines exposure** (total + ×12/window
  annualized) if `otif_fine` is present.

**Velocity damage** (lost shelf-sales from OTIF failures) is a *modeled* figure in
the demo. It cannot be derived from a scorecard alone, so it is **disclosed as a
data limitation**, never invented.

## Basis & window (engagement.yml)

```yaml
as_of_date: "2025-12-31"          # analysis anchor; NEVER today's date
basis:
  window_months: 36               # annualization divisor for fines
  window_label: "Jan 2023 – Dec 2025"   # printed beside the annualized figure
```

## Run

```bash
pip install -e ../engagement-template/lib
python client_mode.py --config engagement.yml --input client-data/otif.csv \
    --out client-output [--final]
```

Output to `client-output/` (gitignored): a branded, provenance-footed,
DRAFT-watermarked `otif-gap-summary.html` (the fill-vs-OTIF gap, failure split,
fines exposure — each with its basis and window) + `json/summary.json`; or a Data
Readiness Report if a required column is missing. The demo React app is never
edited.
