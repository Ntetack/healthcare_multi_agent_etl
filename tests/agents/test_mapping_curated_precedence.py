"""A curated mapping names the authoritative source column of a field: the
automatic search must never look for the same field in another column.

The bug this guards against: a curated mapping covered only SOME of the raw
values of `Encounter.class.code` (AMB, EMER, IMP but not HH, VR). The agent then
carried on with the automatic search, on the column the model had chosen for
`visit_source_value` (`type.code`, SNOMED encounter types). Its results formed a
second group for the same output column, and the Transformation Agent applies
the groups in turn: the later one erased the curated one, every visit lost its
concept, and every visit row was dropped.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from app.agents import mapping as mapping_module
from app.agents.mapping import MappingAgent
from app.agents.transformation import TransformationAgent
from app.schemas.structural_target_mapping import StructuralTargetMapping
from app.tools.data.fhir_fixed_mappings import derive_fhir_fixed_mappings
from app.tools.data.fhir_flattener import build_fhir_tables

FIXTURE = Path(__file__).parent.parent / "fixtures" / "fhir" / "synthea_r4_sample_bundle.json"

VISIT_COLUMNS = ["visit_occurrence_id", "person_id", "visit_concept_id", "visit_source_value", "visit_start_date"]
OUTPUT_COLUMN = "__omop_visit_occurrence__visit_concept_id"


def _tables_with_uncovered_classes() -> dict[str, pd.DataFrame]:
    bundle = json.loads(FIXTURE.read_text(encoding="utf-8"))
    tables = build_fhir_tables([("bundle.json", [e["resource"] for e in bundle["entry"]])])
    encounter = tables["Encounter"]
    extra = encounter.iloc[[0, 0]].copy()
    extra["class.code"] = ["HH", "VR"]                   # two classes the curated file does not cover
    tables["Encounter"] = pd.concat([encounter, extra], ignore_index=True)
    return tables


def _plain_resolution(source_field: str) -> StructuralTargetMapping:
    return StructuralTargetMapping(
        target_table="visit_occurrence", target_field="visit_source_value",
        source_table="Encounter", source_field=source_field, confidence=0.9, reason="chosen by the model",
    )


def _resolve(monkeypatch, paired_source_field: str | None, map_concept=None):
    tables = _tables_with_uncovered_classes()
    cfg, _ = derive_fhir_fixed_mappings(tables, {"format": "fhir", "tables": {}, "type_concepts": {}})

    monkeypatch.setattr(mapping_module, "IN_SCOPE_TABLES", ["visit_occurrence"])
    monkeypatch.setattr(mapping_module, "TABLE_FIELD_TEMPLATES", {})
    monkeypatch.setattr(mapping_module, "get_table_columns",
                        lambda table, *a, **k: [{"column_name": c, "data_type": "integer"} for c in VISIT_COLUMNS])
    monkeypatch.setattr(mapping_module, "get_vocabulary_fields", lambda table: {"visit_concept_id": "Visit"})
    monkeypatch.setattr(mapping_module, "find_paired_source_value_field",
                        lambda field, available: "visit_source_value" if "visit_source_value" in available else None)
    monkeypatch.setattr(mapping_module, "map_concept", map_concept or (lambda value, standard: None))

    agent = MappingAgent()
    plain = [_plain_resolution(paired_source_field)] if paired_source_field else []
    monkeypatch.setattr(agent, "_resolve_plain_fields", lambda *a, **k: (plain, {}))
    records, _ = agent._resolve_all_target_fields(
        tables, tables, {}, batch_cfg=cfg, source_folder=Path("/folder/that/does/not/exist"),
    )
    return tables, [r for r in records if r.target_field == "visit_concept_id"]


def _transform(tables, records) -> pd.Series:
    transformed = {name: df.copy() for name, df in tables.items()}
    TransformationAgent._apply_vocab_fields([r.model_dump(mode="json") for r in records], transformed, [], [])
    return transformed["Encounter"][OUTPUT_COLUMN]


def test_the_automatic_search_does_not_look_in_another_column(monkeypatch):
    # The model linked visit_source_value to type.code, not to the curated class.code.
    _, records = _resolve(monkeypatch, "type.code")
    assert {r.source_field for r in records} == {"class.code"}


def test_the_curated_concepts_survive_the_transformation(monkeypatch):
    tables, records = _resolve(monkeypatch, "type.code")
    column = _transform(tables, records)
    by_class = dict(zip(tables["Encounter"]["class.code"], column))
    assert by_class["AMB"] == 9202 and by_class["EMER"] == 9203 and by_class["IMP"] == 9201
    assert column.notna().sum() >= 3                      # not erased: this was the symptom


def test_the_uncovered_values_are_reported_as_unresolved_with_the_file_to_complete(monkeypatch):
    _, records = _resolve(monkeypatch, "type.code")
    unresolved = {r.source_value: r for r in records if r.target_concept_id is None}
    assert set(unresolved) == {"HH", "VR"}
    assert "fhir_encounter_class_to_visit_concept.csv" in unresolved["HH"].reason
    assert unresolved["HH"].confidence == 0.0


def test_the_uncovered_values_stay_unresolved_after_the_transformation(monkeypatch):
    tables, records = _resolve(monkeypatch, "type.code")
    by_class = dict(zip(tables["Encounter"]["class.code"], _transform(tables, records)))
    assert pd.isna(by_class["HH"]) and pd.isna(by_class["VR"])


def test_a_missing_paired_field_still_reports_the_uncovered_values(monkeypatch):
    _, records = _resolve(monkeypatch, None)              # the model resolved no visit_source_value at all
    assert {r.source_value for r in records if r.target_concept_id is None} == {"HH", "VR"}
    assert {r.source_value for r in records if r.target_concept_id} == {"AMB", "EMER", "IMP"}


def test_when_the_paired_field_is_the_curated_column_the_automatic_search_still_runs(monkeypatch):
    searched = []

    def fake_map_concept(value, standard):
        searched.append((value, standard))
        return {"concept_id": 262, "_match_confidence": 0.95} if value == "HH" else None

    _, records = _resolve(monkeypatch, "class.code", fake_map_concept)
    assert searched and {v for v, _ in searched} == {"HH", "VR"}      # only what the curated file does not cover
    by_value = {r.source_value: r.target_concept_id for r in records}
    assert by_value["AMB"] == 9202 and by_value["HH"] == 262          # the automatic search can still help
