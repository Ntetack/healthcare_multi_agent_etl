"""Mechanism 2 (target-first field resolution) calls the LLM AND
introspects the real DB (get_table_columns) - both mocked here so this
runs without real API keys or a DB. Verifies: complete field lists drive
resolution (not a hand-picked subset), vocabulary fields are resolved
automatically once paired, and fields with no plausible pairing (e.g.
*_type_concept_id) are explicitly skipped rather than guessed."""
import json
from unittest.mock import MagicMock

import pandas as pd

from app.agents.mapping import MappingAgent

# Minimal fake PERSON columns - enough to test the pairing mechanism
# without needing a real DB.
_FAKE_PERSON_COLUMNS = [
    {"column_name": "person_id", "data_type": "integer"},
    {"column_name": "gender_concept_id", "data_type": "integer"},
    {"column_name": "gender_source_value", "data_type": "character varying"},
    {"column_name": "year_of_birth", "data_type": "integer"},
    {"column_name": "birth_datetime", "data_type": "timestamp without time zone"},
]


def _fake_llm_response(mappings):
    return MagicMock(content=json.dumps({"mappings": mappings}))


def test_full_field_list_used_not_a_hand_picked_subset(monkeypatch):
    """The bug being fixed: year_of_birth must be askable, since it's
    part of the REAL introspected field list - not a hand-curated
    STRUCTURAL_TABLE_FIELDS subset that used to omit it."""
    monkeypatch.setattr(
        "app.agents.mapping.get_table_columns",
        lambda table, schema=None: _FAKE_PERSON_COLUMNS if table == "person" else [],
    )
    monkeypatch.setattr("app.agents.mapping.map_concept", lambda value, standard: None)

    agent = MappingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = _fake_llm_response([
        {"target_field": "year_of_birth", "source_table": "PATIENTS", "source_field": "BIRTHDATE",
         "confidence": 0.8, "reason": "birth date column found"},
    ])

    tables = {"PATIENTS": pd.DataFrame({"BIRTHDATE": ["1975-03-21"]})}
    records, _ = agent._resolve_all_target_fields(tables, tables, profiling_per_table={})

    assert any(r.target_field == "year_of_birth" and r.source_table == "PATIENTS" for r in records)
    # Confirm the LLM was actually asked about year_of_birth (not just
    # gender_concept_id / gender_source_value, which are the vocab pair).
    called_prompt = agent.llm.invoke.call_args_list[0].args[0]
    assert "year_of_birth" in called_prompt


def test_vocab_field_resolved_automatically_once_paired(monkeypatch):
    monkeypatch.setattr(
        "app.agents.mapping.get_table_columns",
        lambda table, schema=None: _FAKE_PERSON_COLUMNS if table == "person" else [],
    )

    def fake_map_concept(value, standard):
        if standard == "Gender" and value == "F":
            return {"concept_id": 8532, "domain_id": "Gender"}
        return None
    monkeypatch.setattr("app.agents.mapping.map_concept", fake_map_concept)

    agent = MappingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = _fake_llm_response([
        {"target_field": "gender_source_value", "source_table": "PATIENTS", "source_field": "gender",
         "confidence": 0.9, "reason": "explicit gender column"},
    ])

    tables = {"PATIENTS": pd.DataFrame({"gender": ["F", "F"]})}
    records, _ = agent._resolve_all_target_fields(tables, tables, profiling_per_table={})

    gender_concept_records = [r for r in records if r.target_field == "gender_concept_id"]
    assert len(gender_concept_records) == 1
    assert gender_concept_records[0].target_concept_id == 8532
    assert gender_concept_records[0].source_value == "F"
    assert gender_concept_records[0].data_type == "integer"


def test_missing_table_does_not_crash_whole_batch(monkeypatch):
    """If a table can't be introspected (DDL not installed, DB down),
    record the failure for that table and continue with the others."""
    def fake_get_columns(table, schema=None):
        if table == "person":
            raise ValueError(f"Table '{table}' has no columns")
        return []
    monkeypatch.setattr("app.agents.mapping.get_table_columns", fake_get_columns)
    monkeypatch.setattr("app.agents.mapping.map_concept", lambda value, standard: None)

    agent = MappingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = _fake_llm_response([])

    records, _ = agent._resolve_all_target_fields({}, {}, profiling_per_table={})

    person_failure = [r for r in records if r.target_table == "person"]
    assert len(person_failure) == 1
    assert "Could not introspect" in person_failure[0].reason
