"""Compute OTIF scores from platform fulfillment data and export to frontend.

Input: cache/platform_fulfillment.json (from 00_query_cinderhaven.py)
Output: frontend/src/data/{summary,root_causes,true_fill,exposure,audit_rows}.json

All scores are derived from platform causal fulfillment data.
No target-locking or normalization -- the data produces the numbers.
Velocity damage is the only modeled component (labeled explicitly).
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import date, timedelta

from otif_config import (
    CACHE_DIR, DATA_OUT_DIR, WINDOW_START, WINDOW_END,
    RETAILER_MABD_DAYS, RETAILER_NAMES, RETAILER_NAME_TO_ID,
    VELOCITY_DAMAGE_PER_UNIT,
)


def _date_or_none(s: str | None) -> date | None:
    if s is None:
        return None
    try:
        return date.fromisoformat(s[:10])
    except (ValueError, TypeError):
        return None


def _load_platform_data() -> dict:
    path = os.path.join(CACHE_DIR, "platform_fulfillment.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Platform data not found: {path}\n"
            "Run 00_query_cinderhaven.py first."
        )
    with open(path) as f:
        return json.load(f)


def _join_shipment_data(data: dict) -> list[dict]:
    """Join shipments with line aggregates and receipt aggregates."""
    ship_line_map = {r["shipment_id"]: r for r in data["shipment_line_aggs"]}
    receipt_map = {r["shipment_id"]: r for r in data["receipt_line_aggs"]}

    joined = []
    for s in data["shipments"]:
        sid = s["shipment_id"]
        sl = ship_line_map.get(sid, {})
        rl = receipt_map.get(sid, {})

        row = dict(s)
        row["units_ordered"] = int(sl.get("units_ordered") or s.get("po_units") or 0)
        row["units_shipped"] = int(sl.get("units_shipped") or 0)
        row["units_short"] = int(sl.get("units_short") or 0)
        row["shortfall_reasons"] = sl.get("shortfall_reasons") or []

        row["units_received"] = int(rl.get("units_received") or row["units_shipped"])
        row["units_discrepant"] = int(rl.get("units_discrepant") or 0)
        row["discrepancy_reasons"] = rl.get("discrepancy_reasons") or []

        joined.append(row)

    return joined


def _compute_otif(shipments: list[dict]) -> list[dict]:
    """Add OTIF scoring fields to each shipment."""
    for row in shipments:
        retailer_id = row["retailer_id"]
        mabd_days = RETAILER_MABD_DAYS.get(retailer_id, 5)

        requested = _date_or_none(row.get("requested_ship_date"))
        delivery = _date_or_none(row.get("delivery_date"))

        brand_on_time = bool(row.get("is_on_time"))

        if requested and delivery:
            mabd = requested + timedelta(days=mabd_days)
            retailer_on_time = delivery <= mabd
            row["mabd"] = mabd.isoformat()
        else:
            retailer_on_time = brand_on_time
            row["mabd"] = None

        units_ordered = row["units_ordered"]
        units_shipped = row["units_shipped"]
        units_received = row["units_received"]

        brand_in_full = units_shipped >= units_ordered if units_ordered > 0 else True
        retailer_in_full = units_received >= units_ordered if units_ordered > 0 else True

        row["brand_on_time"] = brand_on_time
        row["retailer_on_time"] = retailer_on_time
        row["brand_in_full"] = brand_in_full
        row["retailer_in_full"] = retailer_in_full
        row["retailer_otif"] = retailer_on_time and retailer_in_full

        if not retailer_on_time:
            row["on_time_root_cause"] = "warehouse_late" if not brand_on_time else "carrier_late"
        else:
            row["on_time_root_cause"] = None

        if not retailer_in_full:
            row["in_full_root_cause"] = "short_ship" if not brand_in_full else "receiving_discrepancy"
        else:
            row["in_full_root_cause"] = None

        retailer_shortfall = max(0, units_ordered - units_received)
        row["velocity_damage"] = round(retailer_shortfall * VELOCITY_DAMAGE_PER_UNIT, 2)

    return shipments


def _retailer_metrics(shipments: list[dict]) -> dict[str, dict]:
    """Compute per-retailer OTIF metrics."""
    by_retailer: dict[str, list[dict]] = defaultdict(list)
    for s in shipments:
        by_retailer[s["retailer_id"]].append(s)

    metrics = {}
    for rid, rows in sorted(by_retailer.items()):
        total = len(rows)
        total_ordered = sum(r["units_ordered"] for r in rows)
        total_shipped = sum(r["units_shipped"] for r in rows)
        total_received = sum(r["units_received"] for r in rows)
        otif_pass = sum(1 for r in rows if r["retailer_otif"])
        on_time_pass = sum(1 for r in rows if r["retailer_on_time"])
        in_full_pass = sum(1 for r in rows if r["retailer_in_full"])

        metrics[rid] = {
            "retailer_id": rid,
            "retailer_name": RETAILER_NAMES.get(rid, rid),
            "shipment_count": total,
            "brand_fill": round(total_shipped / total_ordered, 4) if total_ordered else 0,
            "retailer_fill": round(total_received / total_ordered, 4) if total_ordered else 0,
            "on_time_rate": round(on_time_pass / total, 4) if total else 0,
            "in_full_rate": round(in_full_pass / total, 4) if total else 0,
            "otif_rate": round(otif_pass / total, 4) if total else 0,
        }

    return metrics


def build_summary(shipments: list[dict], retailer_metrics: dict) -> dict:
    """Build summary.json -- portfolio fill vs Walmart OTIF."""
    total_ordered = sum(s["units_ordered"] for s in shipments)
    total_shipped = sum(s["units_shipped"] for s in shipments)
    internal_fill = round(total_shipped / total_ordered, 4) if total_ordered else 0

    walmart = retailer_metrics.get("RET-WALMART", {})
    retailer_otif = walmart.get("otif_rate", 0)

    walmart_rows = [s for s in shipments if s["retailer_id"] == "RET-WALMART"]

    gap_pts = round((internal_fill - retailer_otif) * 100, 2)

    wm_total = len(walmart_rows)
    if wm_total > 0 and gap_pts > 0:
        wm_ontime_fail = sum(1 for s in walmart_rows if not s["retailer_on_time"])
        wm_infull_fail = sum(1 for s in walmart_rows if not s["retailer_in_full"])
        wm_total_fails = wm_ontime_fail + wm_infull_fail
        if wm_total_fails > 0:
            ontime_gap_pts = round(wm_ontime_fail / wm_total_fails * gap_pts, 2)
            infull_gap_pts = round(gap_pts - ontime_gap_pts, 2)
        else:
            ontime_gap_pts = 0.0
            infull_gap_pts = 0.0
    else:
        ontime_gap_pts = 0.0
        infull_gap_pts = 0.0

    return {
        "internal_fill_rate": internal_fill,
        "retailer_otif": retailer_otif,
        "gap_pts": gap_pts,
        "ontime_gap_pts": ontime_gap_pts,
        "infull_gap_pts": infull_gap_pts,
        "total_shipments": len(shipments),
        "walmart_shipments": len(walmart_rows),
        "window_start": WINDOW_START.isoformat(),
        "window_end": WINDOW_END.isoformat(),
    }


def build_root_causes(shipments: list[dict], summary: dict) -> list[dict]:
    """Build root_causes.json from Walmart failure modes."""
    gap_pts = summary["gap_pts"]
    ontime_gap = summary["ontime_gap_pts"]
    infull_gap = summary["infull_gap_pts"]

    walmart = [s for s in shipments if s["retailer_id"] == "RET-WALMART"]

    cause_counts: dict[str, int] = defaultdict(int)
    for s in walmart:
        if s.get("on_time_root_cause"):
            cause_counts[s["on_time_root_cause"]] += 1
        if s.get("in_full_root_cause"):
            cause_counts[s["in_full_root_cause"]] += 1

    total_ontime_fails = cause_counts.get("warehouse_late", 0) + cause_counts.get("carrier_late", 0)
    total_infull_fails = cause_counts.get("short_ship", 0) + cause_counts.get("receiving_discrepancy", 0)

    def _gap(cause: str, mode: str) -> float:
        total_mode_fails = total_ontime_fails if mode == "on_time" else total_infull_fails
        mode_gap = ontime_gap if mode == "on_time" else infull_gap
        if total_mode_fails == 0:
            return 0.0
        return round(cause_counts.get(cause, 0) / total_mode_fails * mode_gap, 2)

    causes = [
        {"cause": "warehouse_late",        "failure_mode": "on_time", "label": "Warehouse late"},
        {"cause": "carrier_late",          "failure_mode": "on_time", "label": "Carrier late"},
        {"cause": "short_ship",            "failure_mode": "in_full", "label": "Short-ship"},
        {"cause": "receiving_discrepancy", "failure_mode": "in_full", "label": "Receiving discrepancy"},
    ]

    result = []
    for c in causes:
        count = cause_counts.get(c["cause"], 0)
        gp = _gap(c["cause"], c["failure_mode"])
        result.append({
            "cause": c["cause"],
            "label": c["label"],
            "failure_mode": c["failure_mode"],
            "gap_pts": gp,
            "shipment_count": count,
            "pct_of_gap": round(gp / gap_pts, 4) if gap_pts else 0,
        })

    return sorted(result, key=lambda x: x["gap_pts"], reverse=True)


def build_true_fill(shipments: list[dict]) -> dict:
    """Build true_fill.json -- brand fill vs retailer fill (receiving gap).

    Field mapping from original semantics:
      fill_vs_855 -> brand fill (units_shipped / units_ordered)
      fill_vs_850 -> retailer fill (units_received / units_ordered)
      trimming_gap_pts -> receiving discrepancy gap in pts
    """
    walmart = [s for s in shipments if s["retailer_id"] == "RET-WALMART"]

    total_ordered = sum(s["units_ordered"] for s in walmart)
    total_shipped = sum(s["units_shipped"] for s in walmart)
    total_received = sum(s["units_received"] for s in walmart)

    brand_fill = round(total_shipped / total_ordered, 4) if total_ordered else 0
    retailer_fill = round(total_received / total_ordered, 4) if total_ordered else 0
    receiving_gap_pts = round((brand_fill - retailer_fill) * 100, 2)

    shipments_with_discrepancy = sum(
        1 for s in walmart if s["units_discrepant"] > 0
    )

    return {
        "fill_vs_855": brand_fill,
        "fill_vs_850": retailer_fill,
        "trimming_gap_pts": receiving_gap_pts,
        "orders_with_trimming": shipments_with_discrepancy,
        "pct_orders_trimmed": round(shipments_with_discrepancy / len(walmart), 4) if walmart else 0,
    }


def build_exposure(shipments: list[dict], chargebacks: list[dict]) -> dict:
    """Build exposure.json from real chargebacks + modeled velocity damage."""
    walmart_cbs = [
        cb for cb in chargebacks
        if RETAILER_NAME_TO_ID.get(cb.get("retailer")) == "RET-WALMART"
    ]
    total_fines = sum(cb["amount"] for cb in walmart_cbs)

    walmart_shipments = [s for s in shipments if s["retailer_id"] == "RET-WALMART"]
    total_velocity = sum(s["velocity_damage"] for s in walmart_shipments)

    window_months = (
        (WINDOW_END.year - WINDOW_START.year) * 12
        + WINDOW_END.month - WINDOW_START.month + 1
    )
    scale = 12 / window_months if window_months > 0 else 1.0

    annual_fines = round(total_fines * scale, 2)
    annual_velocity = round(total_velocity * scale, 2)

    by_quarter: dict[str, float] = defaultdict(float)
    for cb in walmart_cbs:
        month_str = cb.get("month", "")
        if month_str and len(month_str) >= 7:
            year = int(month_str[:4])
            month = int(month_str[5:7])
            q = (month - 1) // 3 + 1
            key = f"{year}-Q{q}"
            by_quarter[key] += cb["amount"]

    fines_by_quarter = [
        {"quarter": k, "fines": round(v, 2)}
        for k, v in sorted(by_quarter.items())
    ]

    velocity_by_shipment = sorted(
        [{"order_id": s["order_id"], "velocity_damage": s["velocity_damage"]}
         for s in walmart_shipments if s["velocity_damage"] > 0],
        key=lambda x: x["velocity_damage"],
        reverse=True,
    )[:10]

    return {
        "annual_fines": annual_fines,
        "fines_source": "platform",
        "annual_velocity_damage": annual_velocity,
        "velocity_source": "modeled",
        "total_exposure": round(annual_fines + annual_velocity, 2),
        "fines_by_quarter": fines_by_quarter,
        "velocity_by_sku": velocity_by_shipment,
    }


def build_audit_rows(shipments: list[dict]) -> list[dict]:
    """Build audit_rows.json -- per-shipment OTIF detail for Walmart."""
    walmart = [s for s in shipments if s["retailer_id"] == "RET-WALMART"]

    rows = []
    for s in walmart:
        rows.append({
            "shipment_id": s["shipment_id"],
            "po_number": s["po_number"],
            "ship_date": s.get("ship_date"),
            "mabd": s.get("mabd"),
            "delivery_date": s.get("delivery_date"),
            "on_time_result": s["retailer_on_time"],
            "on_time_root_cause": s.get("on_time_root_cause"),
            "po_units": s["units_ordered"],
            "acknowledged_units": s["units_shipped"],
            "shipped_units": s["units_received"],
            "in_full_result": s["retailer_in_full"],
            "in_full_root_cause": s.get("in_full_root_cause"),
            "otif_fine": 0.0,
            "retailer_penalty_flag": not s["retailer_otif"],
        })

    return rows


def build_portfolio_shipments(shipments: list[dict]) -> list[dict]:
    """Lightweight per-shipment data for client-side window filtering."""
    return [
        {
            "ship_date": s.get("ship_date"),
            "units_ordered": s["units_ordered"],
            "units_shipped": s["units_shipped"],
        }
        for s in shipments
    ]


def build_chargebacks_export(chargebacks: list[dict]) -> list[dict]:
    """Per-chargeback data for client-side window filtering."""
    return [
        {
            "retailer": cb.get("retailer"),
            "reason": cb["reason"],
            "amount": cb["amount"],
            "month": cb["month"],
        }
        for cb in chargebacks
    ]


def main():
    os.makedirs(DATA_OUT_DIR, exist_ok=True)

    data = _load_platform_data()
    shipments = _join_shipment_data(data)
    shipments = _compute_otif(shipments)

    retailers = sorted(set(s["retailer_id"] for s in shipments))
    print(f"Loaded {len(shipments)} shipments across {len(retailers)} retailers", flush=True)

    retailer_metrics = _retailer_metrics(shipments)

    print(f"\n{'='*72}", flush=True)
    print("PER-RETAILER OTIF BREAKDOWN", flush=True)
    print(f"{'='*72}", flush=True)
    print(f"{'Retailer':<16} {'Ships':>6} {'Brand Fill':>11} {'Ret Fill':>9} "
          f"{'On-Time':>8} {'In-Full':>8} {'OTIF':>6}", flush=True)
    print(f"{'-'*72}", flush=True)
    for rid, m in sorted(retailer_metrics.items()):
        print(f"{m['retailer_name']:<16} {m['shipment_count']:>6} "
              f"{m['brand_fill']:>10.1%} {m['retailer_fill']:>8.1%} "
              f"{m['on_time_rate']:>7.1%} {m['in_full_rate']:>7.1%} "
              f"{m['otif_rate']:>5.1%}", flush=True)

    total_ordered = sum(s["units_ordered"] for s in shipments)
    total_shipped = sum(s["units_shipped"] for s in shipments)
    total_received = sum(s["units_received"] for s in shipments)
    total_otif = sum(1 for s in shipments if s["retailer_otif"])
    portfolio_fill = total_shipped / total_ordered if total_ordered else 0
    portfolio_rfill = total_received / total_ordered if total_ordered else 0
    portfolio_otif = total_otif / len(shipments) if shipments else 0
    print(f"{'-'*72}", flush=True)
    print(f"{'Portfolio':<16} {len(shipments):>6} "
          f"{portfolio_fill:>10.1%} {portfolio_rfill:>8.1%} "
          f"{'':>8} {'':>8} {portfolio_otif:>5.1%}", flush=True)

    summary = build_summary(shipments, retailer_metrics)
    root_causes = build_root_causes(shipments, summary)
    true_fill = build_true_fill(shipments)
    exposure = build_exposure(shipments, data["chargebacks"])
    audit_rows = build_audit_rows(shipments)

    files = {
        "summary.json": summary,
        "root_causes.json": root_causes,
        "true_fill.json": true_fill,
        "exposure.json": exposure,
        "audit_rows.json": audit_rows,
        "portfolio_shipments.json": build_portfolio_shipments(shipments),
        "chargebacks.json": build_chargebacks_export(data["chargebacks"]),
    }

    print(f"\nExporting to {DATA_OUT_DIR}...", flush=True)
    for fname, fdata in files.items():
        path = os.path.join(DATA_OUT_DIR, fname)
        with open(path, "w") as f:
            json.dump(fdata, f, default=str, indent=2)
        count = len(fdata) if isinstance(fdata, list) else "object"
        print(f"  {fname}: {count}", flush=True)

    print(f"\n{'='*72}", flush=True)
    print("SUMMARY", flush=True)
    print(f"{'='*72}", flush=True)
    print(f"  Internal fill rate (portfolio): {summary['internal_fill_rate']:.1%}", flush=True)
    print(f"  Walmart OTIF (retailer-scored):  {summary['retailer_otif']:.1%}", flush=True)
    print(f"  Gap:                             {summary['gap_pts']:.1f} pts", flush=True)
    print(f"    On-time contribution:          {summary['ontime_gap_pts']:.1f} pts", flush=True)
    print(f"    In-full contribution:          {summary['infull_gap_pts']:.1f} pts", flush=True)
    print(f"  Annual OTIF fines (chargebacks): ${exposure['annual_fines']:,.0f}", flush=True)
    print(f"  Annual velocity damage (MODEL):  ${exposure['annual_velocity_damage']:,.0f}", flush=True)
    print(f"  Total exposure:                  ${exposure['total_exposure']:,.0f}", flush=True)


if __name__ == "__main__":
    main()
