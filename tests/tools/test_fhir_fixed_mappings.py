"""Tests for the curated mappings shared by every FHIR source."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from app.tools.data.fhir_fixed_mappings import (
    MAPPING_FOLDER,
    derive_fhir_fixed_mappings,
    load_fhir_fixed_mapping_reference,
)
from app.tools.data.fhir_flattener import build_fhir_tables
from app.tools.mapping.fixed_value_mappings import (
    get_fixed_mapping_spec,
    load_fixed_mapping_table,
    resolve_fixed_value,
)

FIXTURE = Path(__file__).parent.parent / "fixtures" / "fhir" / "synthea_r4_sample_bundle.json"


def _sample_tables() -> dict[str, pd.DataFrame]:
    bundle = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return build_fhir_tables([("bundle.json", [e["resource"] for e in bundle["entry"]])])


def _empty_cfg() -> dict:
    return {"format": "fhir", "tables": {}, "type_concepts": {}}


# ------------------------------------------------------------- the reference

def test_the_reference_covers_race_ethnicity_and_visit():
    reference = load_fhir_fixed_mapping_reference()
    assert set(reference["person"]) == {"race_concept_id", "ethnicity_concept_id"}
    assert set(reference["visit_occurrence"]) == {"visit_concept_id"}


def test_every_entry_is_complete_and_points_to_an_existing_file():
    for target_table, fields in load_fhir_fixed_mapping_reference().items():
        for target_field, spec in fields.items():
            for key in ("source_table", "source_field", "mapping_file", "mapping_column"):
                assert spec.get(key), f"{target_table}.{target_field} lacks '{key}'"
            assert (MAPPING_FOLDER / spec["mapping_file"]).exists(), spec["mapping_file"]


def test_every_csv_has_its_key_and_value_columns_and_integer_concepts():
    for fields in load_fhir_fixed_mapping_reference().values():
        for spec in fields.values():
            table = pd.read_csv(MAPPING_FOLDER / spec["mapping_file"], dtype=str)
            columns = {c.lower() for c in table.columns}
            assert spec.get("source_field_column", spec["source_field"]).lower() in columns
            assert spec["mapping_column"].lower() in columns
            assert table[spec["mapping_column"]].str.fullmatch(r"\d+").all(), spec["mapping_file"]
            assert table[spec.get("source_field_column", spec["source_field"])].is_unique


def test_a_missing_reference_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_fhir_fixed_mapping_reference(tmp_path / "nope.yaml")


# ------------------------------------------------------------- the derivation

def test_the_three_mappings_are_derived_for_the_sample():
    cfg, log = derive_fhir_fixed_mappings(_sample_tables(), _empty_cfg())
    derived = cfg["fixed_value_mappings"]
    assert set(derived["person"]) == {"race_concept_id", "ethnicity_concept_id"}
    assert set(derived["visit_occurrence"]) == {"visit_concept_id"}
    assert {e["status"] for e in log} == {"derived"}


def test_a_derived_entry_points_to_the_real_table_name_and_an_absolute_file():
    derived = derive_fhir_fixed_mappings(_sample_tables(), _empty_cfg())[0]["fixed_value_mappings"]
    race = derived["person"]["race_concept_id"]
    assert race["source_table"] == "Patient"
    assert Path(race["mapping_file"]).is_absolute() and Path(race["mapping_file"]).exists()
    assert derived["visit_occurrence"]["visit_concept_id"]["source_table"] == "Encounter"


def test_every_value_of_the_sample_is_covered():
    _, log = derive_fhir_fixed_mappings(_sample_tables(), _empty_cfg())
    assert all(e["values_not_covered"] == [] for e in log)
    found = {e["target_field"]: e["values_found"] for e in log}
    assert found["visit_concept_id"] == ["AMB", "EMER", "IMP"]
    assert found["race_concept_id"] == ["2106-3"]
    assert found["ethnicity_concept_id"] == ["2186-5"]


def test_a_value_the_file_does_not_cover_is_reported():
    tables = _sample_tables()
    patient = tables["Patient"].copy()
    other = patient.iloc[[0]].copy()
    other["extension.us-core-race.ombCategory.code"] = "2131-1"          # "Other Race", deliberately absent
    tables["Patient"] = pd.concat([patient, other], ignore_index=True)
    _, log = derive_fhir_fixed_mappings(tables, _empty_cfg())
    race = next(e for e in log if e["target_field"] == "race_concept_id")
    assert race["values_not_covered"] == ["2131-1"]


def test_a_declaration_written_by_hand_takes_precedence():
    own = {"source_table": "Patient", "source_field": "gender", "mapping_file": "own.csv", "mapping_column": "x"}
    cfg_in = {**_empty_cfg(), "fixed_value_mappings": {"person": {"race_concept_id": own}}}
    cfg, log = derive_fhir_fixed_mappings(_sample_tables(), cfg_in)
    assert cfg["fixed_value_mappings"]["person"]["race_concept_id"] == own
    entry = next(e for e in log if e["target_field"] == "race_concept_id")
    assert entry["status"] == "kept the declaration written by hand"
    assert "ethnicity_concept_id" in cfg["fixed_value_mappings"]["person"]


def test_nothing_is_derived_when_the_source_column_is_absent():
    tables = _sample_tables()
    tables["Patient"] = tables["Patient"][["id", "gender", "birthDate", "_source_file"]]
    cfg, log = derive_fhir_fixed_mappings(tables, _empty_cfg())
    assert "person" not in cfg["fixed_value_mappings"]
    statuses = {e["target_field"]: e["status"] for e in log}
    assert statuses["race_concept_id"] == "skipped: source column not present in this batch"
    assert statuses["visit_concept_id"] == "derived"


def test_nothing_is_derived_when_the_column_holds_no_value():
    tables = _sample_tables()
    tables["Patient"] = tables["Patient"].copy()
    tables["Patient"]["extension.us-core-race.ombCategory.code"] = ""
    _, log = derive_fhir_fixed_mappings(tables, _empty_cfg())
    race = next(e for e in log if e["target_field"] == "race_concept_id")
    assert race["status"] == "skipped: the source column holds no value"


def test_the_original_configuration_is_not_modified():
    cfg_in = _empty_cfg()
    derive_fhir_fixed_mappings(_sample_tables(), cfg_in)
    assert "fixed_value_mappings" not in cfg_in


# ------------------- resolution with the project's own fixed mapping functions

@pytest.mark.parametrize(
    "target_table, target_field, raw, expected",
    [
        ("person", "race_concept_id", "2106-3", 8527),
        ("person", "race_concept_id", "2054-5", 8516),
        ("person", "race_concept_id", "2028-9", 8515),
        ("person", "race_concept_id", "1002-5", 8657),
        ("person", "race_concept_id", "2076-8", 8557),
        ("person", "ethnicity_concept_id", "2186-5", 38003564),
        ("person", "ethnicity_concept_id", "2135-2", 38003563),
        ("visit_occurrence", "visit_concept_id", "AMB", 9202),
        ("visit_occurrence", "visit_concept_id", "EMER", 9203),
        ("visit_occurrence", "visit_concept_id", "IMP", 9201),
        ("visit_occurrence", "visit_concept_id", "amb", 9202),           # case is ignored
    ],
)
def test_a_derived_entry_resolves_through_the_curated_mapping_functions(target_table, target_field, raw, expected):
    cfg, _ = derive_fhir_fixed_mappings(_sample_tables(), _empty_cfg())
    spec = get_fixed_mapping_spec(cfg, target_table, target_field)
    # The source folder does not exist: the absolute path of the entry must win over it.
    table = load_fixed_mapping_table(Path("/folder/of/a/source/that/does/not/exist"), spec)
    assert table is not None
    assert resolve_fixed_value(raw, table, spec)["concept_id"] == expected


def test_a_value_outside_the_file_falls_through_to_the_automatic_resolution():
    cfg, _ = derive_fhir_fixed_mappings(_sample_tables(), _empty_cfg())
    spec = get_fixed_mapping_spec(cfg, "visit_occurrence", "visit_concept_id")
    table = load_fixed_mapping_table(Path("/anywhere"), spec)
    assert resolve_fixed_value("HH", table, spec) is None
