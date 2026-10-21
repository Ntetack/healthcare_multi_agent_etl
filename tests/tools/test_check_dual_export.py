"""Tests for the source-level check of a CSV export against a FHIR export."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from app.tools.data.source_loader import load_source_tables

import importlib.util


def _load_script(name: str):
    """Loads scripts/<name>.py by its path: the tests then do not depend on
    how pytest names packages or on what is on sys.path."""
    path = Path(__file__).resolve().parents[2] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_script = _load_script("check_dual_export")
build_report, compare_patients, count_entities, main = (
    _script.build_report, _script.compare_patients, _script.count_entities, _script.main
)

FIXTURE = Path(__file__).parent.parent / "fixtures" / "fhir" / "synthea_r4_sample_bundle.json"


def _resources() -> list[dict]:
    return [e["resource"] for e in json.loads(FIXTURE.read_text(encoding="utf-8"))["entry"]]


def _write_csv(folder: Path, name: str, n_rows: int, **columns) -> None:
    data = {"Id": [f"row{i}" for i in range(n_rows)], **{k: [v] * n_rows for k, v in columns.items()}}
    pd.DataFrame(data).to_csv(folder / name, index=False)


@pytest.fixture
def exports(tmp_path):
    """A FHIR folder holding the sample bundle and a CSV folder that describes
    exactly the same records, the way Synthea would."""
    fhir_dir, csv_dir = tmp_path / "fhir", tmp_path / "csv"
    fhir_dir.mkdir(); csv_dir.mkdir()
    shutil.copy(FIXTURE, fhir_dir / "patient_Bundle.json")

    resources = _resources()
    patient_id = next(r["id"] for r in resources if r["resourceType"] == "Patient")
    pd.DataFrame({"Id": [patient_id]}).to_csv(csv_dir / "patients.csv", index=False)
    count = lambda t: sum(1 for r in resources if r["resourceType"] == t)
    components = sum(len(r.get("component", [])) for r in resources if r["resourceType"] == "Observation")
    panels = sum(1 for r in resources if r["resourceType"] == "Observation" and r.get("component"))
    _write_csv(csv_dir, "conditions.csv", count("Condition"))
    _write_csv(csv_dir, "encounters.csv", count("Encounter"))
    _write_csv(csv_dir, "medications.csv", count("MedicationRequest"))
    _write_csv(csv_dir, "immunizations.csv", count("Immunization"))
    _write_csv(csv_dir, "procedures.csv", count("Procedure"))
    _write_csv(csv_dir, "observations.csv", count("Observation") - panels + components)
    return csv_dir, fhir_dir


def _by_entity(rows: list[dict]) -> dict:
    return {r["entity"]: r for r in rows}


def test_compare_patients_detects_a_difference_in_either_direction():
    result = compare_patients({"a", "b", "c"}, {"b", "c", "d"})
    assert not result["same"]
    assert result["only_in_csv"] == ["a"] and result["only_in_fhir"] == ["d"]
    assert compare_patients({"a"}, {"a"})["same"]


def test_matching_exports_have_no_difference_in_the_comparable_entities(exports):
    csv_dir, fhir_dir = exports
    rows = _by_entity(count_entities(csv_dir, load_source_tables("fhir", fhir_dir)))
    for entity in ("conditions.csv / Condition", "encounters.csv / Encounter",
                   "medications.csv / MedicationRequest", "immunizations.csv / Immunization",
                   "procedures.csv / Procedure"):
        assert rows[entity]["difference"] == 0, entity


def test_observations_match_once_panels_are_replaced_by_their_components(exports):
    csv_dir, fhir_dir = exports
    rows = _by_entity(count_entities(csv_dir, load_source_tables("fhir", fhir_dir)))
    assert rows["observations.csv / Observation without its panels, plus components"]["difference"] == 0
    assert rows["observations.csv / Observation (all rows)"]["difference"] != 0      # the naive count does not


def test_a_missing_csv_file_is_reported_as_missing_not_as_zero(exports):
    csv_dir, fhir_dir = exports
    (csv_dir / "immunizations.csv").unlink()
    row = _by_entity(count_entities(csv_dir, load_source_tables("fhir", fhir_dir)))["immunizations.csv / Immunization"]
    assert row["csv"] is None and row["difference"] is None


def test_a_resource_type_absent_from_the_fhir_export_is_reported_as_missing(exports):
    csv_dir, fhir_dir = exports
    row = _by_entity(count_entities(csv_dir, load_source_tables("fhir", fhir_dir)))["allergies.csv / AllergyIntolerance"]
    assert row["fhir"] is None and row["difference"] is None


def test_the_report_states_that_the_patients_are_the_same(exports):
    lines, same = build_report(*exports)
    assert same
    assert any("describe the same patients" in line for line in lines)


def test_the_report_flags_exports_that_come_from_different_runs(exports):
    csv_dir, fhir_dir = exports
    pd.DataFrame({"Id": ["another-patient"]}).to_csv(csv_dir / "patients.csv", index=False)
    lines, same = build_report(csv_dir, fhir_dir)
    assert not same
    assert any("do NOT describe the same patients" in line for line in lines)


def test_the_exit_code_reflects_the_patient_check(exports, monkeypatch, capsys):
    csv_dir, fhir_dir = exports
    monkeypatch.setattr("sys.argv", ["check_dual_export", "--csv-dir", str(csv_dir), "--fhir-dir", str(fhir_dir)])
    assert main() == 0
    pd.DataFrame({"Id": ["another-patient"]}).to_csv(csv_dir / "patients.csv", index=False)
    assert main() == 1


def test_a_csv_folder_without_patients_is_an_explicit_error(tmp_path):
    (tmp_path / "csv").mkdir(); (tmp_path / "fhir").mkdir()
    with pytest.raises(FileNotFoundError):
        build_report(tmp_path / "csv", tmp_path / "fhir")


# ------------------------------------------------- observations, code by code

compare_observation_codes = _script.compare_observation_codes
observation_detail_lines = _script.observation_detail_lines


def _csv_observation_rows(resources: list[dict]) -> pd.DataFrame:
    """The rows Synthea would write for the observations of the sample: each
    standalone observation, and each component of a panel (not the panel)."""
    rows = []
    for r in resources:
        if r["resourceType"] != "Observation":
            continue
        if r.get("component"):
            for c in r["component"]:
                coding = c["code"]["coding"][0]
                rows.append({"CODE": coding["code"], "DESCRIPTION": coding.get("display", "")})
        else:
            coding = r["code"]["coding"][0]
            rows.append({"CODE": coding["code"], "DESCRIPTION": coding.get("display", "")})
    return pd.DataFrame(rows)


@pytest.fixture
def fhir_tables(tmp_path):
    shutil.copy(FIXTURE, tmp_path / "patient_Bundle.json")
    return load_source_tables("fhir", tmp_path)


def test_codes_match_when_the_csv_describes_the_same_observations(fhir_tables):
    detail = compare_observation_codes(_csv_observation_rows(_resources()), fhir_tables)
    assert (detail["unexplained"] == 0).all()
    assert detail["csv"].sum() == 4                        # two standalone observations + two components


def test_extra_csv_rows_for_a_code_are_attributed_to_that_code(fhir_tables):
    csv = pd.concat([
        _csv_observation_rows(_resources()),
        pd.DataFrame([{"CODE": "X-1", "DESCRIPTION": "Extra observation"}] * 3),
    ], ignore_index=True)
    detail = compare_observation_codes(csv, fhir_tables).set_index("code")
    assert detail.loc["X-1", "unexplained"] == 3
    assert detail.loc["X-1", "description"] == "Extra observation"
    assert detail["unexplained"].drop("X-1").eq(0).all()


def test_a_panel_row_in_the_csv_is_recognised_as_a_panel(fhir_tables):
    panel_code = next(
        r["code"]["coding"][0]["code"] for r in _resources() if r["resourceType"] == "Observation" and r.get("component")
    )
    csv = pd.concat([_csv_observation_rows(_resources()),
                     pd.DataFrame([{"CODE": panel_code, "DESCRIPTION": "Panel"}])], ignore_index=True)
    detail = compare_observation_codes(csv, fhir_tables).set_index("code")
    assert detail.loc[panel_code, "unexplained"] == 1
    assert detail.loc[panel_code, "fhir_panels"] == 1
    assert detail.loc[panel_code, "unexplained_if_panels_counted"] == 0


def test_a_code_present_only_in_fhir_gives_a_negative_difference(fhir_tables):
    csv = _csv_observation_rows(_resources()).iloc[1:]       # one CSV row less
    detail = compare_observation_codes(csv, fhir_tables)
    assert detail["unexplained"].sum() == -1


def test_the_detail_lines_summarise_and_rank_the_differences(fhir_tables):
    csv = pd.concat([
        _csv_observation_rows(_resources()),
        pd.DataFrame([{"CODE": "BIG", "DESCRIPTION": "Large gap"}] * 5 + [{"CODE": "SMALL", "DESCRIPTION": "Small gap"}]),
    ], ignore_index=True)
    text = "\n".join(observation_detail_lines(compare_observation_codes(csv, fhir_tables), top=1))
    assert "codes whose counts differ: 2" in text
    assert "+6" in text                                      # 5 + 1 rows beyond the FHIR export
    assert "BIG" in text and "SMALL" not in text             # only the top one is listed


def test_the_detail_says_so_when_every_code_matches(fhir_tables):
    text = "\n".join(observation_detail_lines(compare_observation_codes(_csv_observation_rows(_resources()), fhir_tables), 5))
    assert "Every code has the same count in both exports" in text


def test_the_detail_is_unavailable_without_a_code_column(fhir_tables):
    detail = compare_observation_codes(pd.DataFrame({"Id": ["1"]}), fhir_tables)
    assert detail.empty
    assert "Not available" in "\n".join(observation_detail_lines(detail, 5))


def test_the_report_includes_the_detail_only_when_asked(exports):
    csv_dir, fhir_dir = exports
    _csv_observation_rows(_resources()).to_csv(csv_dir / "observations.csv", index=False)
    plain, _ = build_report(csv_dir, fhir_dir)
    detailed, _ = build_report(csv_dir, fhir_dir, observations_detail=True)
    assert not any("code by code" in line for line in plain)
    assert any("Observations, code by code" in line for line in detailed)


# ------------------------------------------------------------ known exclusions

read_observations = _script.read_observations


def _csv_with_health_metrics(resources: list[dict]) -> pd.DataFrame:
    """The sample's observations plus rows of codes that exist only in the CSV
    export, as the non-clinical metrics of a simulator would."""
    extra = [{"CODE": code, "DESCRIPTION": code} for code in ("DALY", "QALY", "QOLS") for _ in range(4)]
    return pd.concat([_csv_observation_rows(resources), pd.DataFrame(extra)], ignore_index=True)


def test_read_observations_leaves_out_the_given_codes_and_counts_them(exports):
    csv_dir, _ = exports
    _csv_with_health_metrics(_resources()).to_csv(csv_dir / "observations.csv", index=False)
    kept, n_ignored = read_observations(csv_dir, ("DALY", "QALY", "QOLS"))
    assert n_ignored == 12
    assert not kept["CODE"].isin(["DALY", "QALY", "QOLS"]).any()
    assert len(kept) == 4


def test_without_ignored_codes_nothing_is_left_out(exports):
    csv_dir, _ = exports
    _csv_with_health_metrics(_resources()).to_csv(csv_dir / "observations.csv", index=False)
    kept, n_ignored = read_observations(csv_dir)
    assert n_ignored == 0 and len(kept) == 16


def test_ignoring_the_extra_codes_brings_the_observation_difference_to_zero(exports):
    csv_dir, fhir_dir = exports
    _csv_with_health_metrics(_resources()).to_csv(csv_dir / "observations.csv", index=False)
    tables = load_source_tables("fhir", fhir_dir)
    with_extra = _by_entity(count_entities(csv_dir, tables))
    without = _by_entity(count_entities(csv_dir, tables, ("DALY", "QALY", "QOLS")))
    key = "observations.csv / Observation without its panels, plus components"
    assert with_extra[key]["difference"] == 12
    assert without[key]["difference"] == 0


def test_the_report_states_what_was_left_out(exports):
    csv_dir, fhir_dir = exports
    _csv_with_health_metrics(_resources()).to_csv(csv_dir / "observations.csv", index=False)
    lines, _ = build_report(csv_dir, fhir_dir, observations_detail=True, ignore_codes=("DALY", "QALY", "QOLS"))
    text = "\n".join(lines)
    assert "left out of the observation counts" in text and ": 12." in text
    assert "Every code has the same count in both exports" in text


def test_the_report_without_the_option_does_not_mention_an_exclusion(exports):
    csv_dir, fhir_dir = exports
    lines, _ = build_report(csv_dir, fhir_dir)
    assert not any("left out" in line for line in lines)


def test_the_command_line_accepts_a_list_of_codes(exports, monkeypatch, capsys):
    csv_dir, fhir_dir = exports
    _csv_with_health_metrics(_resources()).to_csv(csv_dir / "observations.csv", index=False)
    monkeypatch.setattr("sys.argv", ["check_dual_export", "--csv-dir", str(csv_dir), "--fhir-dir", str(fhir_dir),
                                     "--ignore-codes", "DALY, QALY ,QOLS"])
    assert main() == 0
    assert ": 12." in capsys.readouterr().out
