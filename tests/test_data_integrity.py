"""Validate exported JSON files for structural integrity and consistency.

Run after the pipeline:
  python -m pytest tests/test_data_integrity.py -v

Requires frontend/src/data/*.json to exist (run python scripts/run_pipeline.py first).

NOTE: These tests validate structure and internal consistency, not
specific numeric targets. The pipeline computes scores from platform
causal fulfillment data -- the data produces the numbers.
"""
from __future__ import annotations

import json
import os
import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data")


def _load(name: str) -> dict | list:
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        pytest.skip(f"{name} not yet generated -- run python scripts/run_pipeline.py")
    with open(path) as f:
        return json.load(f)


# --- summary.json ---

def test_summary_required_keys():
    s = _load("summary.json")
    required = [
        "internal_fill_rate", "retailer_otif", "gap_pts",
        "ontime_gap_pts", "infull_gap_pts",
        "total_shipments", "walmart_shipments",
        "window_start", "window_end",
    ]
    for key in required:
        assert key in s, f"summary.json missing key: {key}"


def test_internal_fill_in_valid_range():
    s = _load("summary.json")
    assert 0.80 <= s["internal_fill_rate"] <= 1.0, (
        f"internal_fill_rate={s['internal_fill_rate']:.3f} outside [0.80, 1.0]"
    )


def test_retailer_otif_in_valid_range():
    s = _load("summary.json")
    assert 0.50 <= s["retailer_otif"] <= 1.0, (
        f"retailer_otif={s['retailer_otif']:.3f} outside [0.50, 1.0]"
    )


def test_internal_fill_exceeds_retailer_otif():
    s = _load("summary.json")
    assert s["internal_fill_rate"] > s["retailer_otif"], (
        f"internal_fill={s['internal_fill_rate']:.3f} should exceed "
        f"retailer_otif={s['retailer_otif']:.3f} (the blind spot)"
    )


def test_gap_decomposition_sums():
    s = _load("summary.json")
    implied = s["ontime_gap_pts"] + s["infull_gap_pts"]
    assert abs(s["gap_pts"] - implied) < 0.5, (
        f"gap_pts={s['gap_pts']} != ontime({s['ontime_gap_pts']}) + "
        f"infull({s['infull_gap_pts']}) = {implied}"
    )


def test_walmart_shipments_positive():
    s = _load("summary.json")
    assert s["walmart_shipments"] > 1000, (
        f"Only {s['walmart_shipments']} Walmart shipments -- expected >1000"
    )


# --- root_causes.json ---

def test_root_causes_has_four_entries():
    rc = _load("root_causes.json")
    assert len(rc) == 4, f"Expected 4 root causes, got {len(rc)}"


def test_root_causes_cover_both_failure_modes():
    rc = _load("root_causes.json")
    modes = {r["failure_mode"] for r in rc}
    assert "on_time" in modes, "Missing on_time failure mode"
    assert "in_full" in modes, "Missing in_full failure mode"


def test_root_cause_required_keys():
    rc = _load("root_causes.json")
    for row in rc:
        for key in ["cause", "failure_mode", "gap_pts", "shipment_count", "pct_of_gap"]:
            assert key in row, f"root_causes row missing key: {key}"


def test_root_cause_gap_pts_sum_to_total():
    s = _load("summary.json")
    rc = _load("root_causes.json")
    rc_total = sum(r["gap_pts"] for r in rc)
    assert abs(rc_total - s["gap_pts"]) < 0.5, (
        f"Root cause gap_pts sum={rc_total:.2f} should approximate "
        f"summary gap_pts={s['gap_pts']:.2f}"
    )


# --- true_fill.json ---

def test_true_fill_brand_exceeds_retailer():
    tf = _load("true_fill.json")
    assert tf["fill_vs_855"] >= tf["fill_vs_850"], (
        f"Brand fill ({tf['fill_vs_855']:.3f}) should be >= "
        f"retailer fill ({tf['fill_vs_850']:.3f})"
    )


def test_true_fill_required_keys():
    tf = _load("true_fill.json")
    for key in ["fill_vs_855", "fill_vs_850", "trimming_gap_pts",
                "orders_with_trimming", "pct_orders_trimmed"]:
        assert key in tf, f"true_fill.json missing key: {key}"


# --- exposure.json ---

def test_exposure_required_keys():
    e = _load("exposure.json")
    for key in ["annual_fines", "annual_velocity_damage", "total_exposure", "fines_by_quarter"]:
        assert key in e, f"exposure.json missing key: {key}"


def test_exposure_total_equals_components():
    e = _load("exposure.json")
    expected = e["annual_fines"] + e["annual_velocity_damage"]
    assert abs(e["total_exposure"] - expected) < 1.0, (
        f"total_exposure={e['total_exposure']} != fines({e['annual_fines']}) + "
        f"velocity({e['annual_velocity_damage']}) = {expected}"
    )


def test_exposure_fines_positive():
    e = _load("exposure.json")
    assert e["annual_fines"] > 0, "Annual fines should be positive (chargebacks exist)"


def test_exposure_velocity_positive():
    e = _load("exposure.json")
    assert e["annual_velocity_damage"] > 0, "Velocity damage should be positive (modeled from shortfalls)"


# --- audit_rows.json ---

def test_audit_rows_no_null_shipment_id():
    rows = _load("audit_rows.json")
    null_ids = [r for r in rows if not r.get("shipment_id")]
    assert len(null_ids) == 0, f"{len(null_ids)} rows have null shipment_id"


def test_audit_rows_required_keys():
    rows = _load("audit_rows.json")
    assert len(rows) > 0, "audit_rows.json is empty"
    required = [
        "shipment_id", "po_number", "ship_date", "mabd", "delivery_date",
        "on_time_result", "on_time_root_cause", "po_units", "acknowledged_units",
        "shipped_units", "in_full_result", "in_full_root_cause",
        "otif_fine", "retailer_penalty_flag",
    ]
    sample = rows[0]
    for key in required:
        assert key in sample, f"audit_rows row missing key: {key}"


def test_audit_rows_count_matches_summary():
    rows = _load("audit_rows.json")
    s = _load("summary.json")
    assert len(rows) == s["walmart_shipments"], (
        f"audit_rows has {len(rows)} rows, summary.walmart_shipments={s['walmart_shipments']}"
    )


# --- cross-file ---

def test_all_five_files_exist():
    for fname in ["summary.json", "root_causes.json", "true_fill.json",
                  "exposure.json", "audit_rows.json"]:
        path = os.path.join(DATA_DIR, fname)
        assert os.path.exists(path), f"Missing: {fname}"
