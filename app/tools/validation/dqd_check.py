"""
DQD (OHDSI Data Quality Dashboard) tool - the sole data-quality validator
(architecture doc v6, decision "validation par DQD uniquement").

DataQualityDashboard is an R package. We bridge it via subprocess, calling
database/scripts/run_dqd.R, and parse its JSON output back into Python.
Runs against OMOP_TEMP only (truncated at the start of each run), so
results reflect the current batch exclusively.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

RSCRIPT_BIN = os.getenv("RSCRIPT_BIN", "Rscript")
DQD_OUTPUT_DIR = Path(os.getenv("DQD_OUTPUT_DIR", "runs"))
RUN_DQD_SCRIPT = Path("database/scripts/run_dqd.R")


def run_dqd_checks(execution_id: str, cdm_schema: str = "omop_temp") -> dict:
    """Executes the DQD R script against cdm_schema, returns the parsed
    result JSON. Raises CalledProcessError on a hard R/DB failure (that's
    a technical error -> logged, not a quality validator per se - see
    architecture doc v6, top of doc)."""
    output_dir = DQD_OUTPUT_DIR / execution_id / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            RSCRIPT_BIN, str(RUN_DQD_SCRIPT),
            "--cdmSchema", cdm_schema,
            "--outputFolder", str(output_dir),
            "--cdmSourceName", execution_id,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    result_files = list(output_dir.glob("*.json"))
    if not result_files:
        raise FileNotFoundError(f"DQD produced no JSON output in {output_dir}")
    with open(result_files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def summarize_dqd_result(dqd_result: dict) -> dict:
    """Splits DQD checks by severity so the Validation Agent can apply a
    simple pass/fail rule: only FATAL failures block the pipeline;
    CONVENTION/CHARACTERIZATION failures are logged as warnings."""
    checks = dqd_result.get("CheckResults", [])
    by_severity: dict[str, list] = {"FATAL": [], "CONVENTION": [], "CHARACTERIZATION": []}
    for check in checks:
        if check.get("FAILED") == 1:
            severity = check.get("checkSeverity", "CHARACTERIZATION").upper()
            by_severity.setdefault(severity, []).append(check)

    return {
        "total_checks": len(checks),
        "failed_fatal": len(by_severity["FATAL"]),
        "failed_convention": len(by_severity["CONVENTION"]),
        "failed_characterization": len(by_severity["CHARACTERIZATION"]),
        "passed": len(by_severity["FATAL"]) == 0,
        "details": by_severity,
    }
