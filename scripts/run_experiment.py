#!/usr/bin/env python3
"""Run R independent runs of one scenario: reset, pipeline, DQD, comparison.

For every run the script
  1. empties EVERY cache and every trace of a previous run:
       pipeline_meta.mapping_cache          (all sources, all kinds)
       pipeline_meta.processed_folders      (rows of the source, so the batches are new again)
       omop_temp and omop (final)           (the nine clinical tables)
     The vocabulary tables and cdm_source are left alone.
  2. runs the pipeline, either on ONE batch and stops (--mode single), or on every new
     batch, one after the other, until none is left (--mode all);
  3. copies the DQD json of each batch, recomputes its pass rate (scripts/dqd_summary.py rule)
     and records the elapsed time;
  3b. with --gold, adds the Precision, Recall and F1 of the batch's mapping against the gold set;
  4. runs scripts/run_full_comparison.py and appends the mean field agreement of each table
     to runs.csv (read by scripts/aggregate_runs.py).

Comparison:
  - scenario S4: after EACH batch, on omop_temp (which holds that batch only), with --batch k;
  - other scenarios: once, after the last batch; on omop_temp if one batch was processed,
    on omop (cumulative) if several were.

Everything after "--" is passed to run_full_comparison.py (B0 database, patients.csv, ...).

Example:
    python scripts/run_experiment.py --source hospital_b --scenario S1 --runs 5 --mode single \\
        --out results -- --patients-csv data/raw/hospital_b/mimic4/PATIENTS.csv \\
        --b1-source-column ROW_ID --b0-source-column SUBJECT_ID \\
        --b0-db-host localhost --b0-db-name mimic_omop --b0-schema public --b0-db-user u

--reset-only empties the caches and stops. --dry-run prints what would be done.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

SCRIPTS = ROOT / "scripts"
MAX_BATCHES = 50


# --------------------------------------------------------------------------- reset
def reset_everything(source: str, dry_run: bool = False) -> None:
    """Empty the mapping cache, forget the processed batches, empty omop_temp and omop."""
    from sqlalchemy import text
    from app.tools.database.db import OMOP_FINAL_SCHEMA, OMOP_TEMP_SCHEMA, OMOP_TABLES, session_scope
    statements = [
        "TRUNCATE TABLE pipeline_meta.mapping_cache",
        "DELETE FROM pipeline_meta.processed_folders WHERE source_name = :source",
    ] + [f'TRUNCATE TABLE "{schema}"."{t}" CASCADE'
         for schema in (OMOP_TEMP_SCHEMA, OMOP_FINAL_SCHEMA) for t in OMOP_TABLES]
    if dry_run:
        print("[dry-run] reset:", *statements, sep="\n  ")
        return
    with session_scope() as session:
        for sql in statements:
            session.execute(text(sql), {"source": source} if ":source" in sql else {})
    print(f"  caches and previous results emptied ({len(statements)} statements)")


def next_folder(source: str):
    from app.tools.data.folder_watcher import find_next_folder
    from app.tools.data.metadata_loader import source_root_path
    return find_next_folder(source, source_root_path(source))


# --------------------------------------------------------------------------- one batch
def run_pipeline(source: str, execution_id: str) -> int:
    t0 = time.time()
    code = subprocess.run([sys.executable, "-m", "app.main", "--source", source,
                           "--execution-id", execution_id], cwd=ROOT).returncode
    print(f"  pipeline exit code {code}, {time.time() - t0:.0f} s")
    return code


def collect_dqd(execution_id: str, dest: Path) -> Path | None:
    """Copy the raw result of the Data Quality Dashboard (the json that holds CheckResults).
    The validation folder also holds result.json, the agent's own summary, which is NOT the
    DQD output and cannot give the pass rate."""
    import json
    folder = ROOT / "runs" / execution_id / "validation"
    for path in sorted(folder.glob("*.json"), key=lambda q: q.stat().st_size, reverse=True):
        if path.name == "result.json":
            continue
        try:
            if "CheckResults" in json.loads(path.read_text(encoding="utf-8")):
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(path, dest)
                return dest
        except (OSError, ValueError):
            continue
    return None


def compare(schema: str, scenario: str, run: int, batch: str, runs_csv: Path, report: Path, extra: list[str]) -> int:
    cmd = [sys.executable, str(SCRIPTS / "run_full_comparison.py"), "--b1-schema", schema,
           "--output", str(report), "--runs-csv", str(runs_csv), "--scenario", scenario, "--run", str(run)]
    if batch:
        cmd += ["--batch", batch]
    return subprocess.run(cmd + extra, cwd=ROOT).returncode


def mapping_scores(gold: str, execution_id: str, scenario: str, run: int, batch: str, runs_csv: Path) -> None:
    """Precision, Recall and F1 of this batch's mapping against the gold set, appended to runs.csv."""
    import mapping_metrics
    report = ROOT / "runs" / execution_id / "mapping" / "report.csv"
    scores = mapping_metrics.score(Path(gold), report)
    mapping_metrics.append_rows(runs_csv, scenario, run, scores, batch)
    print(f"  mapping vs gold: P={scores['precision']:.4f} R={scores['recall']:.4f} F1={scores['f1']:.4f}")


def append_metrics(path: Path, row: dict) -> None:
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)


# --------------------------------------------------------------------------- one run
def one_run(a, run: int, extra: list[str], hooks) -> bool:
    """Returns True if the run went to the end. `hooks` holds the functions that touch the outside
    (database, subprocess), so the loop can be tested without them."""
    out = Path(a.out) / a.scenario / f"run{run}"
    print(f"\n=== {a.scenario} run {run}/{a.runs} ===")
    hooks.reset(a.source, a.dry_run)
    processed, previous = 0, None
    while processed < (1 if a.mode == "single" else MAX_BATCHES):
        folder = hooks.next_folder(a.source)
        if folder is None:
            print("  nothing left to process")
            break
        if str(folder) == previous:
            print(f"  batch {folder.name} was not completed; stopping this run")
            return False
        previous, processed = str(folder), processed + 1
        execution_id = f"{a.scenario}-run{run}-b{processed}"
        print(f"  batch {processed}: {folder.name} (execution {execution_id})")
        t0 = time.time()
        code = hooks.run_pipeline(a.source, execution_id)
        elapsed = time.time() - t0
        dqd = hooks.collect_dqd(execution_id, out / f"batch{processed}_dqd.json")
        hooks.append_metrics(Path(a.out) / "metrics.csv", {
            "scenario": a.scenario, "run": run, "batch": processed, "folder": folder.name,
            "execution_id": execution_id, "exit_code": code, "seconds": f"{elapsed:.1f}",
            "dqd_json": str(dqd) if dqd else ""})
        if code != 0:
            return False
        if a.gold:
            hooks.mapping_scores(a.gold, execution_id, a.scenario, run,
                                 str(processed) if a.scenario == "S4" else "", Path(a.out) / "runs.csv")
        if a.scenario == "S4":
            rc = hooks.compare("omop_temp", a.scenario, run, str(processed), Path(a.out) / "runs.csv",
                               out / f"batch{processed}_comparison.md", extra)
            if rc != 0:
                return False
    if processed and a.scenario != "S4":
        schema = "omop_temp" if processed == 1 else "omop"
        rc = hooks.compare(schema, a.scenario, run, "", Path(a.out) / "runs.csv", out / "comparison.md", extra)
        return rc == 0
    return processed > 0


class Hooks:
    reset = staticmethod(reset_everything)
    next_folder = staticmethod(next_folder)
    run_pipeline = staticmethod(run_pipeline)
    collect_dqd = staticmethod(collect_dqd)
    compare = staticmethod(compare)
    append_metrics = staticmethod(append_metrics)
    mapping_scores = staticmethod(mapping_scores)


def main(argv=None, hooks=Hooks) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    extra = []
    if "--" in argv:
        i = argv.index("--")
        argv, extra = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--scenario", required=True, choices=["S1", "S2", "S3", "S4"])
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--first-run", type=int, default=1, help="number of the first run (to resume)")
    ap.add_argument("--mode", choices=["single", "all"], default="single",
                    help="single: one batch per run, then stop; all: every new batch, one after the other")
    ap.add_argument("--out", default="results")
    ap.add_argument("--gold", default=None,
                    help="gold mapping set: Precision, Recall and F1 of each batch's mapping are added to runs.csv")
    ap.add_argument("--reset-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    if a.dry_run:
        hooks.reset(a.source, True)
        print(f"[dry-run] {a.runs} run(s) of {a.scenario}, mode {a.mode}, out {a.out}; "
              f"comparison arguments: {extra or 'none'}. Nothing was executed.")
        return 0
    if a.reset_only:
        hooks.reset(a.source, a.dry_run)
        return 0
    failed = []
    for run in range(a.first_run, a.first_run + a.runs):
        if not one_run(a, run, extra, hooks):
            failed.append(run)
    print(f"\nDone. Runs not completed: {failed or 'none'}")
    print(f"Aggregate with: python scripts/aggregate_runs.py {Path(a.out) / 'runs.csv'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
