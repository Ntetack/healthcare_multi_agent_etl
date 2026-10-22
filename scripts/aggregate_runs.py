#!/usr/bin/env python3
"""Aggregate the R runs of each scenario and test hypotheses H1-H3 of the Methodology.

Input: a long CSV, one value per row, with the columns
    scenario   S1, S2, S3, S4
    metric     f1, field_agreement, precision, recall, ... (any name)
    unit       optional: the table for field_agreement, empty otherwise
    run        run number (1..R)
    batch      only for S4: 1 (first batch) or 2 (second batch), empty otherwise
    value      the measured value, in [0, 1] for the rates

Output:
    - for every (scenario, metric, unit): n, mean, standard deviation, min, max
    - H1: mean F1 > 0.80 (S1, S3), one-sided one-sample t-test
    - H2: mean field agreement per table > 0.90 (S1, S2, S3), same test
    - H3: S4, paired differences (second minus first batch) of F1 and of the mean
      field agreement, TOST with equivalence margin +-0.05
    alpha = 0.05; the unit of analysis is the run; no correction for multiple tests.
    When the standard deviation is 0 the test is not defined: the mean is compared
    directly to the threshold (or the difference to the margin) and the p-value is
    reported as n/a.

Usage:
    python scripts/aggregate_runs.py runs.csv [--out report.md] [--alpha 0.05]
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from collections import defaultdict

from scipy import stats

H1 = {"metric": "f1", "scenarios": ("S1", "S3"), "threshold": 0.80}
H2 = {"metric": "field_agreement", "scenarios": ("S1", "S2", "S3"), "threshold": 0.90}
H3 = {"scenario": "S4", "metrics": ("f1", "field_agreement"), "margin": 0.05}


def describe(values: list[float]) -> dict:
    n = len(values)
    return {"n": n, "mean": statistics.fmean(values),
            "sd": statistics.stdev(values) if n > 1 else float("nan"),
            "min": min(values), "max": max(values)}


def one_sided_greater(values: list[float], threshold: float, alpha: float) -> dict:
    """H1: mean > threshold. One-sample t-test, one-sided."""
    d = describe(values)
    n, mean, sd = d["n"], d["mean"], d["sd"]
    if n < 2:
        return {**d, "t": None, "p": None, "dz": None, "reject": None, "note": "n < 2"}
    if sd == 0:
        return {**d, "t": None, "p": None, "dz": None, "reject": mean > threshold,
                "note": "sd = 0: mean compared directly to the threshold"}
    t, p = stats.ttest_1samp(values, threshold, alternative="greater")
    return {**d, "t": float(t), "p": float(p), "dz": (mean - threshold) / sd,
            "reject": bool(p < alpha), "note": ""}


def tost(diffs: list[float], margin: float, alpha: float) -> dict:
    """H3: mean difference within +-margin. Two one-sided t-tests; p = max of the two."""
    d = describe(diffs)
    n, mean, sd = d["n"], d["mean"], d["sd"]
    if n < 2:
        return {**d, "p": None, "equivalent": None, "note": "n < 2"}
    if sd == 0:
        return {**d, "p": None, "equivalent": abs(mean) < margin,
                "note": "sd = 0: difference compared directly to the margin"}
    p_low = stats.ttest_1samp(diffs, -margin, alternative="greater").pvalue
    p_up = stats.ttest_1samp(diffs, margin, alternative="less").pvalue
    p = float(max(p_low, p_up))
    return {**d, "p": p, "equivalent": bool(p < alpha), "note": ""}


def read_runs(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["value"].strip() == "":
                continue
            rows.append({"scenario": r["scenario"].strip(), "metric": r["metric"].strip(),
                         "unit": (r.get("unit") or "").strip(), "run": int(r["run"]),
                         "batch": (r.get("batch") or "").strip(), "value": float(r["value"])})
    return rows


def analyse(rows: list[dict], alpha: float = 0.05) -> dict:
    groups = defaultdict(dict)   # (scenario, metric, unit, batch) -> {run: value}
    for r in rows:
        groups[(r["scenario"], r["metric"], r["unit"], r["batch"])][r["run"]] = r["value"]

    descriptive = {k: describe(list(v.values())) for k, v in sorted(groups.items())}

    h1 = {}
    for (sc, metric, unit, batch), runs in sorted(groups.items()):
        if metric == H1["metric"] and sc in H1["scenarios"] and not unit:
            h1[sc] = one_sided_greater(list(runs.values()), H1["threshold"], alpha)

    h2 = {}
    for (sc, metric, unit, batch), runs in sorted(groups.items()):
        if metric == H2["metric"] and sc in H2["scenarios"] and unit:
            h2[(sc, unit)] = one_sided_greater(list(runs.values()), H2["threshold"], alpha)

    h3 = {}
    for metric in H3["metrics"]:
        first = groups.get((H3["scenario"], metric, "", "1"), {})
        second = groups.get((H3["scenario"], metric, "", "2"), {})
        common = sorted(set(first) & set(second))
        if common:
            h3[metric] = tost([second[r] - first[r] for r in common], H3["margin"], alpha)
    return {"descriptive": descriptive, "H1": h1, "H2": h2, "H3": h3}


def _f(x, nd=4):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def _p(x):
    """A p-value to 4 decimals; below 0.0001 it is written as such, never as 0.0000."""
    if x is None:
        return "n/a"
    return "<0.0001" if x < 0.0001 else f"{x:.4f}"


def _verdict(res: dict, key: str) -> str:
    v = res[key]
    return "n/a" if v is None else ("yes" if v else "no")


def render(result: dict, alpha: float) -> str:
    out = ["# Aggregation of the runs", "", "## Descriptive statistics", "",
           "| Scenario | Metric | Unit | Batch | n | Mean | SD | Min | Max |", "|---|---|---|---|---|---|---|---|---|"]
    for (sc, m, u, b), d in result["descriptive"].items():
        out.append(f"| {sc} | {m} | {u or '-'} | {b or '-'} | {d['n']} | {_f(d['mean'])} | {_f(d['sd'])} | {_f(d['min'])} | {_f(d['max'])} |")
    out += ["", f"## H1 - mean F1 > {H1['threshold']} (one-sided t-test, alpha = {alpha})", "",
            "| Scenario | n | Mean | SD | t | p | d_z | Rejected H0 | Note |", "|---|---|---|---|---|---|---|---|---|"]
    for sc, r in result["H1"].items():
        out.append(f"| {sc} | {r['n']} | {_f(r['mean'])} | {_f(r['sd'])} | {_f(r['t'], 3)} | {_p(r['p'])} | {_f(r['dz'], 2)} | {_verdict(r, 'reject')} | {r['note']} |")
    out += ["", f"## H2 - mean field agreement per table > {H2['threshold']} (one-sided t-test, alpha = {alpha})", "",
            "| Scenario | Table | n | Mean | SD | t | p | d_z | Rejected H0 | Note |", "|---|---|---|---|---|---|---|---|---|---|"]
    for (sc, u), r in result["H2"].items():
        out.append(f"| {sc} | {u} | {r['n']} | {_f(r['mean'])} | {_f(r['sd'])} | {_f(r['t'], 3)} | {_p(r['p'])} | {_f(r['dz'], 2)} | {_verdict(r, 'reject')} | {r['note']} |")
    out += ["", f"## H3 - S4 schema drift, TOST on (second - first batch), margin +-{H3['margin']} (alpha = {alpha})", "",
            "| Metric | n | Mean difference | SD | p (TOST) | Equivalent | Note |", "|---|---|---|---|---|---|---|"]
    for m, r in result["H3"].items():
        out.append(f"| {m} | {r['n']} | {_f(r['mean'])} | {_f(r['sd'])} | {_p(r['p'])} | {_verdict(r, 'equivalent')} | {r['note']} |")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs_csv")
    ap.add_argument("--out")
    ap.add_argument("--alpha", type=float, default=0.05)
    a = ap.parse_args(argv)
    text = render(analyse(read_runs(a.runs_csv), a.alpha), a.alpha)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
