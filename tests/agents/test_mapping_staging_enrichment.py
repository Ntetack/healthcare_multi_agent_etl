"""Verifies that semantic mapping enriches the DataFrame with resolved
*_concept_id columns for EVERY distinct value (not just a sample) before
staging is written - the actual bug being fixed here."""
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.agents.mapping import MappingAgent


@pytest.fixture
def mock_search():
    """Fakes resolve_concept_pair() so no DB is needed: every code maps
    to a concept_id derived from the code itself, with domain
    'Condition'. source_concept == standard_concept here (the simple
    case - as if the declared vocabulary were itself Standard)."""
    def fake_resolve_concept_pair(source_value, standard):
        concept_id = (
            int(source_value.replace(".", "")) if source_value.replace(".", "").isdigit()
            else hash(source_value) % 1000
        )
        concept = {"concept_id": concept_id, "domain_id": "Condition", "concept_name": source_value}
        return {"source_concept": concept, "standard_concept": concept}
    return fake_resolve_concept_pair


def test_all_distinct_values_mapped_and_written_to_staging(monkeypatch, mock_search):
    monkeypatch.setattr("app.agents.mapping.resolve_concept_pair", mock_search)
    monkeypatch.setattr("app.agents.mapping.write_initial_staging", lambda name, df, exec_id: (
        _CAPTURED.update({"df": df, "name": name}) or f"staging_{name}"
    ))
    # This test exercises mechanism 1 (domain-driven semantic mapping);
    # mechanism 2 (target-first field resolution) also runs as part of
    # MappingAgent.run(), so its DB introspection is mocked out here too.
    monkeypatch.setattr("app.agents.mapping.get_table_columns", lambda table, schema=None: [])

    global _CAPTURED
    _CAPTURED = {}

    agent = MappingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content='{"mappings": []}')

    state = {
        "source_name": "test_source",
        "execution_id": "RUN-1",
        "batch_metadata": {"tables": {"diagnoses": {"icd_code": "ICD10"}}},
        "_raw_tables": {
            "DIAGNOSES": pd.DataFrame({"icd_code": ["100", "200", "300", "100"]})  # 3 distinct values, 4 rows
        },
        "profiling_output": {},
    }

    agent.run(state)

    enriched = _CAPTURED["df"]
    assert "icd_code_concept_id" in enriched.columns
    # All 4 rows filled, not just one sample - the fix under test.
    assert enriched["icd_code_concept_id"].notna().all()
    assert enriched.loc[enriched["icd_code"] == "100", "icd_code_concept_id"].iloc[0] == 100
    assert enriched.loc[enriched["icd_code"] == "200", "icd_code_concept_id"].iloc[0] == 200
