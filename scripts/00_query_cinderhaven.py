"""Query Cinderhaven platform for Walmart order/shipment data.

Requires: flyctl proxy 5432 -a cinderhaven-db (or DATABASE_URL env var)
Output: scripts/cache/cinderhaven_snapshot.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras
import psycopg2.extensions
from dotenv import load_dotenv

from otif_config import WALMART_RETAILER_ID, CACHE_DIR, PROJECT_ROOT, DATABASE_URL

DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    "DEC2FLOAT",
    lambda value, curs: float(value) if value is not None else None,
)
psycopg2.extensions.register_type(DEC2FLOAT)


def _load_env():
    env_path = Path(PROJECT_ROOT) / ".env"
    if not env_path.exists():
        env_path = Path(PROJECT_ROOT).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def get_conn():
    _load_env()
    url = os.environ.get("DATABASE_URL", DATABASE_URL)
    conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.cursor().execute(
        "SET search_path TO public_intermediate, public_staging, public_marts, raw, public"
    )
    conn.commit()
    return conn


def query_walmart_orders(conn) -> list[dict]:
    """Fetch all Walmart orders with shipment and COGS data."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            o.order_id,
            o.retailer_id,
            o.po_number,
            o.po_date::text                    AS po_date,
            o.requested_ship_date::text        AS requested_ship_date,
            o.total_units                      AS po_qty,
            o.total_value,

            s.shipment_id,
            s.ship_date::text                  AS ship_date,
            s.delivery_date::text              AS delivery_date,
            s.carrier,
            s.units_shipped,
            s.asn_sent,
            s.asn_sent_late,

            COALESCE(cogs.total_cogs, 0.0)     AS total_cogs,
            COALESCE(cogs.total_po_units, o.total_units) AS total_po_units

        FROM fct_retailer_orders o
        LEFT JOIN fct_retailer_shipments s ON o.order_id = s.order_id
        LEFT JOIN (
            SELECT
                ol.order_id,
                SUM(ol.units_ordered * sc.cogs_per_unit) AS total_cogs,
                SUM(ol.units_ordered)                    AS total_po_units
            FROM retailer_order_lines ol
            JOIN sku_costs sc ON ol.sku = sc.sku
            GROUP BY ol.order_id
        ) cogs ON o.order_id = cogs.order_id

        WHERE o.retailer_id = %s
        ORDER BY o.po_date, o.order_id
        """,
        (WALMART_RETAILER_ID,),
    )
    rows = cur.fetchall()
    return [dict(row) for row in rows]


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    print(f"Connecting to Cinderhaven DB...", flush=True)
    conn = get_conn()

    print(f"Querying Walmart orders...", flush=True)
    orders = query_walmart_orders(conn)
    conn.close()

    print(f"  {len(orders)} Walmart orders found")

    out_path = os.path.join(CACHE_DIR, "cinderhaven_snapshot.json")
    with open(out_path, "w") as f:
        json.dump({"orders": orders}, f, default=str, indent=2)

    print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
