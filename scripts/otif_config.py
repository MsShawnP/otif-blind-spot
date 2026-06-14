"""Shared constants for the OTIF Blind Spot data pipeline.

All OTIF scores and fill rates are computed from platform causal
fulfillment data. No target-locking or normalization.
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

# Load .env before resolving DB connection
def _bootstrap_env():
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    here = Path(__file__).resolve().parent
    for candidate in [here.parent / ".env", here.parent.parent / ".env"]:
        if candidate.exists():
            load_dotenv(candidate)
            return

_bootstrap_env()

# Data window
WINDOW_START = date(2023, 1, 1)
WINDOW_END = date(2025, 12, 31)

# Retailer MABD offset = max(transit_range) + otif_window_days
# Source: cinderhaven-data-platform seed_config.py RETAILER_TRANSIT_DAYS
# and RETAILER_OTIF_WINDOW_DAYS. These are retailer compliance policies,
# not synthesis parameters.
RETAILER_MABD_DAYS = {
    "RET-WALMART": 3,     # max_transit=3 + otif_window=0
    "RET-KROGER": 4,      # 3 + 1
    "RET-COSTCO": 6,      # 4 + 2
    "RET-WHOLEFOODS": 6,  # 5 + 1
    "RET-SPROUTS": 5,     # 4 + 1
    "RET-REGIONAL": 8,    # 6 + 2
}

RETAILER_NAMES = {
    "RET-WALMART": "Walmart",
    "RET-KROGER": "Kroger",
    "RET-COSTCO": "Costco",
    "RET-WHOLEFOODS": "Whole Foods",
    "RET-SPROUTS": "Sprouts",
    "RET-REGIONAL": "Regional Group",
}

RETAILER_NAME_TO_ID = {v: k for k, v in RETAILER_NAMES.items()}

# Velocity damage: MODELED soft cost per unit of retailer shortfall.
# Estimates shelf-velocity damage from empty shelves (lost sales velocity
# when product isn't available). NOT a platform-computed value.
VELOCITY_DAMAGE_PER_UNIT = 3.50

# Overlap note: chargebacks with reason='short_ship' are counted here as
# OTIF fines AND in the short-ship-cost project as short-ship chargebacks.
# Canonical scoping must ensure these are not double-counted across projects.

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
    _database_url = f"postgresql://postgres:REDACTED@localhost:5432/cinderhaven"
DATABASE_URL = _database_url
