"""Synthesize OTIF scorecard data from Cinderhaven snapshot.

Pure function layer — reads cache/cinderhaven_snapshot.json, no DB calls.
Output: cache/otif_synthetic.json

Synthesized fields added per order:
  - mabd, on_time_result, on_time_root_cause
  - acknowledged_qty, shipped_qty, in_full_result, in_full_root_cause
  - cogs, otif_fine, velocity_damage
"""
from __future__ import annotations

import json
import os
import random
from datetime import date, timedelta

from otif_config import (
    RNG_SEED, MABD_WINDOW_DAYS, OTIF_FINE_RATE, VELOCITY_DAMAGE_PER_UNIT_GAP,
    ON_TIME_FAIL_RATE, IN_FULL_FAIL_RATE,
    ORDER_TRIM_RATE, ACK_RATE_MIN, ACK_RATE_MAX,
    SHORT_SHIP_RATE, SHORT_SHIP_MIN, SHORT_SHIP_MAX,
    CACHE_DIR,
)


def _date_or_none(s: str | None) -> date | None:
    if s is None:
        return None
    try:
        return date.fromisoformat(s[:10])
    except (ValueError, TypeError):
        return None


def synthesize(orders: list[dict], rng: random.Random) -> list[dict]:
    result = []

    for order in orders:
        row = dict(order)

        po_qty = int(order["po_qty"] or 0)
        total_cogs = float(order["total_cogs"] or 0.0)
        requested_ship_date = _date_or_none(order["requested_ship_date"])
        asn_sent_late = bool(order.get("asn_sent_late") or False)

        # --- MABD (for display; defines Walmart's receiving window) ---
        if requested_ship_date:
            mabd = requested_ship_date + timedelta(days=MABD_WINDOW_DAYS)
            row["mabd"] = mabd.isoformat()
        else:
            row["mabd"] = None

        # --- On-time result (probability-based to hit target ~7.8% fail) ---
        on_time_fail = rng.random() < ON_TIME_FAIL_RATE
        row["on_time_result"] = not on_time_fail
        if on_time_fail:
            row["on_time_root_cause"] = "warehouse_late" if asn_sent_late else "carrier_late"
        else:
            row["on_time_root_cause"] = None

        # --- Acknowledged qty (order trimming) ---
        is_trimmed = rng.random() < ORDER_TRIM_RATE
        if is_trimmed and po_qty > 0:
            ack_rate = rng.uniform(ACK_RATE_MIN, ACK_RATE_MAX)
            acknowledged_qty = max(1, round(po_qty * ack_rate))
        else:
            acknowledged_qty = po_qty
        row["acknowledged_qty"] = acknowledged_qty

        # --- Shipped qty (production short-ship synthesis) ---
        is_short_ship = rng.random() < SHORT_SHIP_RATE
        if is_short_ship and po_qty > 0:
            ship_ratio = rng.uniform(SHORT_SHIP_MIN, SHORT_SHIP_MAX)
            synthetic_shipped = max(1, round(po_qty * ship_ratio))
        else:
            synthetic_shipped = po_qty
        row["synthetic_shipped_qty"] = synthetic_shipped

        # --- In-full result ---
        in_full_result = synthetic_shipped >= acknowledged_qty
        row["in_full_result"] = in_full_result
        if not in_full_result:
            row["in_full_root_cause"] = "order_trimming" if is_trimmed else "production_short_ship"
        else:
            row["in_full_root_cause"] = None

        # --- COGS and OTIF fine ---
        row["cogs"] = round(total_cogs, 2)
        if total_cogs > 0 and (not row["on_time_result"] or not in_full_result):
            row["otif_fine"] = round(total_cogs * OTIF_FINE_RATE, 2)
        else:
            row["otif_fine"] = 0.0

        # --- Velocity damage (in-full failures only) ---
        missed_units = max(0, po_qty - synthetic_shipped)
        row["velocity_damage"] = round(missed_units * VELOCITY_DAMAGE_PER_UNIT_GAP, 2)

        result.append(row)

    return result


def main():
    snapshot_path = os.path.join(CACHE_DIR, "cinderhaven_snapshot.json")
    if not os.path.exists(snapshot_path):
        raise FileNotFoundError(
            f"Snapshot not found: {snapshot_path}\n"
            "Run 00_query_cinderhaven.py first."
        )

    with open(snapshot_path) as f:
        snapshot = json.load(f)

    orders = snapshot["orders"]
    print(f"Synthesizing OTIF data for {len(orders)} orders (seed={RNG_SEED})...", flush=True)

    rng = random.Random(RNG_SEED)
    synthetic = synthesize(orders, rng)

    # Diagnostics
    total = len(synthetic)
    on_time_fails = sum(1 for r in synthetic if not r["on_time_result"])
    in_full_fails = sum(1 for r in synthetic if not r["in_full_result"])
    otif_passes = sum(1 for r in synthetic if r["on_time_result"] and r["in_full_result"])
    total_po = sum(r["po_qty"] for r in synthetic if r["po_qty"])
    total_shipped = sum(r["synthetic_shipped_qty"] for r in synthetic if r.get("synthetic_shipped_qty"))
    total_ack = sum(r["acknowledged_qty"] for r in synthetic if r.get("acknowledged_qty"))

    print(f"  On-time fail rate:   {on_time_fails/total:.1%} (target ~7.8%)")
    print(f"  In-full fail rate:   {in_full_fails/total:.1%} (target ~6.5%)")
    print(f"  OTIF pass rate:      {otif_passes/total:.1%} (target ~86%)")
    print(f"  Internal fill (855): {total_shipped/total_ack:.1%} (target ~95%)")
    print(f"  True fill (850):     {total_shipped/total_po:.1%}")
    print(f"  Total OTIF fines:    ${sum(r['otif_fine'] for r in synthetic):,.0f} (target ~$140K)")
    print(f"  Total velocity dmg:  ${sum(r['velocity_damage'] for r in synthetic):,.0f} (target ~$320K)")

    out_path = os.path.join(CACHE_DIR, "otif_synthetic.json")
    with open(out_path, "w") as f:
        json.dump({"orders": synthetic}, f, default=str, indent=2)

    print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
