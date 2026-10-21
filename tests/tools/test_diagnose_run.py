"""Tests for the run diagnosis: it reads the JSON artefacts of a run and
reports what the known problems look like."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_script(name: str):
    path = Path(__file__).resolve().parents[2] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_script = _load_script("diagnose_run")
build_report, mapping_groups, warnings_for, main = (
    _script.build_report, _script.mapping_groups, _script.warnings_for, _script.main,
)


def _record(field, source_field, value, concept, reason="", table="visit_occurrence", source_table="Encounter"):
    return {"target_table": table, "target_field": field, "source_table": source_table,
            "source_field": source_field, "source_value": value, "target_concept_id": concept, "reason": reason}


CURATED = "Resolved via human-curated fixed mapping (takes priority over automatic search)"


def _write_run(runs_dir: Path, name: str, structural: list[dict], per_table: dict, extra_mapping: dict | None = None) -> Path:
    run = runs_dir / name
    (run / "mapping").mkdir(parents=True)
    (run / "loading_load_temp").mkdir()
    (run / "mapping" / "result.json").write_text(json.dumps(
        {"output": {"structural_target_mappings": structural, **(extra_mapping or {})}}), encoding="utf-8")
    (run / "loading_load_temp" / "result.json").write_text(json.dumps(
        {"output": {"per_table_result": per_table}}), encoding="utf-8")
    return run


@pytest.fixture
def healthy_run(tmp_path):
    structural = [_record("visit_concept_id", "class.code", v, c, CURATED)
                  for v, c in (("AMB", 9202), ("EMER", 9203), ("IMP", 9201))]
    return _write_run(tmp_path, "RUN-ok", structural, {"visit_occurrence": {"rows_loaded": 6000}, "person": {"rows_loaded": 114}})


@pytest.fixture
def erased_run(tmp_path):
    """The failure met on the FHIR batch: a curated group, then a second group
    from another column that resolved nothing, and every visit dropped."""
    structural = (
        [_record("visit_concept_id", "class.code", v, c, CURATED) for v, c in (("AMB", 9202), ("EMER", 9203))]
        + [_record("visit_concept_id", "type.code", v, None, "No candidate found in vocabulary 'Visit'")
           for v in ("185349003", "50849002", "32485007")]
    )
    per_table = {"visit_occurrence": {
        "rows_loaded": 0, "reason": "all rows dropped (missing required concept)",
        "dropped_missing_concept": {"dropped_rows": 6790, "reason": "visit_concept_id could not be resolved"},
    }}
    return _write_run(tmp_path, "RUN-erased", structural, per_table)


def test_mapping_groups_count_what_each_source_column_resolved():
    records = [_record("visit_concept_id", "class.code", "AMB", 9202, CURATED),
               _record("visit_concept_id", "class.code", "HH", None, "not covered")]
    group = mapping_groups(records, "visit_occurrence")[("visit_concept_id", "Encounter", "class.code")]
    assert (group["records"], group["resolved"], group["curated"]) == (2, 1, 1)
    assert group["unresolved_values"] == ["HH"]


def test_records_of_other_tables_and_without_a_source_are_ignored():
    records = [_record("person_id", "subject.id", None, None, table="person"),
               {"target_table": "visit_occurrence", "target_field": "visit_type_concept_id", "reason": "no source"}]
    assert mapping_groups(records, "visit_occurrence") == {}


def test_a_healthy_run_raises_no_warning(healthy_run):
    text = "\n".join(build_report(healthy_run, "visit_occurrence"))
    assert "None of the known problems was detected" in text
    assert "visit_occurrence: 6000 rows" in text and "person: 114 rows" in text


def test_the_erased_concept_failure_is_recognised(erased_run):
    text = "\n".join(build_report(erased_run, "visit_occurrence"))
    assert "2 different source columns" in text and "Encounter.class.code" in text and "Encounter.type.code" in text
    assert "the last one erases the others" in text


def test_dropped_rows_are_reported_with_their_count(erased_run):
    text = "\n".join(build_report(erased_run, "visit_occurrence"))
    assert "6790 rows of visit_occurrence were dropped (dropped_missing_concept)" in text


def test_a_field_with_nothing_resolved_is_flagged():
    groups = mapping_groups([_record("visit_concept_id", "class.code", "AMB", None, "no match")], "visit_occurrence")
    assert any("none of its 1 values was resolved" in w for w in warnings_for("visit_occurrence", groups, None))


def test_the_curated_and_automatic_resolutions_are_told_apart(erased_run):
    lines = build_report(erased_run, "visit_occurrence")
    curated_row = next(l for l in lines if "class.code" in l and l.startswith("|"))
    automatic_row = next(l for l in lines if "type.code" in l and l.startswith("|"))
    assert "| 2 | 2 | 2 |" in curated_row            # records, resolved, curated
    assert "| 3 | 0 | 0 |" in automatic_row


def test_the_unresolved_values_are_listed(erased_run):
    row = next(l for l in build_report(erased_run, "visit_occurrence") if "type.code" in l and l.startswith("|"))
    assert "185349003" in row


def test_the_derivation_log_of_a_fhir_batch_is_shown(tmp_path):
    extra = {"fhir_derived_fixed_mappings": [
        {"target_table": "visit_occurrence", "target_field": "visit_concept_id", "status": "derived", "values_not_covered": ["HH", "VR"]}]}
    run = _write_run(tmp_path, "RUN-fhir", [], {}, extra)
    text = "\n".join(build_report(run, "visit_occurrence"))
    assert "visit_occurrence.visit_concept_id: derived - not covered: ['HH', 'VR']" in text


def test_a_run_without_artefacts_is_reported_not_crashed(tmp_path):
    (tmp_path / "RUN-empty").mkdir()
    text = "\n".join(build_report(tmp_path / "RUN-empty", "visit_occurrence"))
    assert "No loading result found" in text and "No mapping result found" in text


def test_the_command_line_reports_an_unknown_run(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["diagnose_run", "RUN-nope", "--runs-dir", str(tmp_path)])
    assert main() == 1
    assert "No run folder" in capsys.readouterr().out


def test_the_command_line_prints_the_report(healthy_run, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["diagnose_run", "RUN-ok", "--runs-dir", str(healthy_run.parent)])
    assert main() == 0
    assert "# RUN-ok - table visit_occurrence" in capsys.readouterr().out
