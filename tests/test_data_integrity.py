"""Validate exported JSON files against the brief's target figures.

Run after the pipeline:
  python -m pytest tests/test_data_integrity.py -v

Requires frontend/src/data/*.json to exist (run python scripts/run_pipeline.py first).
"""
from __future__ import annotations

import json
import os
import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data")


def _load(name: str) -> dict | list:
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        pytest.skip(f"{name} not yet generated — run python scripts/run_pipeline.py")
    with open(path) as f:
        return json.load(f)


# ─── summary.json ────────────────────────────────────────────────────────────

def test_internal_fill_rate():
    s = _load("summary.json")
    assert abs(s["internal_fill_rate"] - 0.95) <= 0.005, (
        f"internal_fill_rate={s['internal_fill_rate']:.3f}, expected ~0.95"
    )


def test_retailer_otif():
    s = _load("summary.json")
    assert abs(s["retailer_otif"] - 0.86) <= 0.005, (
        f"retailer_otif={s['retailer_otif']:.3f}, expected ~0.86"
    )


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


# ─── root_causes.json ────────────────────────────────────────────────────────

def test_ontime_gap_pts():
    rc = _load("root_causes.json")
    ontime_total = sum(r["gap_pts"] for r in rc if r["failure_mode"] == "on_time")
    assert abs(ontime_total - 5.0) <= 0.5, (
        f"on-time gap_pts sum={ontime_total:.2f}, expected ~5.0"
    )


def test_infull_gap_pts():
    rc = _load("root_causes.json")
    infull_total = sum(r["gap_pts"] for r in rc if r["failure_mode"] == "in_full")
    assert abs(infull_total - 4.0) <= 0.5, (
        f"in-full gap_pts sum={infull_total:.2f}, expected ~4.0"
    )


def test_root_causes_has_four_entries():
    rc = _load("root_causes.json")
    assert len(rc) == 4, f"Expected 4 root causes, got {len(rc)}"


def test_root_cause_required_keys():
    rc = _load("root_causes.json")
    for row in rc:
        for key in ["cause", "failure_mode", "gap_pts", "shipment_count", "pct_of_gap"]:
            assert key in row, f"root_causes row missing key: {key}"


# ─── true_fill.json ──────────────────────────────────────────────────────────

def test_true_fill_855_greater_than_850():
    tf = _load("true_fill.json")
    assert tf["fill_vs_855"] > tf["fill_vs_850"], (
        f"fill_vs_855={tf['fill_vs_855']:.3f} should be > fill_vs_850={tf['fill_vs_850']:.3f} "
        "(order trimming inflates 855 fill rate)"
    )


def test_true_fill_required_keys():
    tf = _load("true_fill.json")
    for key in ["fill_vs_855", "fill_vs_850", "trimming_gap_pts", "orders_with_trimming", "pct_orders_trimmed"]:
        assert key in tf, f"true_fill.json missing key: {key}"


# ─── exposure.json ───────────────────────────────────────────────────────────

def test_annual_fines():
    e = _load("exposure.json")
    assert abs(e["annual_fines"] - 140_000) / 140_000 <= 0.15, (
        f"annual_fines=${e['annual_fines']:,.0f}, expected ~$140K (±15%)"
    )


def test_annual_velocity_damage():
    e = _load("exposure.json")
    assert abs(e["annual_velocity_damage"] - 320_000) / 320_000 <= 0.15, (
        f"annual_velocity_damage=${e['annual_velocity_damage']:,.0f}, expected ~$320K (±15%)"
    )


def test_total_exposure():
    e = _load("exposure.json")
    expected = 140_000 + 320_000
    actual = e["annual_fines"] + e["annual_velocity_damage"]
    assert abs(actual - expected) / expected <= 0.15, (
        f"total_exposure=${actual:,.0f}, expected ~$460K (±15%)"
    )


def test_exposure_required_keys():
    e = _load("exposure.json")
    for key in ["annual_fines", "annual_velocity_damage", "total_exposure", "fines_by_quarter"]:
        assert key in e, f"exposure.json missing key: {key}"


# ─── audit_rows.json ─────────────────────────────────────────────────────────

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


def test_audit_rows_penalty_flag_matches_fine():
    rows = _load("audit_rows.json")
    for r in rows:
        if r["retailer_penalty_flag"]:
            assert r["otif_fine"] > 0, "penalty_flag=True but otif_fine=0"
        else:
            assert r["otif_fine"] == 0, "penalty_flag=False but otif_fine>0"


# ─── cross-file ──────────────────────────────────────────────────────────────

def test_all_five_files_exist():
    for fname in ["summary.json", "root_causes.json", "true_fill.json", "exposure.json", "audit_rows.json"]:
        path = os.path.join(DATA_DIR, fname)
        assert os.path.exists(path), f"Missing: {fname}"


def test_audit_rows_count_matches_summary():
    rows = _load("audit_rows.json")
    s = _load("summary.json")
    assert len(rows) == s["walmart_shipments"], (
        f"audit_rows has {len(rows)} rows, summary.walmart_shipments={s['walmart_shipments']}"
    )
