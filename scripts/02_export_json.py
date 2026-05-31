"""Aggregate synthetic OTIF data and export to frontend/src/data/.

Input: cache/otif_synthetic.json
Output: frontend/src/data/{summary,root_causes,true_fill,exposure,audit_rows}.json
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

from otif_config import (
    TARGET_INTERNAL_FILL, TARGET_RETAILER_OTIF,
    TARGET_ONTIME_GAP_PTS, TARGET_INFULL_GAP_PTS,
    CACHE_DIR, DATA_OUT_DIR, WINDOW_START, WINDOW_END,
    WALMART_RETAILER_ID,
)


def _load_synthetic() -> list[dict]:
    path = os.path.join(CACHE_DIR, "otif_synthetic.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Synthetic data not found: {path}\n"
            "Run 01_synthesize_otif.py first."
        )
    with open(path) as f:
        return json.load(f)["orders"]


def build_summary(orders: list[dict]) -> dict:
    total = len(orders)
    on_time_pass = sum(1 for r in orders if r["on_time_result"])
    in_full_pass = sum(1 for r in orders if r["in_full_result"])
    otif_pass = sum(1 for r in orders if r["on_time_result"] and r["in_full_result"])

    total_po = sum(r["po_qty"] for r in orders if r["po_qty"])
    total_shipped = sum(r.get("synthetic_shipped_qty", r["po_qty"]) for r in orders)
    total_ack = sum(r.get("acknowledged_qty", r["po_qty"]) for r in orders)

    # Hardcoded to portfolio target: Cinderhaven reports 95% fill based on their
    # internal WMS measurement, which differs from the OTIF scorecard methodology.
    internal_fill = TARGET_INTERNAL_FILL
    retailer_otif = round(otif_pass / total, 4) if total else TARGET_RETAILER_OTIF
    gap_pts = round((internal_fill - retailer_otif) * 100, 2)

    on_time_rate = round(on_time_pass / total, 4)
    in_full_rate = round(in_full_pass / total, 4)
    ontime_gap_pts = round((1 - on_time_rate) / (1 - retailer_otif) * gap_pts, 2) if gap_pts else TARGET_ONTIME_GAP_PTS
    infull_gap_pts = round(gap_pts - ontime_gap_pts, 2) if gap_pts else TARGET_INFULL_GAP_PTS

    return {
        "internal_fill_rate": internal_fill,
        "retailer_otif": retailer_otif,
        "gap_pts": gap_pts,
        "ontime_gap_pts": ontime_gap_pts,
        "infull_gap_pts": infull_gap_pts,
        "total_shipments": total,
        "walmart_shipments": total,
        "window_start": WINDOW_START.isoformat(),
        "window_end": WINDOW_END.isoformat(),
    }


def build_root_causes(orders: list[dict], summary: dict) -> list[dict]:
    gap_pts = summary["gap_pts"]
    ontime_gap = summary["ontime_gap_pts"]
    infull_gap = summary["infull_gap_pts"]

    # Count failures by root cause
    cause_counts: dict[str, int] = defaultdict(int)
    for r in orders:
        if r.get("on_time_root_cause"):
            cause_counts[r["on_time_root_cause"]] += 1
        if r.get("in_full_root_cause"):
            cause_counts[r["in_full_root_cause"]] += 1

    total_ontime_fails = cause_counts.get("warehouse_late", 0) + cause_counts.get("carrier_late", 0)
    total_infull_fails = cause_counts.get("production_short_ship", 0) + cause_counts.get("order_trimming", 0)

    def _gap(cause: str, mode: str) -> float:
        total_mode_fails = total_ontime_fails if mode == "on_time" else total_infull_fails
        mode_gap = ontime_gap if mode == "on_time" else infull_gap
        if total_mode_fails == 0:
            return 0.0
        return round(cause_counts.get(cause, 0) / total_mode_fails * mode_gap, 2)

    causes = [
        {"cause": "warehouse_late",      "failure_mode": "on_time",  "label": "Warehouse late"},
        {"cause": "carrier_late",         "failure_mode": "on_time",  "label": "Carrier late"},
        {"cause": "production_short_ship","failure_mode": "in_full",  "label": "Production short-ship"},
        {"cause": "order_trimming",       "failure_mode": "in_full",  "label": "Order trimming"},
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


def build_true_fill(orders: list[dict]) -> dict:
    total_po = sum(r["po_qty"] for r in orders if r["po_qty"])
    total_ack = sum(r.get("acknowledged_qty", r["po_qty"]) for r in orders)
    total_shipped = sum(r.get("synthetic_shipped_qty", r["po_qty"]) for r in orders)

    fill_vs_855 = round(total_shipped / total_ack, 4) if total_ack else 0
    fill_vs_850 = round(total_shipped / total_po, 4) if total_po else 0

    trimmed = [r for r in orders if r.get("acknowledged_qty", r["po_qty"]) < r["po_qty"]]
    orders_with_trimming = len(trimmed)
    trimming_gap_pts = round((fill_vs_855 - fill_vs_850) * 100, 2)

    return {
        "fill_vs_855": fill_vs_855,
        "fill_vs_850": fill_vs_850,
        "trimming_gap_pts": trimming_gap_pts,
        "orders_with_trimming": orders_with_trimming,
        "pct_orders_trimmed": round(orders_with_trimming / len(orders), 4) if orders else 0,
    }


def build_exposure(orders: list[dict]) -> dict:
    from collections import defaultdict

    annual_fines = sum(r["otif_fine"] for r in orders)
    annual_velocity = sum(r["velocity_damage"] for r in orders)

    # Scale to annual if window > 12 months
    from otif_config import WINDOW_START, WINDOW_END
    window_months = (
        (WINDOW_END.year - WINDOW_START.year) * 12
        + WINDOW_END.month - WINDOW_START.month + 1
    )
    scale = 12 / window_months if window_months > 0 else 1.0

    annual_fines = round(annual_fines * scale, 2)
    annual_velocity = round(annual_velocity * scale, 2)

    # Quarterly breakdown of fines (from po_date quarters)
    by_quarter: dict[str, float] = defaultdict(float)
    for r in orders:
        if r["otif_fine"] and r.get("po_date"):
            d = r["po_date"][:10]
            year, month = int(d[:4]), int(d[5:7])
            q = (month - 1) // 3 + 1
            key = f"{year}-Q{q}"
            by_quarter[key] += r["otif_fine"]

    fines_by_quarter = [
        {"quarter": k, "fines": round(v, 2)}
        for k, v in sorted(by_quarter.items())
    ]

    # Velocity by order (top 10 for summary; full data in audit_rows)
    velocity_by_order = sorted(
        [{"order_id": r["order_id"], "velocity_damage": r["velocity_damage"]}
         for r in orders if r["velocity_damage"] > 0],
        key=lambda x: x["velocity_damage"],
        reverse=True,
    )[:10]

    return {
        "annual_fines": annual_fines,
        "annual_velocity_damage": annual_velocity,
        "total_exposure": round(annual_fines + annual_velocity, 2),
        "fines_by_quarter": fines_by_quarter,
        "velocity_by_sku": velocity_by_order,
    }


def build_audit_rows(orders: list[dict]) -> list[dict]:
    rows = []
    for r in orders:
        rows.append({
            "shipment_id": r.get("shipment_id") or r["order_id"],
            "po_number": r["po_number"],
            "ship_date": r.get("ship_date"),
            "mabd": r.get("mabd"),
            "delivery_date": r.get("delivery_date"),
            "on_time_result": r["on_time_result"],
            "on_time_root_cause": r.get("on_time_root_cause"),
            "po_units": r["po_qty"],
            "acknowledged_units": r.get("acknowledged_qty", r["po_qty"]),
            "shipped_units": r.get("synthetic_shipped_qty", r["po_qty"]),
            "in_full_result": r["in_full_result"],
            "in_full_root_cause": r.get("in_full_root_cause"),
            "otif_fine": r["otif_fine"],
            "retailer_penalty_flag": r["otif_fine"] > 0,
        })
    return rows


def main():
    os.makedirs(DATA_OUT_DIR, exist_ok=True)
    orders = _load_synthetic()
    print(f"Exporting {len(orders)} orders to {DATA_OUT_DIR}...", flush=True)

    summary = build_summary(orders)
    root_causes = build_root_causes(orders, summary)
    true_fill = build_true_fill(orders)
    exposure = build_exposure(orders)
    audit_rows = build_audit_rows(orders)

    files = {
        "summary.json": summary,
        "root_causes.json": root_causes,
        "true_fill.json": true_fill,
        "exposure.json": exposure,
        "audit_rows.json": audit_rows,
    }

    for fname, data in files.items():
        path = os.path.join(DATA_OUT_DIR, fname)
        with open(path, "w") as f:
            json.dump(data, f, default=str, indent=2)
        count = len(data) if isinstance(data, list) else "object"
        print(f"  {fname}: {count}")

    print(f"\nSummary:")
    print(f"  Internal fill rate: {summary['internal_fill_rate']:.1%}")
    print(f"  Retailer OTIF:      {summary['retailer_otif']:.1%}")
    print(f"  Gap:                {summary['gap_pts']:.1f} pts")
    print(f"  Annual fines:       ${exposure['annual_fines']:,.0f}")
    print(f"  Velocity damage:    ${exposure['annual_velocity_damage']:,.0f}")
    print(f"  Total exposure:     ${exposure['total_exposure']:,.0f}")


if __name__ == "__main__":
    main()
