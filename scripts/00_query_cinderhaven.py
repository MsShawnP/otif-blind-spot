"""Query Cinderhaven platform for causal fulfillment data.

Requires: flyctl proxy 5432 -a cinderhaven-db (or DATABASE_URL env var)
Output: scripts/cache/platform_fulfillment.json

Pulls from the causal fulfillment model (Groups B-E):
  - Retailer shipments with timing (all retailers)
  - Shipment-line aggregates (fill data, shortfall reasons)
  - Receipt-line aggregates (receiving data, discrepancy reasons)
  - OTIF-relevant chargebacks (short_ship, late_delivery, receiving_discrepancy)
"""
from __future__ import annotations

import json
import os

import psycopg2
import psycopg2.extras
import psycopg2.extensions

from otif_config import CACHE_DIR, DATABASE_URL, WINDOW_START, WINDOW_END

DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    "DEC2FLOAT",
    lambda value, curs: float(value) if value is not None else None,
)
psycopg2.extensions.register_type(DEC2FLOAT)


def get_conn():
    # .env is loaded and DATABASE_URL resolved once at otif_config import time.
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.cursor().execute(
        "SET search_path TO public_intermediate, public_staging, public_marts, raw, public"
    )
    conn.commit()
    return conn


def query_shipments(conn) -> list[dict]:
    """Per-shipment data with order context and timing (all retailers)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT
            s.shipment_id,
            s.order_id,
            s.retailer_id,
            o.po_number,
            o.po_date::text              AS po_date,
            s.requested_ship_date::text  AS requested_ship_date,
            s.ship_date::text            AS ship_date,
            s.delivery_date::text        AS delivery_date,
            s.carrier,
            s.is_on_time,
            s.days_late,
            o.total_units                AS po_units,
            o.total_value
        FROM fct_retailer_shipments s
        JOIN fct_retailer_orders o ON s.order_id = o.order_id
        ORDER BY o.po_date, s.shipment_id
    """)
    return [dict(row) for row in cur.fetchall()]


def query_shipment_line_aggs(conn) -> list[dict]:
    """Per-shipment aggregates from shipment lines (fill data)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT
            shipment_id,
            retailer_id,
            SUM(units_ordered)  AS units_ordered,
            SUM(units_shipped)  AS units_shipped,
            SUM(units_short)    AS units_short,
            COUNT(*) FILTER (WHERE is_short) AS short_line_count,
            COUNT(*)            AS total_line_count,
            array_agg(DISTINCT shortfall_reason)
                FILTER (WHERE shortfall_reason IS NOT NULL) AS shortfall_reasons
        FROM fct_retailer_shipment_lines
        GROUP BY shipment_id, retailer_id
    """)
    return [dict(row) for row in cur.fetchall()]


def query_receipt_line_aggs(conn) -> list[dict]:
    """Per-shipment aggregates from receipt lines (retailer receiving data)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT
            shipment_id,
            SUM(units_ordered)    AS receipt_units_ordered,
            SUM(units_received)   AS units_received,
            SUM(units_discrepant) AS units_discrepant,
            COUNT(*) FILTER (WHERE has_discrepancy) AS discrepant_line_count,
            array_agg(DISTINCT discrepancy_reason)
                FILTER (WHERE discrepancy_reason IS NOT NULL) AS discrepancy_reasons
        FROM fct_retailer_receipt_lines
        GROUP BY shipment_id
    """)
    return [dict(row) for row in cur.fetchall()]


def query_chargebacks(conn) -> list[dict]:
    """OTIF-relevant chargebacks (real causal fines from the platform)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT
            chargeback_id,
            retailer,
            reason,
            amount,
            month
        FROM fct_chargebacks
        WHERE reason IN ('short_ship', 'late_delivery', 'receiving_discrepancy')
          AND month >= to_char(%s::date, 'YYYY-MM')
          AND month <= to_char(%s::date, 'YYYY-MM')
        ORDER BY month
    """, (WINDOW_START, WINDOW_END))
    return [dict(row) for row in cur.fetchall()]


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    print("Connecting to Cinderhaven DB...", flush=True)
    conn = get_conn()

    print("Querying shipments...", flush=True)
    shipments = query_shipments(conn)
    print(f"  {len(shipments)} shipments")

    print("Querying shipment line aggregates...", flush=True)
    ship_lines = query_shipment_line_aggs(conn)
    print(f"  {len(ship_lines)} shipment-line groups")

    print("Querying receipt line aggregates...", flush=True)
    receipt_lines = query_receipt_line_aggs(conn)
    print(f"  {len(receipt_lines)} receipt-line groups")

    print("Querying OTIF chargebacks...", flush=True)
    chargebacks = query_chargebacks(conn)
    print(f"  {len(chargebacks)} OTIF-relevant chargebacks")

    conn.close()

    out_path = os.path.join(CACHE_DIR, "platform_fulfillment.json")
    with open(out_path, "w") as f:
        json.dump({
            "shipments": shipments,
            "shipment_line_aggs": ship_lines,
            "receipt_line_aggs": receipt_lines,
            "chargebacks": chargebacks,
        }, f, default=str, indent=2)

    print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
