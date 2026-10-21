"""Tests for the FHIR code system reference and the derived declarations."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from app.tools.data.fhir_code_systems import (
    FROM_SYSTEM_PREFIX,
    MAX_CODED_FIELD_LENGTH,
    build_system_code_keys,
    derive_fhir_declarations,
    known_code_systems,
    load_fhir_reference,
    parse_from_system,
    split_system_code_key,
    standard_for_system,
)
from app.tools.data.fhir_flattener import build_fhir_tables
from app.tools.data.source_loader import load_source_tables

FIXTURE = Path(__file__).parent.parent / "fixtures" / "fhir" / "synthea_r4_sample_bundle.json"


def _sample_tables() -> dict[str, pd.DataFrame]:
    bundle = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return build_fhir_tables([("bundle.json", [e["resource"] for e in bundle["entry"]])])


def _empty_cfg() -> dict:
    return {"format": "fhir", "tables": {}, "type_concepts": {}}


# ------------------------------------------------------------- the reference

def test_reference_covers_the_systems_of_the_sample():
    systems = load_fhir_reference()["code_systems"]
    assert systems["http://snomed.info/sct"] == "SNOMED"
    assert systems["http://loinc.org"] == "LOINC"
    assert systems["http://www.nlm.nih.gov/research/umls/rxnorm"] == "RxNorm"
    assert systems["http://hl7.org/fhir/sid/cvx"] == "CVX"


def test_oid_forms_resolve_to_the_same_standards():
    systems = load_fhir_reference()["code_systems"]
    assert systems["urn:oid:2.16.840.1.113883.6.96"] == "SNOMED"
    assert systems["urn:oid:2.16.840.1.113883.6.1"] == "LOINC"
    assert systems["urn:oid:2.16.840.1.113883.6.88"] == "RxNorm"
    assert systems["urn:oid:2.16.840.1.113883.12.292"] == "CVX"


def test_icd9_is_mapped_only_through_its_unambiguous_forms():
    systems = load_fhir_reference()["code_systems"]
    assert systems["http://hl7.org/fhir/sid/icd-9-cm/diagnosis"] == "ICD9CM"
    assert systems["http://hl7.org/fhir/sid/icd-9-cm/procedure"] == "ICD9Proc"
    assert "http://hl7.org/fhir/sid/icd-9-cm" not in systems


def test_every_standard_token_exists_in_the_semantic_mapper():
    mapper = pytest.importorskip("app.tools.mapping.semantic.semantic_mapper")
    if not getattr(mapper, "STANDARD_TO_VOCABULARY", None):
        pytest.skip("semantic_mapper has no vocabulary table (test stub)")
    tokens = set(load_fhir_reference()["code_systems"].values())
    assert tokens <= set(mapper.STANDARD_TO_VOCABULARY), tokens - set(mapper.STANDARD_TO_VOCABULARY)


def test_missing_reference_file_raises_but_known_systems_degrades(tmp_path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(FileNotFoundError):
        load_fhir_reference(missing)
    assert known_code_systems(missing) == set()


# --------------------------------------------------------------- helpers

def test_parse_from_system():
    assert parse_from_system("from_system:code.system") == "code.system"
    assert parse_from_system("from_system: vaccineCode.system ") == "vaccineCode.system"
    assert parse_from_system("SNOMED") is None
    assert parse_from_system(None) is None
    assert parse_from_system("from_system:") is None


def test_standard_for_system():
    systems = load_fhir_reference()["code_systems"]
    assert standard_for_system("http://snomed.info/sct", systems) == "SNOMED"
    assert standard_for_system(" http://loinc.org ", systems) == "LOINC"
    assert standard_for_system("http://example.org/local", systems) is None
    assert standard_for_system("", systems) is None
    assert standard_for_system(None, systems) is None


# --------------------------------------------------------- (system, code) keys

def test_system_code_keys_pair_each_code_with_its_system():
    systems = pd.Series(["http://snomed.info/sct", "http://loinc.org"])
    codes = pd.Series(["44054006", "8480-6"])
    keys = build_system_code_keys(systems, codes)
    assert [split_system_code_key(k) for k in keys] == [
        ("http://snomed.info/sct", "44054006"),
        ("http://loinc.org", "8480-6"),
    ]


def test_the_same_code_in_two_systems_gives_two_distinct_keys():
    keys = build_system_code_keys(
        pd.Series(["http://snomed.info/sct", "http://loinc.org"]), pd.Series(["1234", "1234"])
    )
    assert keys.nunique() == 2


def test_a_blank_code_gets_no_key():
    keys = build_system_code_keys(pd.Series(["http://snomed.info/sct"] * 3), pd.Series(["44054006", "  ", ""]))
    assert isinstance(keys.iloc[0], str)
    assert pd.isna(keys.iloc[1]) and pd.isna(keys.iloc[2])


def test_a_code_with_unusual_characters_survives_the_round_trip():
    key = build_system_code_keys(pd.Series(["urn:oid:1.2.3"]), pd.Series(["A|B:C/D 1"])).iloc[0]
    assert split_system_code_key(key) == ("urn:oid:1.2.3", "A|B:C/D 1")


# ------------------------------------------------------ derived declarations

def test_declarations_are_derived_for_the_event_code_of_each_table():
    cfg, _ = derive_fhir_declarations(_sample_tables(), _empty_cfg())
    declared = cfg["tables"]
    assert declared["condition"]["code.code"] == "from_system:code.system"
    assert declared["observation"]["code.code"] == "from_system:code.system"
    assert declared["observation_component"]["code.code"] == "from_system:code.system"
    assert declared["procedure"]["code.code"] == "from_system:code.system"
    assert declared["medicationrequest"]["medicationCodeableConcept.code"] == "from_system:medicationCodeableConcept.system"
    assert declared["immunization"]["vaccineCode.code"] == "from_system:vaccineCode.system"
    assert declared["encounter"]["type.code"] == "from_system:type.system"


def test_qualifiers_of_an_event_are_not_declared():
    declared = derive_fhir_declarations(_sample_tables(), _empty_cfg())[0]["tables"]
    all_fields = {(t, f) for t, fields in declared.items() for f in fields}
    for qualifier in ("category.code", "clinicalStatus.code", "reasonCode.code", "verificationStatus.code"):
        assert not any(f == qualifier for _, f in all_fields), qualifier


def test_the_log_reports_the_vocabulary_found_for_each_field():
    _, log = derive_fhir_declarations(_sample_tables(), _empty_cfg())
    by_field = {(e["table"], e["field"]): e for e in log}
    assert by_field[("Condition", "code.code")]["standards"] == ["SNOMED"]
    assert by_field[("Observation", "code.code")]["standards"] == ["LOINC"]
    assert by_field[("MedicationRequest", "medicationCodeableConcept.code")]["standards"] == ["RxNorm"]
    assert by_field[("Immunization", "vaccineCode.code")]["standards"] == ["CVX"]
    assert all(e["status"] == "derived" for e in log)


def test_a_declaration_written_by_hand_takes_precedence():
    cfg_in = {"format": "fhir", "tables": {"condition": {"code.code": "ICD10"}}, "type_concepts": {}}
    cfg, log = derive_fhir_declarations(_sample_tables(), cfg_in)
    assert cfg["tables"]["condition"]["code.code"] == "ICD10"
    entry = next(e for e in log if e["table"] == "Condition")
    assert entry["status"] == "kept the declaration written by hand"


def test_nothing_is_derived_when_no_system_is_known():
    df = pd.DataFrame({"id": ["1"], "code.system": ["http://example.org/local"], "code.code": ["L1"]})
    cfg, log = derive_fhir_declarations({"Condition": df}, _empty_cfg())
    assert cfg["tables"] == {}
    assert log[0]["status"] == "skipped: no known coding system in the data"
    assert log[0]["unsupported_systems"] == ["http://example.org/local"]


def test_a_field_name_too_long_to_be_enriched_is_skipped():
    path = "p" * (MAX_CODED_FIELD_LENGTH)               # "<path>.code" is then too long
    df = pd.DataFrame({"id": ["1"], f"{path}.system": ["http://snomed.info/sct"], f"{path}.code": ["1"]})
    reference = {"code_systems": {"http://snomed.info/sct": "SNOMED"}, "event_code_paths": {"condition": [path]}}
    cfg, log = derive_fhir_declarations({"Condition": df}, _empty_cfg(), reference)
    assert cfg["tables"] == {}
    assert "longer than" in log[0]["status"]


def test_the_original_configuration_is_not_modified():
    cfg_in = _empty_cfg()
    derive_fhir_declarations(_sample_tables(), cfg_in)
    assert cfg_in["tables"] == {}


def test_a_table_without_an_event_code_path_gets_no_declaration():
    df = pd.DataFrame({"id": ["1"], "code.system": ["http://snomed.info/sct"], "code.code": ["1"]})
    cfg, log = derive_fhir_declarations({"Device": df}, _empty_cfg())
    assert cfg["tables"] == {} and log == []


# -------------------------------------------- the loader uses the known systems

def test_loader_keeps_the_coding_whose_system_is_known(tmp_path):
    condition = {
        "resourceType": "Condition", "id": "c1",
        "code": {"coding": [
            {"system": "http://example.org/local", "code": "L1"},
            {"system": "http://snomed.info/sct", "code": "44054006"},
        ]},
    }
    (tmp_path / "c.json").write_text(json.dumps(condition), encoding="utf-8")
    table = load_source_tables("fhir", tmp_path)["Condition"]
    assert table.iloc[0]["code.code"] == "44054006"
    assert table.iloc[0]["code.system"] == "http://snomed.info/sct"
    assert len(json.loads(table.iloc[0]["code.coding.json_all"])) == 2
