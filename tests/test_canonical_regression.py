"""Cinderhaven canonical data regression tests for otif-blind-spot.

Verifies the baked JSON data artifacts match the Cinderhaven data contract
for the subset this tool covers.

Canonical contract (target):
    - 50 SKUs, 5 product lines, 6 retailers
    - Retailers: Walmart, Costco, Whole Foods, Sprouts, Kroger, Regional Group

SCOPE NOTE: This tool is intentionally Walmart-only.  It analyzes OTIF
(On-Time In-Full) performance for Cinderhaven's Walmart channel.  The
single-retailer focus is by design -- Walmart is the only retailer with
OTIF fine exposure in the portfolio.  Other retailers are out of scope.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "data"


def _load(name: str):
    path = DATA_DIR / name
    if not path.exists():
        pytest.skip(f"{name} not yet generated -- run python scripts/run_pipeline.py")
    return json.loads(path.read_text())


class TestCinderhavenCanonicalRegression:
    """Guard-rails for the baked Cinderhaven OTIF dataset (Walmart-only)."""

    # ------------------------------------------------------------------
    # Scope: Walmart only
    # ------------------------------------------------------------------

    def test_walmart_only_scope(self):
        """This tool covers Walmart OTIF only -- total_shipments == walmart_shipments."""
        s = _load("summary.json")
        assert s["total_shipments"] == s["walmart_shipments"], (
            "total_shipments should equal walmart_shipments (Walmart-only scope)"
        )

    def test_scope_note_walmart_shipments_positive(self):
        """Walmart shipment count should be non-trivial."""
        s = _load("summary.json")
        assert s["walmart_shipments"] > 5000, (
            f"Only {s['walmart_shipments']} Walmart shipments -- expected >5000"
        )

    # ------------------------------------------------------------------
    # OTIF gap structure
    # ------------------------------------------------------------------

    def test_otif_gap_decomposition(self):
        """gap_pts should approximately equal ontime_gap_pts + infull_gap_pts."""
        s = _load("summary.json")
        implied = s["ontime_gap_pts"] + s["infull_gap_pts"]
        assert abs(s["gap_pts"] - implied) < 0.5, (
            f"gap_pts={s['gap_pts']} != ontime({s['ontime_gap_pts']}) + "
            f"infull({s['infull_gap_pts']}) = {implied}"
        )

    def test_internal_fill_rate_above_retailer_otif(self):
        """Internal fill rate should be higher than retailer OTIF (the blind spot)."""
        s = _load("summary.json")
        assert s["internal_fill_rate"] > s["retailer_otif"], (
            f"Internal fill {s['internal_fill_rate']} should exceed "
            f"retailer OTIF {s['retailer_otif']}"
        )

    # ------------------------------------------------------------------
    # Root causes
    # ------------------------------------------------------------------

    def test_root_causes_count(self):
        """4 root causes in the decomposition."""
        rc = _load("root_causes.json")
        assert len(rc) == 4, f"Expected 4 root causes, got {len(rc)}"

    def test_root_causes_cover_both_failure_modes(self):
        """Root causes must include both on_time and in_full failure modes."""
        rc = _load("root_causes.json")
        modes = {r["failure_mode"] for r in rc}
        assert "on_time" in modes, "Missing on_time failure mode"
        assert "in_full" in modes, "Missing in_full failure mode"

    # ------------------------------------------------------------------
    # Data file existence
    # ------------------------------------------------------------------

    def test_all_data_files_exist(self):
        for name in ("summary.json", "root_causes.json", "true_fill.json",
                      "exposure.json", "audit_rows.json"):
            assert (DATA_DIR / name).exists(), f"Missing: {name}"

    # ------------------------------------------------------------------
    # Exposure financial sanity
    # ------------------------------------------------------------------

    def test_total_exposure_range(self):
        """Total annual exposure should be in a plausible range ($300K-$600K)."""
        e = _load("exposure.json")
        total = e["total_exposure"]
        assert 300_000 < total < 600_000, (
            f"Total exposure ${total:,.0f} outside $300K-$600K range"
        )
