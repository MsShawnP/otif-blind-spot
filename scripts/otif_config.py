"""Shared constants for the OTIF Blind Spot data generation pipeline."""
from __future__ import annotations

import os
from datetime import date

# Data window
WINDOW_START = date(2023, 1, 1)
WINDOW_END = date(2025, 3, 31)

# Retailer
WALMART_RETAILER_ID = "RET-WALMART"

# RNG — matches Cinderhaven platform convention
RNG_SEED = 100

# OTIF mechanics
MABD_WINDOW_DAYS = 2        # MABD = requested_ship_date + 2 days (for display)
OTIF_FINE_RATE = 0.03       # 3% of COGS on penalized shipments

# Portfolio targets
TARGET_INTERNAL_FILL = 0.95
TARGET_RETAILER_OTIF = 0.86
TARGET_ONTIME_GAP_PTS = 5.0
TARGET_INFULL_GAP_PTS = 4.0

# Synthesis parameters — tune if test_data_integrity fails
ON_TIME_FAIL_RATE = 0.079       # ~7.9% of orders are late → ~5-pt on-time contribution
WAREHOUSE_LATE_FRACTION = 0.40  # 40% of on-time failures are warehouse_late

ORDER_TRIM_RATE = 0.35          # 35% of orders have acknowledged_qty < po_qty
ACK_RATE_MIN = 0.80
ACK_RATE_MAX = 0.95

SHORT_SHIP_RATE = 0.063         # ~6.3% of orders short-ship → ~4-pt in-full contribution
SHORT_SHIP_MIN = 0.70
SHORT_SHIP_MAX = 0.92

# COGS multiplier — scales Cinderhaven seed COGS to match brief's $3M-$20M brand magnitude
COGS_MULTIPLIER = 14.0

# Velocity damage: dollars per unit short vs acknowledged (tuned to hit ~$320K annual target)
VELOCITY_DAMAGE_PER_UNIT_GAP = 20.0

# Paths
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
CACHE_DIR = os.path.join(SCRIPTS_DIR, "cache")
DATA_OUT_DIR = os.path.join(PROJECT_ROOT, "frontend", "src", "data")

# DB connection — mirrors Cinderhaven platform pattern
_database_url = os.environ.get("DATABASE_URL")
if not _database_url:
    _pg_password = os.environ.get("POSTGRES_PASSWORD")
    if not _pg_password:
        raise EnvironmentError(
            "Set DATABASE_URL or POSTGRES_PASSWORD in .env before running the pipeline."
        )
    _database_url = f"postgresql://postgres:{_pg_password}@localhost:5432/cinderhaven"
DATABASE_URL = _database_url
