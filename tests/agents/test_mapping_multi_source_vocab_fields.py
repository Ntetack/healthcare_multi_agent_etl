"""A vocabulary field whose paired source_value field is filled from SEVERAL
source tables must be resolved for every one of them.

The bug this guards against: `measurement.unit_source_value` is mapped from
CHARTEVENTS.valueuom, LABEVENTS.valueuom and PROCEDUREEVENTS_MV.valueuom. The
plain resolutions were indexed by target field, so only the last one survived
and `unit_concept_id` was resolved from PROCEDUREEVENTS_MV alone (two distinct
values). The units of the two largest source tables never reached the
vocabulary and 100% of the measurements were loaded with unit_concept_id = 0.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd

from app.agents import mapping as mapping_module
from app.agents.mapping import MappingAgent
from app.agents.transformation import TransformationAgent
from app.schemas.structural_target_mapping import StructuralTargetMapping

COLUMNS = ["measurement_id", "unit_concept_id", "unit_source_value"]
UNIT_IDS = {"mg/dL": 8840, "%": 8554, "min": 8550}      # exact codes of the fake vocabulary


def _tables() -> dict[str, pd.DataFrame]:
    return {
        "CHARTEVENTS": pd.DataFrame({"valueuom": ["mg/dL", "BPM", "mg/dL", None]}),
        "LABEVENTS": pd.DataFrame({"valueuom": ["mg/dL", "%"]}),
        "PROCEDUREEVENTS_MV": pd.DataFrame({"valueuom": ["min", None]}),
    }


def _plain(source_table: str, source_field: str = "valueuom") -> StructuralTargetMapping:
    return StructuralTargetMapping(
        target_table="measurement", target_field="unit_source_value",
        source_table=source_table, source_field=source_field, confidence=0.95, reason="unit of measure",
    )


def _resolve(monkeypatch, plain, tables=None, llm=None):
    tables = tables if tables is not None else _tables()
    monkeypatch.setattr(mapping_module, "IN_SCOPE_TABLES", ["measurement"])
    monkeypatch.setattr(mapping_module, "TABLE_FIELD_TEMPLATES", {})
    monkeypatch.setattr(mapping_module, "get_table_columns",
                        lambda table, *a, **k: [{"column_name": c, "data_type": "integer"} for c in COLUMNS])
    monkeypatch.setattr(mapping_module, "get_vocabulary_fields", lambda table: {"unit_concept_id": "Unit"})
    monkeypatch.setattr(mapping_module, "find_paired_source_value_field",
                        lambda field, available: "unit_source_value" if "unit_source_value" in available else None)
    monkeypatch.setattr(mapping_module, "map_concept",
                        lambda value, standard: {"concept_id": UNIT_IDS[value]} if value in UNIT_IDS else None)
    agent = MappingAgent(llm=llm) if llm is not None else MappingAgent()
    monkeypatch.setattr(agent, "_resolve_plain_fields", lambda *a, **k: (list(plain), {}))
    records, retry_log = agent._resolve_all_target_fields(tables, tables, {})
    return agent, tables, [r for r in records if r.target_field == "unit_concept_id"], retry_log


def _all_three():
    return [_plain("CHARTEVENTS"), _plain("LABEVENTS"), _plain("PROCEDUREEVENTS_MV")]


def test_every_source_table_gets_its_own_group(monkeypatch):
    _, _, records, _ = _resolve(monkeypatch, _all_three())
    assert {(r.source_table, r.source_field) for r in records} == {
        ("CHARTEVENTS", "valueuom"), ("LABEVENTS", "valueuom"), ("PROCEDUREEVENTS_MV", "valueuom"),
    }


def test_each_source_is_resolved_against_its_own_values(monkeypatch):
    _, _, records, _ = _resolve(monkeypatch, _all_three())
    by_source = {}
    for r in records:
        by_source.setdefault(r.source_table, {})[r.source_value] = r.target_concept_id
    assert by_source["CHARTEVENTS"] == {"mg/dL": 8840, "BPM": None}
    assert by_source["LABEVENTS"] == {"mg/dL": 8840, "%": 8554}
    assert by_source["PROCEDUREEVENTS_MV"] == {"min": 8550}


def test_a_value_shared_by_two_tables_is_kept_for_both(monkeypatch):
    """"mg/dL" is in CHARTEVENTS and LABEVENTS: the final deduplication must not
    drop the second record, or that table would lose its whole group."""
    _, _, records, _ = _resolve(monkeypatch, _all_three())
    shared = [r for r in records if r.source_value == "mg/dL"]
    assert sorted(r.source_table for r in shared) == ["CHARTEVENTS", "LABEVENTS"]


def test_each_source_table_receives_its_concepts_after_transformation(monkeypatch):
    _, tables, records, _ = _resolve(monkeypatch, _all_three())
    transformed = {name: df.copy() for name, df in tables.items()}
    TransformationAgent._apply_vocab_fields([r.model_dump(mode="json") for r in records], transformed, [], [])
    column = "__omop_measurement__unit_concept_id"
    chart = transformed["CHARTEVENTS"][column]
    assert chart.iloc[0] == 8840 and chart.iloc[2] == 8840 and pd.isna(chart.iloc[1])   # BPM: unresolved
    assert list(transformed["LABEVENTS"][column]) == [8840, 8554]
    assert transformed["PROCEDUREEVENTS_MV"][column].iloc[0] == 8550


def test_the_sources_are_exported_for_the_snapshot(monkeypatch):
    agent, _, _, _ = _resolve(monkeypatch, _all_three())
    exported = {(v["target_field"], v["source_table"]) for v in agent._vocab_sources}
    assert exported == {("unit_concept_id", t) for t in ("CHARTEVENTS", "LABEVENTS", "PROCEDUREEVENTS_MV")}


def test_the_same_source_listed_twice_is_resolved_once(monkeypatch):
    _, _, records, _ = _resolve(monkeypatch, [_plain("LABEVENTS"), _plain("LABEVENTS")])
    assert len(records) == len({r.source_value for r in records}) == 2


def test_no_retry_hunts_for_another_column_when_there_are_several_sources(monkeypatch):
    tables = _tables()
    tables["CHARTEVENTS"] = pd.DataFrame({"valueuom": ["BPM", "mEq/L"]})     # matches nothing
    llm = MagicMock()
    _, _, records, retry_log = _resolve(monkeypatch, _all_three(), tables=tables, llm=llm)
    llm.invoke.assert_not_called()
    assert "measurement.unit_concept_id" not in retry_log
    # the unresolved units stay visible, per source, instead of disappearing
    chart = {r.source_value: r.target_concept_id for r in records if r.source_table == "CHARTEVENTS"}
    assert chart == {"BPM": None, "mEq/L": None}


def test_a_single_source_keeps_its_retry_behaviour(monkeypatch):
    tables = {"CHARTEVENTS": pd.DataFrame({"valueuom": ["BPM"], "other": ["mg/dL"]})}
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content='{"source_table": "CHARTEVENTS", "source_field": "other", '
                                                '"confidence": 0.7, "reason": "better column"}')
    _, _, records, retry_log = _resolve(monkeypatch, [_plain("CHARTEVENTS")], tables=tables, llm=llm)
    assert llm.invoke.called
    assert {r.source_field for r in records} == {"other"}
    assert retry_log["measurement.unit_concept_id"]["final_outcome"] == "resolved"


def test_a_source_that_is_not_loaded_is_skipped_without_hiding_the_others(monkeypatch):
    tables = _tables()
    del tables["LABEVENTS"]
    _, _, records, _ = _resolve(monkeypatch, _all_three(), tables=tables)
    assert {r.source_table for r in records} == {"CHARTEVENTS", "PROCEDUREEVENTS_MV"}
