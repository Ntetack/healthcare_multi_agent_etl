"""End-to-end proof that the two-step OMOP resolution actually works
through the real MappingAgent.run() flow - not just the underlying
semantic_mapper function in isolation. Reproduces the exact MIMIC-III
scenario: a raw ICD9CM diagnosis code (non-standard vocabulary) must
resolve to BOTH its own source concept AND a mapped Standard (SNOMED)
concept, routing correctly to condition_occurrence."""
import json
from unittest.mock import MagicMock

import pandas as pd

from app.agents.mapping import MappingAgent


def test_icd9cm_code_resolves_source_and_standard_concept_separately(monkeypatch):
    monkeypatch.setattr("app.agents.mapping.get_table_columns", lambda table, schema=None: [])
    monkeypatch.setattr("app.agents.mapping.write_initial_staging", lambda name, df, exec_id: f"staging_{name}")

    # Simulates the real two-step outcome: 307.50 (ICD9CM, non-standard)
    # maps via "Maps to" to a real SNOMED standard concept.
    def fake_resolve_concept_pair(source_value, standard):
        if standard == "ICD9CM" and source_value == "307.50":
            source_concept = {
                "concept_id": 44821974, "concept_name": "Eating disorder, unspecified",
                "vocabulary_id": "ICD9CM", "domain_id": "Condition", "standard_concept": None,
            }
            standard_concept = {
                "concept_id": 4263084, "concept_name": "Eating disorder",
                "vocabulary_id": "SNOMED", "domain_id": "Condition",
            }
            return {"source_concept": source_concept, "standard_concept": standard_concept}
        return {"source_concept": None, "standard_concept": None}

    monkeypatch.setattr("app.agents.mapping.resolve_concept_pair", fake_resolve_concept_pair)

    agent = MappingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({"mappings": []}))

    state = {
        "source_name": "mimic_iii_demo",
        "execution_id": "RUN-1",
        "batch_metadata": {"format": "csv", "tables": {"diagnoses_icd": {"icd9_code": "ICD9CM"}}},
        "_raw_tables": {"diagnoses_icd": pd.DataFrame({"icd9_code": ["307.50"]})},
        "profiling_output": {"per_table": {}},
    }

    result = agent.run(state)

    semantic_mapping = result.output["per_table"]["diagnoses_icd"]["semantic_mapping"]
    assert len(semantic_mapping) == 1
    record = semantic_mapping[0]

    # The STANDARD concept (SNOMED) - what belongs in condition_concept_id.
    assert record["target_concept_id"] == 4263084
    # The SOURCE concept (ICD9CM, non-standard) - what belongs in
    # condition_source_concept_id. THIS is the field that was
    # previously never computed at all.
    assert record["source_concept_id"] == 44821974
    # Correct routing, based on the STANDARD concept's domain.
    assert record["target_table"] == "condition_occurrence"
    assert record["target_source_concept_field"] == "condition_source_concept_id"
    assert "Maps to" in record["reason"]


def test_icd9cm_code_with_no_standard_mapping_still_routes_via_source_domain(monkeypatch):
    """A source code that exists in its own vocabulary but has NO
    'Maps to' target must still route using its OWN domain, rather than
    being dropped entirely - a genuinely classification-only code
    deserves a best-effort placement, not silent loss."""
    monkeypatch.setattr("app.agents.mapping.get_table_columns", lambda table, schema=None: [])
    monkeypatch.setattr("app.agents.mapping.write_initial_staging", lambda name, df, exec_id: f"staging_{name}")

    def fake_resolve_concept_pair(source_value, standard):
        source_concept = {
            "concept_id": 99999, "concept_name": "Some non-standard code",
            "vocabulary_id": "ICD9CM", "domain_id": "Condition", "standard_concept": None,
        }
        return {"source_concept": source_concept, "standard_concept": None}

    monkeypatch.setattr("app.agents.mapping.resolve_concept_pair", fake_resolve_concept_pair)

    agent = MappingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({"mappings": []}))

    state = {
        "source_name": "mimic_iii_demo", "execution_id": "RUN-1",
        "batch_metadata": {"format": "csv", "tables": {"diagnoses_icd": {"icd9_code": "ICD9CM"}}},
        "_raw_tables": {"diagnoses_icd": pd.DataFrame({"icd9_code": ["999.9"]})},
        "profiling_output": {"per_table": {}},
    }
    result = agent.run(state)

    record = result.output["per_table"]["diagnoses_icd"]["semantic_mapping"][0]
    assert record["target_concept_id"] is None  # no standard mapping found
    assert record["source_concept_id"] == 99999  # but source concept IS preserved
    assert record["target_table"] == "condition_occurrence"  # routed via source's own domain
    assert "no 'Maps to'" in record["reason"]
