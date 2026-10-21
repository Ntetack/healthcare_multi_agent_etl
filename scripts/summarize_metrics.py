"""Summarises execution time and token usage of one or several runs.

Usage:
    python scripts/summarize_metrics.py RUN-ID [RUN-ID ...]
    python scripts/summarize_metrics.py --all
    python scripts/summarize_metrics.py RUN-ID --csv metrics.csv

Reads runs/<execution_id>/metrics.jsonl, written by every agent execution
(see app/agents/base.py). One Markdown table per run is printed; --csv also
writes one row per (run, agent, operation) for use in spreadsheets.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.common import io_utils  # noqa: E402
from app.tools.common.metrics import METRICS_FILENAME, format_summary, summarize_run  # noqa: E402

CSV_FIELDS = [
    "execution_id", "agent", "operation", "executions", "failed_executions",
    "duration_seconds", "llm_seconds", "llm_calls", "input_tokens",
    "output_tokens", "reasoning_tokens", "total_tokens",
    "rate_limit_retries", "calls_without_usage",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_ids", nargs="*", help="execution ids under runs/")
    parser.add_argument("--all", action="store_true", help="every run that has a metrics.jsonl")
    parser.add_argument("--csv", type=Path, default=None, help="also write the rows to this CSV file")
    args = parser.parse_args()

    run_ids = list(args.run_ids)
    if args.all:
        run_ids = sorted(p.parent.name for p in io_utils.RUNS_DIR.glob(f"*/{METRICS_FILENAME}"))
    if not run_ids:
        parser.error("give at least one run id, or --all")

    rows = []
    for run_id in run_ids:
        summary = summarize_run(run_id)
        if not summary["agents"]:
            print(f"{run_id}: no {METRICS_FILENAME} found (run made before metrics were added?)\n")
            continue
        print(f"## {run_id}\n\n{format_summary(summary)}\n")
        rows += [{"execution_id": run_id, **r} for r in summary["agents"]]

    if args.csv and rows:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        print(f"CSV written to {args.csv}")


if __name__ == "__main__":
    main()
