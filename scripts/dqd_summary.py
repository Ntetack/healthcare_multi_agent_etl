#!/usr/bin/env python3
"""Recompute the DQD pass rate from the JSON output of the OHDSI Data Quality Dashboard.

The rate follows the definition of the Methodology:

    DQD pass rate = passed / (passed + failed)

Checks that are not applicable are left out. Checks that ended in an error
are counted apart and are not part of the rate. The percentage shown by the
Shiny viewer is NOT used: it counts the not-applicable checks as passed.

Usage:
    python scripts/dqd_summary.py run1.json [run2.json ...]
        [--labels A B ...] [--csv summary.csv] [--failed-csv failed.csv]
        [--aggregate]

With --aggregate, the mean, standard deviation, minimum and maximum of the
pass rate over the files are added (one file per run of the same scenario).
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

CATEGORIES = ("Completeness", "Conformance", "Plausibility")


def _flag(check: dict, key: str) -> bool:
    return check.get(key) in (1, True)


def classify(check: dict) -> str:
    """Return 'not_applicable', 'error', 'failed' or 'passed' (one only)."""
    if _flag(check, "notApplicable"):
        return "not_applicable"
    if _flag(check, "isError"):
        return "error"
    if _flag(check, "failed"):
        return "failed"
    if _flag(check, "passed"):
        return "passed"
    return "unknown"


def _rate(passed: int, failed: int):
    applicable = passed + failed
    return passed / applicable if applicable else None


def summarize(data: dict) -> tuple[dict, list[dict]]:
    """Counts and rate of one DQD result, plus the list of failed checks."""
    checks = data.get("CheckResults", [])
    counts = {k: 0 for k in ("passed", "failed", "not_applicable", "error", "unknown")}
    by_cat = {c: {"passed": 0, "failed": 0, "not_applicable": 0, "error": 0} for c in CATEGORIES}
    failed_list: list[dict] = []
    for ch in checks:
        status = classify(ch)
        counts[status] += 1
        cat = ch.get("category")
        if cat in by_cat and status in by_cat[cat]:
            by_cat[cat][status] += 1
        if status == "failed":
            failed_list.append({
                "category": cat,
                "check": ch.get("checkName"),
                "table": ch.get("cdmTableName"),
                "field": ch.get("cdmFieldName"),
                "pct_violated_rows": ch.get("pctViolatedRows"),
                "num_violated_rows": ch.get("numViolatedRows"),
                "threshold": ch.get("thresholdValue"),
            })
    summary = {
        "n_checks": len(checks),
        **counts,
        "applicable": counts["passed"] + counts["failed"],
        "pass_rate": _rate(counts["passed"], counts["failed"]),
    }
    for c in CATEGORIES:
        summary[f"{c.lower()}_passed"] = by_cat[c]["passed"]
        summary[f"{c.lower()}_failed"] = by_cat[c]["failed"]
        summary[f"{c.lower()}_rate"] = _rate(by_cat[c]["passed"], by_cat[c]["failed"])
    shiny = (data.get("Overview") or {}).get("percentPassed")
    if isinstance(shiny, list):
        shiny = shiny[0] if shiny else None
    summary["viewer_pct_passed"] = shiny  # shown for comparison only
    return summary, failed_list


def aggregate(rates: list[float]) -> dict:
    vals = [r for r in rates if r is not None]
    if not vals:
        return {}
    return {
        "n_runs": len(vals),
        "mean": statistics.fmean(vals),
        "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        "min": min(vals),
        "max": max(vals),
    }


def _pct(x):
    return "n/a" if x is None else f"{100 * x:.2f} %"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--labels", nargs="*", help="one label per file (default: file name)")
    ap.add_argument("--csv", help="write the summary table to this CSV file")
    ap.add_argument("--failed-csv", help="write the failed checks to this CSV file")
    ap.add_argument("--aggregate", action="store_true", help="add mean, sd, min, max of the pass rate")
    a = ap.parse_args(argv)

    labels = a.labels or [Path(f).stem for f in a.files]
    if len(labels) != len(a.files):
        sys.exit("--labels must have one value per file")

    rows, failed_rows = [], []
    for label, path in zip(labels, a.files):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        s, failed = summarize(data)
        rows.append({"run": label, **s})
        failed_rows += [{"run": label, **f} for f in failed]

    print(f"{'run':<28}{'checks':>7}{'passed':>8}{'failed':>8}{'N/A':>7}{'error':>7}{'pass rate':>11}")
    for r in rows:
        print(f"{r['run'][:27]:<28}{r['n_checks']:>7}{r['passed']:>8}{r['failed']:>8}"
              f"{r['not_applicable']:>7}{r['error']:>7}{_pct(r['pass_rate']):>11}")
        for c in CATEGORIES:
            k = c.lower()
            print(f"  {c:<26}{'':>7}{r[k + '_passed']:>8}{r[k + '_failed']:>8}{'':>14}{_pct(r[k + '_rate']):>11}")
        if r["viewer_pct_passed"] is not None:
            print(f"  (viewer shows {r['viewer_pct_passed']} %, with not-applicable counted as passed)")
        if r["unknown"]:
            print(f"  ! {r['unknown']} check(s) without status")
    if a.aggregate:
        agg = aggregate([r["pass_rate"] for r in rows])
        if agg:
            print(f"\nover {agg['n_runs']} run(s): mean {_pct(agg['mean'])}, sd {100 * agg['sd']:.2f} points, "
                  f"min {_pct(agg['min'])}, max {_pct(agg['max'])}")

    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    if a.failed_csv:
        cols = ["run", "category", "check", "table", "field", "pct_violated_rows", "num_violated_rows", "threshold"]
        with open(a.failed_csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(failed_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
