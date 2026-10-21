"""Tests for the FHIR flattener and for its use by load_source_tables().

The sample bundle is a trimmed Synthea R4 export (13 resources of 7 types)
kept in tests/fixtures/fhir/. It contains a Patient with US Core race and
ethnicity extensions, one encounter of each class (AMB, EMER, IMP), an
observation with a direct value, a blood pressure panel with components,
and an observation with a coded value.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from app.tools.data.fhir_flattener import (
    MAX_COLUMN_NAME_LENGTH,
    build_fhir_tables,
    flatten_resource,
    normalize_reference,
)
from app.tools.data.source_loader import load_source_tables

FIXTURE = Path(__file__).parent.parent / "fixtures" / "fhir" / "synthea_r4_sample_bundle.json"


def _resources() -> list[dict]:
    bundle = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return [entry["resource"] for entry in bundle["entry"]]


# ---------------------------------------------------------------- references

@pytest.mark.parametrize(
    "reference, expected",
    [
        ("urn:uuid:abc-123", {"id": "abc-123"}),
        ("Patient/123", {"id": "123"}),
        ("http://example.org/fhir/Patient/123", {"id": "123"}),
        ("http://example.org/fhir/Patient/123/_history/2", {"id": "123"}),
        ("#contained1", {"id": "contained1"}),
        ("Practitioner?identifier=http://hl7.org/fhir/sid/us-npi|9999956292", {"identifier": "9999956292"}),
        ("Organization?identifier=abc", {"identifier": "abc"}),
        ("Location?name=somewhere", {}),
        ("", {}),
    ],
)
def test_normalize_reference_forms(reference, expected):
    assert normalize_reference(reference) == expected


def test_reference_yields_raw_text_and_resolved_id():
    row = flatten_resource({
        "resourceType": "Condition", "id": "c1",
        "subject": {"reference": "urn:uuid:p1", "display": "Ann"},
    })
    assert row["subject.reference"] == "urn:uuid:p1"
    assert row["subject.id"] == "p1"
    assert row["subject.display"] == "Ann"


def test_conditional_reference_yields_identifier_not_id():
    row = flatten_resource({
        "resourceType": "Encounter", "id": "e1",
        "serviceProvider": {"reference": "Organization?identifier=https://example.org|org-1"},
    })
    assert row["serviceProvider.identifier"] == "org-1"
    assert "serviceProvider.id" not in row


# ------------------------------------------------------------------- codings

def test_codeable_concept_is_lifted_to_its_parent_path():
    row = flatten_resource({
        "resourceType": "Condition", "id": "c1",
        "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes"}],
                 "text": "Diabetes"},
    })
    assert row["code.system"] == "http://snomed.info/sct"
    assert row["code.code"] == "44054006"
    assert row["code.display"] == "Diabetes"
    assert row["code.text"] == "Diabetes"
    assert "code.coding.json_all" not in row


def test_several_codings_prefer_a_known_system_and_keep_all_as_json():
    resource = {
        "resourceType": "Condition", "id": "c1",
        "code": {"coding": [
            {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11"},
            {"system": "http://snomed.info/sct", "code": "44054006"},
        ]},
    }
    preferred = flatten_resource(resource, known_systems={"http://snomed.info/sct"})
    assert preferred["code.code"] == "44054006"
    assert len(json.loads(preferred["code.coding.json_all"])) == 2

    default = flatten_resource(resource)
    assert default["code.code"] == "E11"


# -------------------------------------------------------------------- arrays

def test_arrays_keep_first_element_and_json_all_only_when_needed():
    row = flatten_resource({
        "resourceType": "Patient", "id": "p1",
        "name": [{"family": "Smith", "given": ["Ann", "Marie"]}],
        "telecom": [{"value": "111"}, {"value": "222"}],
    })
    assert row["name.family"] == "Smith"
    assert row["name.given"] == "Ann"
    assert json.loads(row["name.given.json_all"]) == ["Ann", "Marie"]
    assert "name.json_all" not in row          # a single name: nothing to keep apart
    assert row["telecom.value"] == "111"
    assert len(json.loads(row["telecom.json_all"])) == 2


# ---------------------------------------------------------------- extensions

def test_extensions_are_named_after_their_url_and_coded_values_are_lifted():
    row = flatten_resource({
        "resourceType": "Patient", "id": "p1",
        "extension": [
            {"url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race", "extension": [
                {"url": "ombCategory", "valueCoding": {
                    "system": "urn:oid:2.16.840.1.113883.6.238", "code": "2106-3", "display": "White"}},
                {"url": "text", "valueString": "White"},
            ]},
            {"url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex", "valueCode": "F"},
        ],
    })
    assert row["extension.us-core-race.ombCategory.code"] == "2106-3"
    assert row["extension.us-core-race.ombCategory.system"] == "urn:oid:2.16.840.1.113883.6.238"
    assert row["extension.us-core-race.text.valueString"] == "White"
    assert row["extension.us-core-birthsex.valueCode"] == "F"


def test_repeated_extension_keeps_the_first_and_the_whole_list_as_json():
    row = flatten_resource({
        "resourceType": "Patient", "id": "p1",
        "extension": [
            {"url": "http://example.org/ext-a", "valueString": "first"},
            {"url": "http://example.org/ext-a", "valueString": "second"},
        ],
    })
    assert row["extension.ext-a.valueString"] == "first"
    assert len(json.loads(row["extension.json_all"])) == 2


# ----------------------------------------------------------- values and names

def test_booleans_and_numbers_become_strings():
    row = flatten_resource({
        "resourceType": "Patient", "id": "p1",
        "multipleBirthBoolean": False,
        "valueQuantity": {"value": 82, "unit": "mm[Hg]"},
    })
    assert row["multipleBirthBoolean"] == "false"
    assert row["valueQuantity.value"] == "82"


def test_narrative_and_meta_are_dropped():
    row = flatten_resource({
        "resourceType": "Patient", "id": "p1",
        "meta": {"profile": ["http://example.org/profile"]},
        "text": {"status": "generated", "div": "<div>narrative</div>"},
        "gender": "female",
    })
    assert set(row) == {"id", "gender"}


def test_long_paths_are_capped_deterministically_and_never_merged():
    deep = {"a" * 30: {"b" * 30: {"c" * 30: "x"}}}
    other = {"a" * 30: {"b" * 30: {"d" * 30: "y"}}}
    row = flatten_resource({"resourceType": "T", "id": "1", **deep})
    row_other = flatten_resource({"resourceType": "T", "id": "1", **other})
    name = next(k for k in row if k != "id")
    name_other = next(k for k in row_other if k != "id")
    assert len(name) <= MAX_COLUMN_NAME_LENGTH
    assert name != name_other
    assert name == next(k for k in flatten_resource({"resourceType": "T", "id": "1", **deep}) if k != "id")


# ------------------------------------------------------------ table building

def test_tables_follow_the_csv_conventions():
    tables = build_fhir_tables([("bundle.json", _resources())])
    assert set(tables) == {
        "Patient", "Encounter", "Condition", "Observation", "Observation_component",
        "Procedure", "MedicationRequest", "Immunization",
    }
    for name, df in tables.items():
        assert df.columns[0] == "id", name
        assert df.columns[-1] == "_source_file", name
        assert (df.dtypes == object).all() or all(str(t) in ("object", "str", "string") for t in df.dtypes), name
        assert not df.isna().any().any(), name          # missing values are empty strings
        assert (df["_source_file"] == "bundle.json").all(), name
        assert all(len(c) <= MAX_COLUMN_NAME_LENGTH for c in df.columns), name


def test_references_join_the_tables_deterministically():
    tables = build_fhir_tables([("bundle.json", _resources())])
    patient_ids = set(tables["Patient"]["id"])
    encounter_ids = set(tables["Encounter"]["id"])
    for table, column in [("Condition", "subject.id"), ("Observation", "subject.id"),
                          ("Procedure", "subject.id"), ("MedicationRequest", "subject.id"),
                          ("Immunization", "patient.id")]:
        assert tables[table][column].isin(patient_ids).all(), f"{table}.{column}"
    assert tables["Condition"]["encounter.id"].isin(encounter_ids | {""}).all()


def test_the_sample_patient_carries_race_ethnicity_and_gender():
    patient = build_fhir_tables([("bundle.json", _resources())])["Patient"].iloc[0]
    assert patient["extension.us-core-race.ombCategory.code"] == "2106-3"
    assert patient["extension.us-core-ethnicity.ombCategory.code"] == "2186-5"
    assert patient["gender"] == "female"
    assert patient["birthDate"] == "1990-01-24"


def test_encounter_class_and_period_are_available():
    encounters = build_fhir_tables([("bundle.json", _resources())])["Encounter"]
    assert set(encounters["class.code"]) == {"AMB", "EMER", "IMP"}
    assert (encounters["period.start"] != "").all()


# ------------------------------------------- the three layouts of a FHIR batch

def test_load_source_tables_reads_a_synthea_bundle_per_patient(tmp_path):
    shutil.copy(FIXTURE, tmp_path / "patient1_Bundle.json")
    tables = load_source_tables("fhir", tmp_path)
    assert set(tables) == {"Patient", "Encounter", "Condition", "Observation", "Observation_component",
                           "Procedure", "MedicationRequest", "Immunization"}
    assert "code.code" in tables["Condition"].columns
    assert (tables["Condition"]["_source_file"] == "patient1_Bundle.json").all()


def test_load_source_tables_reads_bulk_ndjson(tmp_path):
    lines = [json.dumps(r) for r in _resources() if r["resourceType"] in ("Condition", "Observation")]
    (tmp_path / "export.ndjson").write_text("\n".join(lines), encoding="utf-8")
    tables = load_source_tables("fhir", tmp_path)
    assert set(tables) == {"Condition", "Observation", "Observation_component"}
    assert len(tables["Condition"]) == 2


def test_load_source_tables_reads_a_standalone_resource(tmp_path):
    patient = next(r for r in _resources() if r["resourceType"] == "Patient")
    (tmp_path / "one_resource.json").write_text(json.dumps(patient, indent=2), encoding="utf-8")
    tables = load_source_tables("fhir", tmp_path)
    assert set(tables) == {"Patient"}
    assert tables["Patient"].iloc[0]["gender"] == "female"


def test_several_bundles_are_merged_by_resource_type(tmp_path):
    shutil.copy(FIXTURE, tmp_path / "patient1_Bundle.json")
    shutil.copy(FIXTURE, tmp_path / "patient2_Bundle.json")
    tables = load_source_tables("fhir", tmp_path)
    assert len(tables["Patient"]) == 2
    assert set(tables["Patient"]["_source_file"]) == {"patient1_Bundle.json", "patient2_Bundle.json"}


# -------------------------------------------------------------- child tables

def _observation_with_components() -> dict:
    return next(r for r in _resources() if r["resourceType"] == "Observation" and r.get("component"))


def test_every_component_becomes_a_child_row():
    resources = _resources()
    expected = sum(len(r.get("component", [])) for r in resources if r["resourceType"] == "Observation")
    tables = build_fhir_tables([("bundle.json", resources)])
    assert expected == 2
    assert len(tables["Observation_component"]) == expected


def test_the_parent_table_no_longer_holds_the_component_columns():
    observation = build_fhir_tables([("bundle.json", _resources())])["Observation"]
    assert not [c for c in observation.columns if c.startswith("component")]
    assert len(observation) == 3          # the panel itself is kept as a row


def test_a_child_row_carries_its_own_code_and_value():
    child = build_fhir_tables([("bundle.json", _resources())])["Observation_component"]
    systolic = child[child["code.code"] == "8480-6"].iloc[0]
    assert systolic["code.system"] == "http://loinc.org"
    assert systolic["valueQuantity.unit"] == "mm[Hg]"
    assert systolic["valueQuantity.value"] != ""


def test_a_child_row_inherits_the_context_of_its_parent():
    parent = _observation_with_components()
    child = build_fhir_tables([("bundle.json", _resources())])["Observation_component"]
    row = child.iloc[0]
    assert row["parent.id"] == parent["id"]
    assert row["parent.status"] == parent["status"]
    assert row["parent.subject.id"] == parent["subject"]["reference"].split(":")[-1]
    assert row["parent.encounter.id"] == parent["encounter"]["reference"].split(":")[-1]
    assert row["parent.effectiveDateTime"] == parent["effectiveDateTime"]
    assert "parent.code.code" not in child.columns       # only context is inherited


def test_child_ids_are_unique_and_follow_the_parent_id():
    parent = _observation_with_components()
    child = build_fhir_tables([("bundle.json", _resources())])["Observation_component"]
    assert child["id"].is_unique
    assert list(child["id"]) == [f"{parent['id']}#0", f"{parent['id']}#1"]


def test_no_child_table_when_there_is_no_component():
    resources = [r for r in _resources() if not r.get("component")]
    assert "Observation_component" not in build_fhir_tables([("bundle.json", resources)])


def test_a_coded_value_inside_a_component_is_lifted():
    resource = {
        "resourceType": "Observation", "id": "o1", "status": "final",
        "subject": {"reference": "urn:uuid:p1"},
        "effectiveDateTime": "2020-01-01T00:00:00Z",
        "component": [{
            "code": {"coding": [{"system": "http://loinc.org", "code": "Q1"}]},
            "valueCodeableConcept": {"coding": [{"system": "http://loinc.org", "code": "LA1", "display": "Yes"}]},
        }],
    }
    child = build_fhir_tables([("o.json", [resource])])["Observation_component"].iloc[0]
    assert child["valueCodeableConcept.code"] == "LA1"
    assert child["valueCodeableConcept.display"] == "Yes"


def test_only_context_is_inherited_dates_included():
    resource = {
        "resourceType": "Observation", "id": "o1", "status": "final",
        "subject": {"reference": "Patient/p1"},
        "effectivePeriod": {"start": "2020-03-04T10:00:00Z", "end": "2020-03-04"},
        "valueString": "2020",          # looks like a year but is not a date
        "component": [{"code": {"coding": [{"code": "c"}]}, "valueString": "x"}],
    }
    child = build_fhir_tables([("o.json", [resource])])["Observation_component"].iloc[0]
    assert child["parent.effectivePeriod.start"] == "2020-03-04T10:00:00Z"
    assert child["parent.effectivePeriod.end"] == "2020-03-04"
    assert child["parent.subject.id"] == "p1"
    assert "parent.valueString" not in child.index


def test_a_panel_without_a_value_of_its_own_is_kept_in_the_parent_table():
    observation = build_fhir_tables([("bundle.json", _resources())])["Observation"]
    panel = observation[observation["code.code"] == "85354-9"].iloc[0]
    assert panel["valueQuantity.value"] == ""
    assert panel["valueCodeableConcept.code"] == ""
