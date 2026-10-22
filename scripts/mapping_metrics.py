#!/usr/bin/env python3
"""Precision, Recall and F1 of the structural mapping of a run against the gold mapping set.

The three values are the micro-averaged ones of scripts/evaluate_mapping.py (counted over
all source-to-target field pairs): Precision = |M_B1 inter M_GT| / |M_B1|, Recall =
|M_B1 inter M_GT| / |M_GT|, F1 = their harmonic mean. They are appended to the long CSV
read by scripts/aggregate_runs.py (metric = precision, recall, f1; no unit).

One run:
    python scripts/mapping_metrics.py --gold data/raw/hospital_a/gold_standard_scoped.csv \\
        --agent runs/S1-run1-b1/mapping/report.csv --scenario S1 --run 1 --runs-csv results/runs.csv

Runs already done (the mapping report of each run stays in runs/):
    python scripts/mapping_metrics.py --gold GOLD --scenario S1 --backfill 5 \\
        --agent-template "runs/S1-run{run}-b1/mapping/report.csv" --runs-csv results/runs.csv

A row already written for the same (scenario, metric, run, batch) is replaced.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate_mapping as em  # noqa: E402

HEADER = ["scenario", "metric", "unit", "run", "batch", "value"]
METRICS = ("precision", "recall", "f1")


def score(gold_csv: Path, agent_csv: Path) -> dict:
    """Micro Precision, Recall and F1 of one mapping report, plus the pair counts."""
    gold = em.load_gold(Path(gold_csv))
    agent = em.load_agent_report(Path(agent_csv))
    m = em.evaluate(gold, agent)["map"]
    return {"precision": m["micro_precision"], "recall": m["micro_recall"], "f1": m["micro_f1"],
            "tp": m["tp"], "fp": m["fp"], "fn": m["fn"]}


def append_rows(path: Path, scenario: str, run: int, scores: dict, batch: str = "") -> None:
    old = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            old = list(csv.DictReader(fh))
    new = [{"scenario": scenario, "metric": k, "unit": "", "run": str(run), "batch": str(batch),
            "value": f"{scores[k]:.6f}"} for k in METRICS]
    replaced = {(r["scenario"], r["metric"], r["run"], r["batch"]) for r in new}
    kept = [r for r in old if not (r["metric"] in METRICS and not r.get("unit")
                                   and (r["scenario"], r["metric"], r["run"], r["batch"]) in replaced)]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows([{k: r.get(k, "") for k in HEADER} for r in kept + new])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gold", required=True, type=Path)
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--runs-csv", required=True, type=Path)
    ap.add_argument("--agent", type=Path, help="mapping report.csv of one run")
    ap.add_argument("--run", type=int)
    ap.add_argument("--batch", default="")
    ap.add_argument("--backfill", type=int, help="number of runs already done (1..N)")
    ap.add_argument("--agent-template", help='path with {run}, e.g. "runs/S1-run{run}-b1/mapping/report.csv"')
    ap.add_argument("--first-run", type=int, default=1)
    a = ap.parse_args(argv)

    jobs = []
    if a.backfill:
        if not a.agent_template:
            ap.error("--backfill needs --agent-template")
        jobs = [(r, Path(a.agent_template.format(run=r))) for r in range(a.first_run, a.first_run + a.backfill)]
    else:
        if not a.agent or a.run is None:
            ap.error("give --agent and --run, or --backfill with --agent-template")
        jobs = [(a.run, a.agent)]
    for run, agent in jobs:
        s = score(a.gold, agent)
        append_rows(a.runs_csv, a.scenario, run, s, a.batch)
        print(f"{a.scenario} run {run}: P={s['precision']:.4f} R={s['recall']:.4f} F1={s['f1']:.4f} "
              f"(TP {s['tp']} / FP {s['fp']} / FN {s['fn']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
