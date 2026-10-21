"""A curated mapping declared for a local field takes ABSOLUTE PRIORITY.

The bug this guards against: the curated file was consulted only when the
model had proposed NO vocabulary for the field. As soon as it suggested some
(it always does), the file was never read and the automatic search - whose
result can be a false friend - decided alone. A curated file that cannot be
applied (missing, or its header lacks the declared column) must also show.
"""
from __future__ import annotations

import pandas as pd
import pytest

from app.agents import mapping as mm
from app.agents.mapping import MappingAgent

JOIN = {"join_table": "D_ITEMS", "join_key_source": "itemid", "join_key_target": "itemid",
        "resolved_column": "label", "resolved_kind": "text", "resolved_standards": ["LOINC", "SNOMED"]}


def _cfg(**spec_extra):
    spec = {"source_table": "DATETIMEEVENTS", "source_field": "itemid",
            "mapping_file": "curated.csv", "mapping_column": "observation_concept_id",
            "source_concept_column": "observation_source_concept_id", "force_target_table": "observation"}
    spec.update(spec_extra)
    return {"tables": {"datetimeevents": {"ITEMID": "local"}},
            "fixed_value_mappings": {"observation": {"observation_concept_id": spec}}}


def _run(monkeypatch, tmp_path, cfg, csv, standards):
    csv.to_csv(tmp_path / "curated.csv", index=False)
    items = ["225757", "999"]  # 225757 is curated, 999 is not
    tables = {"DATETIMEEVENTS": pd.DataFrame({"itemid": items, "row_id": ["a", "b"]}),
              "D_ITEMS": pd.DataFrame({"itemid": items, "label": ["Insertion Date", "Other"]})}

    def found(value, standards, templates=None, aliases=None):
        c = {"concept_id": 100, "concept_name": value, "domain_id": "Measurement", "_match_confidence": 1.0}
        return {"source_concept": c, "standard_concept": c}

    monkeypatch.setattr(mm, "ensure_mapping_cache_table", lambda: None)
    monkeypatch.setattr(mm, "source_root_path", lambda name: tmp_path)
    monkeypatch.setattr(mm, "build_structural_mapping", lambda cols: {})
    monkeypatch.setattr(mm, "resolve_local_vocab_join", lambda *a, **k: dict(JOIN, resolved_standards=standards))
    monkeypatch.setattr(mm, "resolve_concept_with_policy", found)
    monkeypatch.setattr(mm, "resolve_standards_from_labels", lambda llm, t, f, l, n, s, fb, rows=None: fb)
    monkeypatch.setattr(mm, "discover_name_templates", lambda *a, **k: None)
    monkeypatch.setattr(mm, "get_concept_domain", lambda cid: "Measurement")
    monkeypatch.setattr(mm, "write_initial_staging", lambda n, d, e: "staging")
    agent = MappingAgent()
    monkeypatch.setattr(agent, "_resolve_all_target_fields", lambda *a, **k: ([], []))
    state = {"source_name": "src", "batch_metadata": cfg, "_raw_tables": tables, "execution_id": "e"}
    result = agent.run(state)
    enriched = state["_enriched_tables"]["DATETIMEEVENTS"].set_index("row_id")
    return result, enriched


CSV = pd.DataFrame({"itemid": ["225757"], "observation_concept_id": [42536500],
                    "observation_source_concept_id": [2001028908]})


@pytest.mark.parametrize("standards", [["LOINC", "SNOMED"], []])
def test_curated_value_wins_whatever_the_model_proposed(monkeypatch, tmp_path, standards):
    _, e = _run(monkeypatch, tmp_path, _cfg(), CSV, standards)
    assert e.loc["a", "itemid_concept_id"] == 42536500
    assert e.loc["a", "itemid_source_concept_id"] == 2001028908
    assert e.loc["a", "itemid_target_table"] == "observation"      # force_target_table


def test_a_value_the_file_does_not_cover_keeps_the_automatic_result(monkeypatch, tmp_path):
    _, e = _run(monkeypatch, tmp_path, _cfg(), CSV, ["LOINC", "SNOMED"])
    assert e.loc["b", "itemid_concept_id"] == 100
    assert e.loc["b", "itemid_target_table"] == "measurement"


def test_the_curated_values_are_recorded_as_mappings(monkeypatch, tmp_path):
    result, _ = _run(monkeypatch, tmp_path, _cfg(), CSV, ["LOINC", "SNOMED"])
    records = result.output["per_table"]["DATETIMEEVENTS"]["semantic_mapping"]
    assert [r["source_value"] for r in records if r["standard"] == "fixed_mapping"] == ["225757"]


def test_a_header_without_the_declared_key_column_is_reported(monkeypatch, tmp_path):
    renamed = CSV.rename(columns={"itemid": "item_id"})
    result, e = _run(monkeypatch, tmp_path, _cfg(), renamed, ["LOINC", "SNOMED"])
    failure = result.output["local_vocab_join_failures"]["DATETIMEEVENTS.itemid"]
    assert "itemid" in failure and "source_field_column" in failure
    assert e.loc["a", "itemid_concept_id"] == 100                    # nothing could be applied


def test_declaring_the_key_column_makes_it_work(monkeypatch, tmp_path):
    renamed = CSV.rename(columns={"itemid": "item_id"})
    result, e = _run(monkeypatch, tmp_path, _cfg(source_field_column="item_id"), renamed, ["LOINC", "SNOMED"])
    assert "DATETIMEEVENTS.itemid" not in result.output["local_vocab_join_failures"]
    assert e.loc["a", "itemid_concept_id"] == 42536500


def test_a_missing_file_is_reported(monkeypatch, tmp_path):
    result, _ = _run(monkeypatch, tmp_path, _cfg(mapping_file="absent.csv"), CSV, ["LOINC", "SNOMED"])
    assert "not found" in result.output["local_vocab_join_failures"]["DATETIMEEVENTS.itemid"]
