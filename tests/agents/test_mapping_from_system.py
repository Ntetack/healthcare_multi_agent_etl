"""The Mapping Agent on a FHIR batch: coded fields derived from the data and
resolved value by value in the vocabulary of their own coding system.

Everything that needs the database (the mapping cache, the staging tables,
the concept search) is replaced; what is tested is the logic of the agent:
which vocabulary each (system, code) pair is searched in, what happens to a
pair whose system is unknown, and what the enriched tables contain.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from app.agents import mapping as mapping_module
from app.agents.mapping import MappingAgent
from app.tools.data.fhir_flattener import build_fhir_tables

FIXTURE = Path(__file__).parent.parent / "fixtures" / "fhir" / "synthea_r4_sample_bundle.json"

DOMAIN_BY_STANDARD = {"SNOMED": "Condition", "LOINC": "Measurement", "RxNorm": "Drug", "CVX": "Drug"}


def _sample_tables() -> dict[str, pd.DataFrame]:
    bundle = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return build_fhir_tables([("bundle.json", [e["resource"] for e in bundle["entry"]])])


@pytest.fixture
def concept_calls(monkeypatch, tmp_path):
    """Replaces every database access of the agent. Returns the list of
    (code, standard) pairs the concept search was asked for."""
    calls: list[tuple[str, str]] = []

    def fake_resolve_concept_pair(value, standard):
        calls.append((value, standard))
        concept = {
            "concept_id": 100000 + len(calls),
            "concept_name": f"{standard}:{value}",
            "domain_id": DOMAIN_BY_STANDARD[standard],
            "_match_confidence": 1.0,
        }
        return {"source_concept": concept, "standard_concept": concept}

    monkeypatch.setattr(mapping_module, "resolve_concept_pair", fake_resolve_concept_pair)
    monkeypatch.setattr(mapping_module, "ensure_mapping_cache_table", lambda: None)
    monkeypatch.setattr(mapping_module, "write_initial_staging", lambda name, df, execution_id: f"staging_{name}")
    monkeypatch.setattr(mapping_module, "run_dir", lambda execution_id, stage: tmp_path)
    monkeypatch.setattr(MappingAgent, "_resolve_all_target_fields", lambda self, *a, **k: ([], {}))
    monkeypatch.setattr(MappingAgent, "persist", lambda self, result, report_markdown=None, stage_override=None: result)
    return calls


def _run(tables: dict[str, pd.DataFrame], batch_cfg: dict | None = None):
    state = {
        "source_name": "fhir_test",
        "batch_metadata": batch_cfg or {"format": "fhir", "tables": {}, "type_concepts": {}},
        "_raw_tables": tables,
        "execution_id": "RUN-test",
    }
    result = MappingAgent().run(state)
    return result, state["_enriched_tables"]


def _records(result, table: str) -> list[dict]:
    return result.output["per_table"][table]["semantic_mapping"]


def test_each_code_is_searched_in_the_vocabulary_of_its_own_system(concept_calls):
    tables = _sample_tables()
    _run(tables)
    standards_used = {standard for _, standard in concept_calls}
    assert standards_used == {"SNOMED", "LOINC", "RxNorm", "CVX"}
    # Only the code is searched: never the composite key, never the URI.
    assert all("\x1f" not in code and not code.startswith("http") for code, _ in concept_calls)
    # Every distinct condition code was searched in SNOMED.
    condition_codes = set(tables["Condition"]["code.code"])
    assert condition_codes <= {code for code, standard in concept_calls if standard == "SNOMED"}
    # Observation and component codes are LOINC.
    loinc_codes = {code for code, standard in concept_calls if standard == "LOINC"}
    assert set(tables["Observation"]["code.code"]) <= loinc_codes
    assert set(tables["Observation_component"]["code.code"]) <= loinc_codes


def test_records_carry_the_code_and_the_vocabulary_not_the_composite_key(concept_calls):
    tables = _sample_tables()
    result, _ = _run(tables)
    records = _records(result, "Condition")
    assert {r["standard"] for r in records} == {"SNOMED"}
    assert {r["source_value"] for r in records} == set(tables["Condition"]["code.code"])
    assert all(r["field"] == "Condition.code.code" for r in records)


def test_enriched_tables_route_each_row_to_the_table_of_its_domain(concept_calls):
    tables = _sample_tables()
    _, enriched = _run(tables)
    assert (enriched["Condition"]["code.code_target_table"] == "condition_occurrence").all()
    assert (enriched["Observation"]["code.code_target_table"] == "measurement").all()
    assert (enriched["Observation_component"]["code.code_target_table"] == "measurement").all()
    assert (enriched["MedicationRequest"]["medicationCodeableConcept.code_target_table"] == "drug_exposure").all()
    assert (enriched["Immunization"]["vaccineCode.code_target_table"] == "drug_exposure").all()
    assert enriched["Condition"]["code.code_concept_id"].notna().all()


def test_the_derived_declarations_are_reported(concept_calls):
    result, _ = _run(_sample_tables())
    derived = {(e["table"], e["field"]): e["status"] for e in result.output["fhir_derived_declarations"]}
    assert derived[("Condition", "code.code")] == "derived"
    assert derived[("Immunization", "vaccineCode.code")] == "derived"
    assert result.output["from_system_failures"] == {}


def test_a_value_with_an_unknown_system_is_left_unresolved_with_its_reason(concept_calls):
    condition = pd.DataFrame({
        "id": ["1", "2", "3"],
        "code.system": ["http://snomed.info/sct", "http://example.org/local", "http://snomed.info/sct"],
        "code.code": ["44054006", "L-77", ""],           # a known code, a local code, a blank code
        "_source_file": ["f.json"] * 3,
    })
    result, enriched = _run({"Condition": condition})

    assert ("L-77", "SNOMED") not in concept_calls
    assert [code for code, _ in concept_calls] == ["44054006"]       # the blank code is never searched

    records = {r["source_value"]: r for r in _records(result, "Condition")}
    assert set(records) == {"44054006", "L-77"}                      # no record for the blank code
    assert records["L-77"]["standard"] == "unknown_system"
    assert records["L-77"]["target_concept_id"] is None
    assert "http://example.org/local" in records["L-77"]["reason"]

    concept = enriched["Condition"]["code.code_concept_id"]
    assert pd.notna(concept.iloc[0])
    assert pd.isna(concept.iloc[1]) and pd.isna(concept.iloc[2])


def test_a_missing_system_column_is_reported_and_does_not_stop_the_agent(concept_calls):
    cfg = {"format": "fhir", "tables": {"condition": {"code.code": "from_system:nope.system"}}, "type_concepts": {}}
    result, _ = _run(_sample_tables(), cfg)
    assert "nope.system" in result.output["from_system_failures"]["Condition.code.code"]


def test_a_declaration_written_by_hand_keeps_its_fixed_vocabulary(concept_calls):
    cfg = {"format": "fhir", "tables": {"condition": {"code.code": "SNOMED"}}, "type_concepts": {}}
    tables = _sample_tables()
    result, _ = _run(tables, cfg)
    entry = next(e for e in result.output["fhir_derived_declarations"] if e["table"] == "Condition")
    assert entry["status"] == "kept the declaration written by hand"
    assert {r["standard"] for r in _records(result, "Condition")} == {"SNOMED"}


def test_a_csv_batch_is_not_affected(concept_calls):
    df = pd.DataFrame({"CODE": ["44054006", "44054006"], "_source_file": ["c.csv"] * 2})
    cfg = {"format": "csv", "tables": {"conditions": {"CODE": "SNOMED"}}, "type_concepts": {}}
    result, enriched = _run({"conditions": df}, cfg)
    assert result.output["fhir_derived_declarations"] == []
    assert concept_calls == [("44054006", "SNOMED")]
    assert enriched["conditions"]["CODE_concept_id"].notna().all()


def test_the_shared_fixed_mappings_reach_the_target_field_resolution(concept_calls, monkeypatch):
    captured = {}

    def fake_resolve_all(self, tables, enriched_tables, profiling_per_table, batch_cfg=None, source_folder=None):
        captured["batch_cfg"] = batch_cfg
        return [], {}

    monkeypatch.setattr(MappingAgent, "_resolve_all_target_fields", fake_resolve_all)
    result, _ = _run(_sample_tables())

    fixed = captured["batch_cfg"]["fixed_value_mappings"]
    assert Path(fixed["person"]["race_concept_id"]["mapping_file"]).name == "fhir_us_core_race_to_concept.csv"
    assert Path(fixed["person"]["ethnicity_concept_id"]["mapping_file"]).name == "fhir_us_core_ethnicity_to_concept.csv"
    assert Path(fixed["visit_occurrence"]["visit_concept_id"]["mapping_file"]).name == "fhir_encounter_class_to_visit_concept.csv"

    derived = {e["target_field"]: e["status"] for e in result.output["fhir_derived_fixed_mappings"]}
    assert derived == {
        "race_concept_id": "derived", "ethnicity_concept_id": "derived", "visit_concept_id": "derived",
    }


def test_a_csv_batch_gets_no_shared_fhir_mapping(concept_calls, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        MappingAgent, "_resolve_all_target_fields",
        lambda self, tables, enriched, profiling, batch_cfg=None, source_folder=None:
            captured.update(batch_cfg=batch_cfg) or ([], {}),
    )
    df = pd.DataFrame({"CODE": ["44054006"], "_source_file": ["c.csv"]})
    cfg = {"format": "csv", "tables": {"conditions": {"CODE": "SNOMED"}}, "type_concepts": {}}
    result, _ = _run({"conditions": df}, cfg)
    assert "fixed_value_mappings" not in captured["batch_cfg"]
    assert result.output["fhir_derived_fixed_mappings"] == []
