"""Client-mode CLI for otif-blind-spot.

Reconciles a client's internal fill against their retailer OTIF scorecard and
prices the exposure — validated, never committed, never deployed. The demo React
app is untouched.

Intake is one OTIF scorecard file (one row per shipment). The tool computes the
internal-fill vs retailer-OTIF gap, the on-time/in-full split, and the fines
exposure (annualized on the config window). Velocity damage is MODELED in the
demo; from a scorecard alone it can't be computed, so it is disclosed as a data
limitation rather than invented.

Usage:
    python client_mode.py --config engagement.yml --input client-data/otif.csv \
        --out client-output [--final]
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from lailara_engagement import (
    ColumnSpec,
    PreflightSpec,
    build_provenance,
    load_config,
    read_table,
    run_preflight,
    validation_status_label,
    write_report,
)
from lailara_engagement import palette as P
from lailara_engagement.provenance import Provenance

TOOL = "otif-blind-spot"
TOOL_VERSION = "1.0"

_TRUE = {"true", "1", "yes", "y", "t", "pass", "on-time", "on time", "in-full", "in full"}
_FALSE = {"false", "0", "no", "n", "f", "fail", "late", "short"}


def _spec() -> PreflightSpec:
    return PreflightSpec(
        tool=TOOL, version=TOOL_VERSION,
        columns=[
            ColumnSpec(name="shipment_id", dtype="identifier", required=True, unique=True,
                       description="unique shipment id", spec_ref="INPUT-SPEC §1"),
            ColumnSpec(name="ship_date", dtype="date", required=True,
                       description="ship date (windowing/annualization)", spec_ref="INPUT-SPEC §1"),
            ColumnSpec(name="on_time_result", dtype="string", required=True,
                       description="on-time pass/fail (true/false)", spec_ref="INPUT-SPEC §1"),
            ColumnSpec(name="in_full_result", dtype="string", required=True,
                       description="in-full pass/fail (true/false)", spec_ref="INPUT-SPEC §1"),
            ColumnSpec(name="po_units", dtype="number", required=True, not_negative=True,
                       description="units ordered on the PO", spec_ref="INPUT-SPEC §1"),
            ColumnSpec(name="shipped_units", dtype="number", required=True, not_negative=True,
                       description="units shipped", spec_ref="INPUT-SPEC §1"),
            ColumnSpec(name="otif_fine", dtype="number", required=False, allow_blank=True,
                       not_negative=True, description="OTIF fine assessed on this shipment"),
            ColumnSpec(name="retailer", dtype="string", required=False, allow_blank=True,
                       description="retailer the scorecard is from"),
        ],
    )


def _to_bool(v: str) -> bool:
    return str(v).strip().casefold() in _TRUE


def _num(v) -> float:
    try:
        return float(str(v).strip())
    except (ValueError, TypeError):
        return 0.0


def run(config_path: str, input_path: str, out_dir: str, *, final: bool = False) -> dict:
    config = load_config(config_path)
    read = read_table(input_path)
    spec = _spec()
    report = run_preflight(read, spec, config)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    provenance = build_provenance(
        tool=TOOL, tool_version=TOOL_VERSION, inputs=[read], config=config,
        validation_status=validation_status_label(report.status, report.n_warnings))
    if not report.passed:
        paths = write_report(report, config, str(out), provenance=provenance,
                             draft=not final, basename="data-readiness-report",
                             title="OTIF Data Readiness Report")
        return {"status": "blocked", "readiness_report": paths["html"]}

    m = report.column_mapping
    frame = read.frame

    def col(name):
        r = m.get(name)
        return frame[r] if r else None

    ot = col("on_time_result"); inf = col("in_full_result")
    pou = col("po_units"); shp = col("shipped_units")
    fine = col("otif_fine")
    n = len(frame)
    total_ordered = total_shipped = 0.0
    otif_pass = ontime_fail = infull_fail = 0
    total_fines = 0.0
    for i in range(n):
        o = _to_bool(ot.iloc[i]); f = _to_bool(inf.iloc[i])
        total_ordered += _num(pou.iloc[i]); total_shipped += _num(shp.iloc[i])
        if o and f:
            otif_pass += 1
        if not o:
            ontime_fail += 1
        if not f:
            infull_fail += 1
        if fine is not None:
            total_fines += _num(fine.iloc[i])

    internal_fill = (total_shipped / total_ordered) if total_ordered else 0.0
    retailer_otif = (otif_pass / n) if n else 0.0
    gap_pts = round((internal_fill - retailer_otif) * 100, 2)
    window_months = int(config.basis.get("window_months") or 0) or None
    annual_fines = (total_fines * 12 / window_months) if (window_months and fine is not None) else None

    summary = {
        "window": {"months": window_months, "label": config.basis.get("window_label", "")},
        "shipments": n,
        "internal_fill_rate": round(internal_fill, 4),
        "retailer_otif": round(retailer_otif, 4),
        "gap_pts": gap_pts,
        "ontime_fail_rate": round(ontime_fail / n, 4) if n else 0,
        "infull_fail_rate": round(infull_fail / n, 4) if n else 0,
        "otif_fines_total": round(total_fines, 2) if fine is not None else None,
        "annual_fines": round(annual_fines, 2) if annual_fines is not None else None,
    }
    limitations = []
    if fine is None:
        limitations.append("No `otif_fine` column — fines exposure not computed.")
    if window_months is None:
        limitations.append("No `basis.window_months` — fines not annualized.")
    limitations.append("Velocity damage (lost-shelf-sales from OTIF failures) is a MODELED figure in "
                       "the demo; it cannot be derived from a scorecard alone and is not included here.")

    json_dir = out / "json"; json_dir.mkdir(parents=True, exist_ok=True)
    (json_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report_path = out / "otif-gap-summary.html"
    report_path.write_text(_summary_html(config, summary, limitations, provenance, draft=not final),
                           encoding="utf-8")
    return {"status": "ok", "gap_pts": gap_pts, "shipments": n,
            "report": str(report_path), "summary_json": str(json_dir / "summary.json"),
            "n_warnings": report.n_warnings}


def _pct(v):
    return "—" if v is None else f"{v*100:.1f}%"


def _dol(v):
    return "—" if v is None else f"${v:,.0f}"


def _summary_html(config, s, limitations, provenance: Provenance, *, draft: bool) -> str:
    esc = html.escape
    wm = s["window"].get("months"); wl = s["window"].get("label") or ""
    win = (f"{wm} months" + (f" ({esc(wl)})" if wl else "")) if wm else "full window"
    lim = "".join(f"<li>{esc(x)}</li>" for x in limitations)
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>OTIF Gap — {esc(config.client_name)}</title><style>{_css(draft)}</style></head>
<body class="{' ll-draft' if draft else ''}"><main class=ll-page>
<header class=ll-header>
  <div class=ll-eyebrow>Lailara LLC · OTIF Blind Spot</div>
  <h1 class=ll-title>Internal Fill vs Retailer OTIF</h1>
  <div class=ll-client>
    <div><span class=ll-k>Client</span> {esc(config.client_name)}</div>
    <div><span class=ll-k>Engagement</span> {esc(config.engagement_id)}</div>
    <div><span class=ll-k>As of</span> {esc(config.as_of_date.isoformat())}</div>
    <div><span class=ll-k>Window</span> {win}</div>
  </div>
</header>
<section class=ll-banner>
  <div class=ll-score>{_pct(s['internal_fill_rate'])} internal &ne; {_pct(s['retailer_otif'])} retailer OTIF</div>
  <div>{s['gap_pts']:.1f}-point gap across {s['shipments']:,} shipments over {win}</div>
</section>
<section class=ll-section>
  <h2 class=ll-h2>The gap</h2>
  <table class=ll-table>
    <tr><td>Internal fill rate (at your dock)</td><td class=num>{_pct(s['internal_fill_rate'])}</td></tr>
    <tr><td>Retailer OTIF (at their dock)</td><td class=num>{_pct(s['retailer_otif'])}</td></tr>
    <tr><td>Gap</td><td class=num>{s['gap_pts']:.1f} pts</td></tr>
    <tr><td>On-time failures</td><td class=num>{_pct(s['ontime_fail_rate'])}</td></tr>
    <tr><td>In-full failures</td><td class=num>{_pct(s['infull_fail_rate'])}</td></tr>
    <tr><td>OTIF fines (total · annualized)</td><td class=num>{_dol(s['otif_fines_total'])} · {_dol(s['annual_fines'])}</td></tr>
  </table>
  <p class=ll-note>Internal fill = units shipped / units ordered. Retailer OTIF = share of
  shipments both on time and in full. Gap is computed from the raw rates. Annualization
  is x12/{wm if wm else '—'}.</p>
</section>
<section class=ll-section><h2 class=ll-h2>Data limitations</h2><ul class=ll-limitations>{lim}</ul></section>
{provenance.to_html()}
</main></body></html>"""


def _css(draft: bool) -> str:
    draft_css = (
        ".ll-draft::before{content:'DRAFT';position:fixed;top:50%;left:50%;"
        "transform:translate(-50%,-50%) rotate(-32deg);font-family:var(--s);"
        "font-size:22vw;font-weight:700;color:rgba(204,16,10,.06);z-index:0;"
        "pointer-events:none;white-space:nowrap}" if draft else ""
    )
    return f"""
:root{{--s:{P.LL_SERIF};--f:{P.LL_SANS}}}*{{box-sizing:border-box}}
body{{margin:0;background:{P.LL_CANVAS};color:{P.LL_TEXT};font-family:var(--f);line-height:1.6}}
.ll-page{{position:relative;z-index:1;max-width:{P.LL_MAX_WIDTH};margin:0 auto;padding:48px 24px}}
.ll-header{{border-bottom:1px solid {P.LL_GRIDLINE};padding-bottom:24px;margin-bottom:24px}}
.ll-eyebrow{{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:{P.LL_RED};font-weight:600}}
.ll-title{{font-family:var(--s);font-weight:700;color:{P.LL_INK};font-size:34px;margin:8px 0 16px}}
.ll-client{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px 24px;font-size:14px}}
.ll-k{{display:block;color:{P.LL_TEXT_SEC};font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
.ll-banner{{border-radius:2px;padding:16px 20px;margin-bottom:32px;background:{P.LL_SG_SURFACE};color:{P.LL_SG_DARK}}}
.ll-score{{font-family:var(--s);font-weight:700;font-size:22px}}
.ll-section{{margin:0 0 32px}}
.ll-h2{{font-family:var(--s);font-weight:700;color:{P.LL_INK};font-size:22px;
margin:0 0 12px;padding-bottom:6px;border-bottom:1px solid {P.LL_GRIDLINE}}}
.ll-note{{font-size:13px;color:{P.LL_TEXT_SEC};margin-top:8px}}
.ll-table{{width:100%;border-collapse:collapse;font-size:14px}}
.ll-table th{{text-align:left;background:{P.LL_CHICAGO};color:#fff;padding:8px 12px}}
.ll-table td{{padding:8px 12px;border-bottom:1px solid {P.LL_GRIDLINE}}}
.ll-limitations{{margin:0;padding-left:20px}}.ll-limitations li{{margin-bottom:6px}}
.num{{text-align:right;font-variant-numeric:tabular-nums}}
.ll-provenance{{margin-top:40px;background:{P.LL_CARD_BG};color:{P.LL_CARD_TEXT};
padding:20px 24px;border-radius:2px;font-size:13px}}
.ll-prov-title{{font-family:var(--s);font-weight:700;font-size:16px;margin-bottom:8px}}
.ll-provenance div{{margin-bottom:4px;color:{P.LL_CARD_SUBTITLE}}}
.ll-provenance strong{{color:{P.LL_CARD_TEXT}}}
.ll-prov-inputs{{width:100%;border-collapse:collapse;margin-top:8px}}
.ll-prov-inputs th{{text-align:left;border-bottom:1px solid rgba(255,255,255,.12);padding:4px 8px;color:{P.LL_CARD_MUTED}}}
.ll-prov-inputs td{{padding:4px 8px;border-bottom:1px solid rgba(255,255,255,.08);color:{P.LL_CARD_SUBTITLE}}}
.ll-prov-brand{{margin-top:12px;font-family:var(--s);color:{P.LL_CARD_MUTED}}}
{draft_css}
@media print{{body{{background:#fff}}}}
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="otif client mode")
    ap.add_argument("--config", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default="client-output")
    ap.add_argument("--final", action="store_true")
    args = ap.parse_args(argv)
    result = run(args.config, args.input, args.out, final=args.final)
    if result["status"] == "blocked":
        print(f"BLOCKED — data not ready. See {result['readiness_report']}")
        return 3
    print(f"gap {result['gap_pts']:.1f} pts across {result['shipments']:,} shipments")
    print(f"report -> {result['report']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
