"""Tests for the DQD pass rate recomputation."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load():
    path = Path(__file__).resolve().parents[2] / "scripts" / "dqd_summary.py"
    spec = importlib.util.spec_from_file_location("_script_dqd_summary", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dqd = _load()


def _check(status, category="Conformance", name="c", table="PERSON", field="F", pct=0.0):
    flags = {"passed": 0, "failed": 0, "isError": 0, "notApplicable": 0}
    if status == "passed":
        flags["passed"] = 1
    elif status == "failed":
        flags["failed"] = 1
    elif status == "not_applicable":
        flags["notApplicable"] = 1
    elif status == "error":
        flags["isError"] = 1
        flags["failed"] = 1   # an errored check may also carry failed=1: it must not be double counted
    return {**flags, "category": category, "checkName": name, "cdmTableName": table,
            "cdmFieldName": field, "pctViolatedRows": pct, "numViolatedRows": 1, "thresholdValue": 0}


def test_not_applicable_checks_are_left_out_of_the_rate():
    data = {"CheckResults": [_check("passed")] * 3 + [_check("failed")] + [_check("not_applicable")] * 6}
    s, _ = dqd.summarize(data)
    assert (s["passed"], s["failed"], s["not_applicable"]) == (3, 1, 6)
    assert s["applicable"] == 4
    assert s["pass_rate"] == pytest.approx(0.75)


def test_an_error_is_counted_apart_and_not_as_a_failure():
    data = {"CheckResults": [_check("passed"), _check("error")]}
    s, failed = dqd.summarize(data)
    assert s["error"] == 1 and s["failed"] == 0
    assert s["pass_rate"] == pytest.approx(1.0)
    assert failed == []


def test_rate_is_undefined_when_nothing_is_applicable():
    s, _ = dqd.summarize({"CheckResults": [_check("not_applicable")]})
    assert s["pass_rate"] is None


def test_rate_by_category():
    data = {"CheckResults": [
        _check("passed", "Completeness"), _check("failed", "Completeness"),
        _check("passed", "Plausibility"), _check("not_applicable", "Plausibility"),
    ]}
    s, _ = dqd.summarize(data)
    assert s["completeness_rate"] == pytest.approx(0.5)
    assert s["plausibility_rate"] == pytest.approx(1.0)
    assert s["conformance_rate"] is None


def test_failed_checks_are_listed_with_their_context():
    data = {"CheckResults": [_check("failed", "Plausibility", "plausibleUnitConceptIds",
                                    "MEASUREMENT", "MEASUREMENT_CONCEPT_ID", 0.62)]}
    _, failed = dqd.summarize(data)
    assert failed == [{"category": "Plausibility", "check": "plausibleUnitConceptIds",
                       "table": "MEASUREMENT", "field": "MEASUREMENT_CONCEPT_ID",
                       "pct_violated_rows": 0.62, "num_violated_rows": 1, "threshold": 0}]


def test_viewer_percentage_is_reported_but_not_used():
    data = {"CheckResults": [_check("passed"), _check("failed"), _check("not_applicable")],
            "Overview": {"percentPassed": [66.67]}}
    s, _ = dqd.summarize(data)
    assert s["viewer_pct_passed"] == 66.67
    assert s["pass_rate"] == pytest.approx(0.5)


def test_aggregate_over_runs():
    agg = dqd.aggregate([0.9, 1.0, None])
    assert agg["n_runs"] == 2
    assert agg["mean"] == pytest.approx(0.95)
    assert agg["min"] == 0.9 and agg["max"] == 1.0
    assert dqd.aggregate([]) == {}


def test_cli_writes_the_two_csv_files(tmp_path):
    f = tmp_path / "run.json"
    f.write_text(json.dumps({"CheckResults": [_check("passed"), _check("failed")]}))
    out, failed = tmp_path / "s.csv", tmp_path / "f.csv"
    assert dqd.main([str(f), "--csv", str(out), "--failed-csv", str(failed), "--aggregate"]) == 0
    assert "pass_rate" in out.read_text().splitlines()[0]
    assert len(failed.read_text().splitlines()) == 2
