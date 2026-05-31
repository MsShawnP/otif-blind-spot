"""Shared constants for the OTIF Blind Spot data generation pipeline."""
from __future__ import annotations

import os
from datetime import date

# Data window
WINDOW_START = date(2024, 1, 1)
WINDOW_END = date(2026, 3, 31)

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
ON_TIME_FAIL_RATE = 0.078       # ~8% of orders are late → ~5-pt on-time contribution
IN_FULL_FAIL_RATE = 0.065       # ~6.5% of orders fail in-full → ~4-pt in-full contribution

ORDER_TRIM_RATE = 0.35          # 35% of orders have acknowledged_qty < po_qty
ACK_RATE_MIN = 0.80
ACK_RATE_MAX = 0.95

SHORT_SHIP_RATE = 0.055         # ~5.5% of orders are production short-ships
SHORT_SHIP_MIN = 0.70
SHORT_SHIP_MAX = 0.92

# Velocity damage: dollars per unit short (tuned to hit ~$320K target)
VELOCITY_DAMAGE_PER_UNIT_GAP = 3.50

# Paths
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
CACHE_DIR = os.path.join(SCRIPTS_DIR, "cache")
DATA_OUT_DIR = os.path.join(PROJECT_ROOT, "frontend", "src", "data")

# DB connection — mirrors Cinderhaven platform pattern
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"postgresql://postgres:{os.environ.get('POSTGRES_PASSWORD', '')}@localhost:5432/cinderhaven"
)
