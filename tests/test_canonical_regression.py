"""Cinderhaven canonical data regression tests for otif-blind-spot.

Verifies the baked JSON data artifacts are structurally valid and
internally consistent against the Cinderhaven causal fulfillment model.

Source data:
    - Platform causal fulfillment (Groups B-E): shipment_lines,
      receipt_lines, chargebacks
    - Fill rates derived from data, not target-locked

SCOPE NOTE: Summary uses portfolio fill rate (all retailers) for the
internal metric, and Walmart-scored OTIF for the retailer metric. The
audit sheet and root-cause decomposition are Walmart-specific.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "data"


def _load(name: str):
    path = DATA_DIR / name
    if not path.exists():
        pytest.skip(f"{name} not yet generated -- run python scripts/run_pipeline.py")
    return json.loads(path.read_text())


class TestCinderhavenCanonicalRegression:
    """Guard-rails for the Cinderhaven OTIF dataset."""

    # --- Scope ---

    def test_total_shipments_exceeds_walmart(self):
        """Pipeline now covers all retailers; total > walmart."""
        s = _load("summary.json")
        assert s["total_shipments"] >= s["walmart_shipments"], (
            "total_shipments should be >= walmart_shipments"
        )

    def test_walmart_shipments_nontrivial(self):
        s = _load("summary.json")
        assert s["walmart_shipments"] > 1000, (
            f"Only {s['walmart_shipments']} Walmart shipments -- expected >1000"
        )

    # --- OTIF gap structure ---

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

    # --- Root causes ---

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

    # --- Data file existence ---

    def test_all_data_files_exist(self):
        for name in ("summary.json", "root_causes.json", "true_fill.json",
                      "exposure.json", "audit_rows.json"):
            assert (DATA_DIR / name).exists(), f"Missing: {name}"

    # --- Exposure financial sanity ---

    def test_exposure_positive(self):
        """Total annual exposure should be positive."""
        e = _load("exposure.json")
        assert e["total_exposure"] > 0, "Total exposure should be positive"

    def test_fines_from_chargebacks(self):
        """Annual fines should be positive (platform has causal chargebacks)."""
        e = _load("exposure.json")
        assert e["annual_fines"] > 0, "Annual fines from chargebacks should be positive"
