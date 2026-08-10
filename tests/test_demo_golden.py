"""Demo golden lock — otif-blind-spot.

The demo is a React app that computes every figure from the seven committed JSON
files in frontend/src/data. This byte-locks those inputs and pins the canonical
full-corpus headline numbers the deployed default renders (Shawn set the default
window to the full corpus so the landing view matches canonical, not the 52-week
subset).

If a SHA or a headline number moves, STOP: a golden moved.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "frontend" / "src" / "data"

GOLDEN_SHA256 = {
    "audit_rows.json": "dfc10dfa4c0bd8e0",
    "chargebacks.json": "2bf6e69481532a33",
    "exposure.json": "6b3969521695f213",
    "portfolio_shipments.json": "6d5812dc1744f97d",
    "root_causes.json": "6edd9c75b081a2f7",
    "summary.json": "ee32563f0d249972",
    "true_fill.json": "ba8fc3320ec67841",
}


@pytest.mark.parametrize("name", sorted(GOLDEN_SHA256))
def test_demo_data_sha256_prefix(name):
    digest = hashlib.sha256((DATA / name).read_bytes()).hexdigest()[:16]
    assert digest == GOLDEN_SHA256[name], (
        f"{name} changed (sha256[:16] {digest} != golden {GOLDEN_SHA256[name]}) "
        "— a demo golden moved; STOP and report."
    )


def test_canonical_headline_gap():
    s = json.loads((DATA / "summary.json").read_text())
    # The core story: internal 99% (fill at the shipping dock) vs Walmart 84%
    # (OTIF at their dock), a 14.8-point gap computed from the raw rates.
    assert s["internal_fill_rate"] == 0.9923
    assert s["retailer_otif"] == 0.8445
    assert s["gap_pts"] == 14.78
    # gap foots to the raw rates (the audit's rounding concern: the 99/84 hero is
    # a round-number hook; the gap is the precise figure).
    assert round((s["internal_fill_rate"] - s["retailer_otif"]) * 100, 2) == s["gap_pts"]


def test_canonical_exposure():
    e = json.loads((DATA / "exposure.json").read_text())
    # Canonical full-corpus exposure $57,197 = fines + modeled velocity damage.
    assert e["total_exposure"] == 57196.45
    assert e["annual_fines"] == 23696.78
    assert e["annual_velocity_damage"] == 33499.67
    assert round(e["annual_fines"] + e["annual_velocity_damage"], 2) == e["total_exposure"]
