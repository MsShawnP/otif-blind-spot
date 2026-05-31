"""Orchestrate the full OTIF data generation pipeline.

Steps:
  00 → query Cinderhaven DB → cache/cinderhaven_snapshot.json
  01 → synthesize OTIF data  → cache/otif_synthetic.json
  02 → export to frontend    → frontend/src/data/*.json

Usage:
  1. flyctl proxy 5432 -a cinderhaven-db
  2. python scripts/run_pipeline.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def run(script: str):
    print(f"\n{'─' * 60}", flush=True)
    print(f"Running {script}...", flush=True)
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script)],
        cwd=str(SCRIPTS_DIR),
    )
    if result.returncode != 0:
        print(f"ERROR: {script} failed (exit code {result.returncode})", flush=True)
        sys.exit(result.returncode)


def main():
    print("OTIF Blind Spot — Data Generation Pipeline", flush=True)
    run("00_query_cinderhaven.py")
    run("01_synthesize_otif.py")
    run("02_export_json.py")
    print(f"\n{'─' * 60}", flush=True)
    print("Pipeline complete.", flush=True)


if __name__ == "__main__":
    main()
