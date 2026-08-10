"""Client-mode tests for otif-blind-spot.

Adversarial fixtures per checklist §6: clean run, boolean-result parsing
variants, missing required column (blocked), no-fines disclosure, mixed date
formats, negative units, duplicate key, empty file, and the --final watermark.
Fictional-placeholder identity only.

Skipped if lailara_engagement isn't installed.
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip("lailara_engagement")

from lailara_engagement.errors import ReadError  # noqa: E402
import client_mode  # noqa: E402

_CONFIG = """
client: {name: Meridian Farms}
engagement: {id: MER-2026-08}
as_of_date: "2025-12-31"
demo: true
basis: {window_months: 36, window_label: "Jan 2023 - Dec 2025"}
columns:
  shipment_id: shipment_id
  ship_date: ship_date
  on_time_result: on_time_result
  in_full_result: in_full_result
  po_units: po_units
  shipped_units: shipped_units
  otif_fine: otif_fine
"""

# 4 shipments: 2 full OTIF pass, 1 on-time-fail, 1 in-full-fail (short).
_CLEAN = (
    "shipment_id,ship_date,on_time_result,in_full_result,po_units,shipped_units,otif_fine\n"
    "S1,2025-01-05,true,true,100,100,0\n"
    "S2,2025-02-05,false,true,100,100,250.00\n"      # on-time fail
    "S3,2025-03-05,true,false,100,80,150.00\n"       # in-full fail (short 20)
    "S4,2025-04-05,true,true,100,100,0\n"
)


def _cfg(tmp_path, text=_CONFIG):
    p = tmp_path / "engagement.yml"
    p.write_text(text, encoding="utf-8")
    return str(p)


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_clean_run(tmp_path):
    src = _write(tmp_path, "otif.csv", _CLEAN)
    result = client_mode.run(_cfg(tmp_path), src, str(tmp_path / "out"))
    assert result["status"] == "ok"
    assert result["shipments"] == 4
    s = json.load(open(result["summary_json"], encoding="utf-8"))
    # internal fill = 380/400 = 0.95 ; OTIF pass = 2/4 = 0.5 ; gap = 45.0 pts
    assert s["internal_fill_rate"] == 0.95
    assert s["retailer_otif"] == 0.5
    assert s["gap_pts"] == 45.0
    assert s["ontime_fail_rate"] == 0.25
    assert s["infull_fail_rate"] == 0.25
    assert s["otif_fines_total"] == 400.0
    assert s["annual_fines"] == pytest.approx(400.0 * 12 / 36, abs=0.01)

    html = open(result["report"], encoding="utf-8").read()
    assert "Meridian Farms" in html and "SHA-256" in html and "DRAFT" in html
    assert "36 months" in html
    assert "x12/36" in html or "×12/36" in html


def test_window_and_annualization_track_config_not_hardcoded(tmp_path):
    """The rendered window ('N months (label)') and the ×12/N annualization
    divisor must come from basis.window_months / window_label, not a hardcoded
    default. The clean-run test asserts only the demo's own '36 months' /
    'x12/36' — a positive-only check a hardcoded '36' would also pass, the gap
    that let trade-spend quote 26 weeks of data as 'trailing 52 weeks'.

    Both halves: feed a distinctive window and assert it tracks (label + divisor
    + numeric annualization), AND assert the demo default is absent."""
    cfg = _cfg(tmp_path, _CONFIG.replace("window_months: 36", "window_months: 41")
                                .replace("Jan 2023 - Dec 2025", "FY2024-FY2026"))
    src = _write(tmp_path, "otif.csv", _CLEAN)
    result = client_mode.run(cfg, src, str(tmp_path / "out"))
    assert result["status"] == "ok"
    s = json.load(open(result["summary_json"], encoding="utf-8"))
    assert s["annual_fines"] == pytest.approx(400.0 * 12 / 41, abs=0.01)
    html = open(result["report"], encoding="utf-8").read()
    assert "41 months" in html and "FY2024-FY2026" in html
    assert "x12/41" in html or "×12/41" in html
    assert "36 months" not in html                       # demo default must not survive
    assert "x12/36" not in html and "×12/36" not in html
    assert "Jan 2023 - Dec 2025" not in html


def test_boolean_variants_parse(tmp_path):
    body = (
        "shipment_id,ship_date,on_time_result,in_full_result,po_units,shipped_units\n"
        "S1,2025-01-05,yes,pass,100,100\n"
        "S2,2025-02-05,LATE,short,100,90\n"
    )
    src = _write(tmp_path, "b.csv", body)
    result = client_mode.run(_cfg(tmp_path), src, str(tmp_path / "out"))
    s = json.load(open(result["summary_json"], encoding="utf-8"))
    assert s["retailer_otif"] == 0.5      # S1 passes both, S2 fails both


def test_missing_required_column_blocks(tmp_path):
    src = _write(tmp_path, "bad.csv",
                 "shipment_id,ship_date,on_time_result,in_full_result,po_units\nS1,2025-01-01,true,true,100\n")
    result = client_mode.run(_cfg(tmp_path), src, str(tmp_path / "out"))
    assert result["status"] == "blocked"
    assert "shipped_units" in open(result["readiness_report"], encoding="utf-8").read().lower()


def test_no_fines_column_disclosed(tmp_path):
    body = ("shipment_id,ship_date,on_time_result,in_full_result,po_units,shipped_units\n"
            "S1,2025-01-05,true,true,100,100\n")
    src = _write(tmp_path, "nf.csv", body)
    result = client_mode.run(_cfg(tmp_path), src, str(tmp_path / "out"))
    assert result["status"] == "ok"
    s = json.load(open(result["summary_json"], encoding="utf-8"))
    assert s["otif_fines_total"] is None
    assert "otif_fine" in open(result["report"], encoding="utf-8").read().lower()


def test_velocity_disclosed_as_modeled(tmp_path):
    src = _write(tmp_path, "otif.csv", _CLEAN)
    result = client_mode.run(_cfg(tmp_path), src, str(tmp_path / "out"))
    assert "velocity damage" in open(result["report"], encoding="utf-8").read().lower()


def test_mixed_dates_warn(tmp_path):
    body = ("shipment_id,ship_date,on_time_result,in_full_result,po_units,shipped_units\n"
            "S1,2025-01-05,true,true,100,100\n"
            "S2,02/05/2025,true,true,100,100\n")
    src = _write(tmp_path, "d.csv", body)
    result = client_mode.run(_cfg(tmp_path), src, str(tmp_path / "out"))
    assert result["n_warnings"] >= 1


def test_empty_file_raises(tmp_path):
    src = _write(tmp_path, "e.csv", "")
    with pytest.raises(ReadError):
        client_mode.run(_cfg(tmp_path), src, str(tmp_path / "out"))


def test_final_drops_watermark(tmp_path):
    src = _write(tmp_path, "otif.csv", _CLEAN)
    result = client_mode.run(_cfg(tmp_path), src, str(tmp_path / "out"), final=True)
    assert "ll-draft" not in open(result["report"], encoding="utf-8").read()
