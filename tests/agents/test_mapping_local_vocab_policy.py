"""MappingAgent, local vocabulary field: which vocabularies and which lookup
policy reach the concept search.

Without a declaration in metadata.yaml, the vocabularies are chosen from a
sample of the REAL labels (not from the raw identifiers). With one, the
declaration wins and the LLM is not asked. Lookups and the LLM are faked.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app.agents import mapping as mm
from app.agents.mapping import MappingAgent

JOIN = {
    "join_table": "D_ITEMS", "join_key_source": "ab_itemid", "join_key_target": "itemid",
    "resolved_column": "label", "resolved_kind": "text", "resolved_standards": ["RxNorm", "SNOMED"],
}


def _tables():
    micro = pd.DataFrame({"ab_itemid": ["1", "", "2", "1"], "row_id": ["a", "b", "c", "d"],
                          "subject_id": ["p1", "p1", "p2", "p3"], "org_name": ["E COLI"] * 4})
    items = pd.DataFrame({"itemid": ["1", "2"], "label": ["GENTAMICIN", "AMIKACIN"]})
    return {"MICROBIOLOGYEVENTS": micro, "D_ITEMS": items}


def _run(monkeypatch, cfg, discovered=None):
    calls = {"policy": [], "standards": [], "discover": []}

    def fake_policy(value, standards, templates=None, aliases=None):
        calls["policy"].append((value, list(standards), templates, aliases))
        concept = {"concept_id": 100, "concept_name": value, "domain_id": "Measurement", "_match_confidence": 1.0}
        return {"source_concept": concept, "standard_concept": concept, "matched_name": value}

    def fake_standards(llm, table, field, labels, n_distinct, source_name, fallback, context_rows=None):
        calls["standards"].append((table, field, list(labels), n_distinct, list(fallback)))
        calls["context"] = context_rows
        return ["LOINC"]

    def fake_discover(llm, table, field, labels, standards, context_rows, source_name):
        calls["discover"].append((table, field, list(labels), list(standards)))
        return discovered

    monkeypatch.setattr(mm, "ensure_mapping_cache_table", lambda: None)
    monkeypatch.setattr(mm, "source_root_path", lambda name: Path("/folder/that/does/not/exist"))
    monkeypatch.setattr(mm, "build_structural_mapping", lambda cols: {})
    monkeypatch.setattr(mm, "resolve_local_vocab_join", lambda *a, **k: dict(JOIN))
    monkeypatch.setattr(mm, "resolve_concept_with_policy", fake_policy)
    monkeypatch.setattr(mm, "resolve_standards_from_labels", fake_standards)
    monkeypatch.setattr(mm, "discover_name_templates", fake_discover)
    monkeypatch.setattr(mm, "write_initial_staging", lambda name, df, execution_id: "staging")
    agent = MappingAgent()
    monkeypatch.setattr(agent, "_resolve_all_target_fields", lambda *a, **k: ([], []))
    state = {"source_name": "src", "batch_metadata": cfg, "_raw_tables": _tables(), "execution_id": "e1"}
    result = agent.run(state)
    return calls, result, state["_enriched_tables"]["MICROBIOLOGYEVENTS"]


BASE_CFG = {"tables": {"microbiologyevents": {"ab_itemid": "local"}}}


def test_without_declaration_the_vocabularies_come_from_the_labels(monkeypatch):
    calls, result, enriched = _run(monkeypatch, dict(BASE_CFG))
    assert calls["standards"] == [("MICROBIOLOGYEVENTS", "ab_itemid", ["GENTAMICIN", "AMIKACIN"], 2, ["RxNorm", "SNOMED"])]
    # the labels were searched in what the label-based question answered, without a policy
    assert {c[0] for c in calls["policy"]} == {"GENTAMICIN", "AMIKACIN"}
    assert all(c[1] == ["LOINC"] and c[2] is None and c[3] is None for c in calls["policy"])
    assert result.output["local_vocab_joins"]["MICROBIOLOGYEVENTS.ab_itemid"]["resolved_standards"] == ["LOINC"]
    assert result.output["local_vocab_join_failures"] == {}


def test_declaration_wins_and_the_llm_is_not_asked(monkeypatch):
    cfg = dict(BASE_CFG, local_vocab_overrides={"MICROBIOLOGYEVENTS": {"ab_itemid": {
        "resolved_standards": ["LOINC"],
        "name_templates": ["{label} [Susceptibility]"],
        "name_aliases": {"PIPERACILLIN/TAZO": "Piperacillin+Tazobactam"},
    }}})
    calls, _, _ = _run(monkeypatch, cfg)
    assert calls["standards"] == []
    assert calls["policy"] and all(
        c[1] == ["LOINC"] and c[2] == ["{label} [Susceptibility]"] and "PIPERACILLIN/TAZO" in c[3]
        for c in calls["policy"])


def test_rows_without_antibiotic_get_no_concept_and_the_others_route_to_measurement(monkeypatch):
    _, _, enriched = _run(monkeypatch, dict(BASE_CFG))
    targets = enriched["ab_itemid_target_table"]
    assert targets.isna().tolist() == [False, True, False, False]
    assert set(targets.dropna()) == {"measurement"}


def test_the_variant_found_by_the_agent_reaches_the_lookup(monkeypatch):
    found = ["{label} [Susceptibility] by Minimum inhibitory concentration (MIC)", "{label} [Susceptibility]"]
    calls, result, _ = _run(monkeypatch, dict(BASE_CFG), discovered=found)
    assert calls["discover"] == [("MICROBIOLOGYEVENTS", "ab_itemid", ["GENTAMICIN", "AMIKACIN"], ["LOINC"])]
    assert all(c[2] == found for c in calls["policy"])
    assert result.output["local_vocab_joins"]["MICROBIOLOGYEVENTS.ab_itemid"]["name_templates"] == found


def test_the_model_sees_rows_without_identifiers(monkeypatch):
    calls, _, _ = _run(monkeypatch, dict(BASE_CFG))
    assert calls["context"] and all(set(r) == {"org_name"} for r in calls["context"])   # no row_id, subject_id, key


def test_a_declaration_bypasses_the_discovery(monkeypatch):
    cfg = dict(BASE_CFG, local_vocab_overrides={"MICROBIOLOGYEVENTS": {"ab_itemid": {"resolved_standards": ["LOINC"]}}})
    calls, _, _ = _run(monkeypatch, cfg, discovered=["{label}x"])
    assert calls["discover"] == [] and calls["standards"] == []
