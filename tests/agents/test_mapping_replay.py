"""Replaying a mapping snapshot through MappingAgent.run().

No database and no real model: vocabulary searches, staging and OMOP schema
introspection are replaced by fakes. The model is a stub that records its
prompts, or one that fails the test as soon as it is called, which is how
"the snapshot replaces the model" is proved.
"""
from __future__ import annotations

import json
import re
from types import SimpleNamespace

import pandas as pd
import pytest

from app.agents.mapping import MappingAgent
from app.tools.common import io_utils
from app.tools.mapping import mapping_snapshot as ms

_COLUMNS = {
    "person": ["person_id", "gender_concept_id", "gender_source_value", "year_of_birth"],
    "condition_occurrence": [
        "condition_occurrence_id", "person_id", "condition_concept_id",
        "condition_start_date", "condition_source_value", "condition_source_concept_id",
    ],
}


class StubLLM:
    """Answers the structural prompt from a fixed table; remembers which
    target tables it was asked about."""

    def __init__(self, answers: dict[str, list[dict]] | None = None):
        self.answers = answers or {}
        self.asked: list[str] = []

    def invoke(self, prompt: str):
        target = re.search(r"table '(\w+)'", prompt).group(1)
        self.asked.append(target)
        return SimpleNamespace(content=json.dumps({"mappings": self.answers.get(target, [])}))


class ForbiddenLLM:
    def invoke(self, prompt: str):
        raise AssertionError("the model must not be called when the snapshot covers the decision")


GENDER = {"F": 8532, "M": 8507}
ICD = {"100": 1001, "200": 2002, "300": 3003}


def _plain(target_field, source_table, source_field):
    return {"target_field": target_field, "source_table": source_table, "source_field": source_field,
            "confidence": 0.9, "reason": "test"}


ANSWERS = {
    "person": [_plain("gender_source_value", "PATIENTS", "gender"), _plain("year_of_birth", "PATIENTS", "birth_year")],
    "condition_occurrence": [_plain("condition_start_date", "DIAGNOSES", "start")],
}


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("MAPPING_SNAPSHOT_DIR", str(tmp_path / "mappings"))
    monkeypatch.setattr(io_utils, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr("app.agents.mapping.ensure_mapping_cache_table", lambda: None)
    monkeypatch.setattr("app.agents.mapping.write_initial_staging", lambda name, df, exec_id: f"staging_{name}")
    monkeypatch.setattr("app.agents.mapping.get_vocabulary_version", lambda: "v-test")
    monkeypatch.setattr(
        "app.agents.mapping.get_table_columns",
        lambda table, schema=None: [{"column_name": c, "data_type": "text"} for c in _COLUMNS.get(table, [])],
    )
    monkeypatch.setattr(
        "app.agents.mapping.map_concept",
        lambda value, domain: {"concept_id": GENDER[value], "_match_confidence": 1.0}
        if domain == "Gender" and value in GENDER else None,
    )

    def fake_pair(value, standard):
        concept_id = ICD.get(value)
        if concept_id is None:
            return {"source_concept": None, "standard_concept": None}
        concept = {"concept_id": concept_id, "domain_id": "Condition", "concept_name": value, "_match_confidence": 1.0}
        return {"source_concept": concept, "standard_concept": concept}

    monkeypatch.setattr("app.agents.mapping.resolve_concept_pair", fake_pair)
    return tmp_path


def _state(tables, replay=None, source="hosp"):
    state = {
        "source_name": source,
        "execution_id": "RUN-X",
        "batch_metadata": {"tables": {"diagnoses": {"icd": "ICD10"}}, "format": "csv"},
        "_raw_tables": tables,
        "profiling_output": {},
    }
    if replay:
        state["mapping_replay"] = replay
    return state


def _batch1():
    return {
        "PATIENTS": pd.DataFrame({"gender": ["F", "F"], "birth_year": ["1980", "1975"]}),
        "DIAGNOSES": pd.DataFrame({"icd": ["100", "200"], "start": ["2020-01-01", "2020-02-01"]}),
    }


def _batch2():
    """Another delivery of the same source: a NEW gender value and a NEW code."""
    return {
        "PATIENTS": pd.DataFrame({"gender": ["M", "F"], "birth_year": ["1990", "1962"]}),
        "DIAGNOSES": pd.DataFrame({"icd": ["100", "300"], "start": ["2021-01-01", "2021-02-01"]}),
    }


def _run_and_snapshot(name="v1", tables=None):
    """Normal run, then the snapshot a validated run would have produced."""
    tables = tables or _batch1()
    state = _state(tables)
    agent = MappingAgent(llm=StubLLM(ANSWERS))
    result = agent.run(state)
    snapshot = ms.build_snapshot(
        name=name, source_name="hosp", execution_id="RUN-1", batch_folder="data/raw/hosp/b1",
        mapping_output=result.output, tables=tables, batch_cfg=state["batch_metadata"],
        source_folder=None, cdm_version="5.4", vocabulary_version="v-test",
    )
    ms.save_snapshot(snapshot)
    return result, snapshot


def _replay(tables, name="v1", on_mismatch="fallback", llm=None):
    agent = MappingAgent(llm=llm or ForbiddenLLM())
    result = agent.run(_state(tables, replay={"name": name, "on_mismatch": on_mismatch}))
    return agent, result


# ----------------------------------------------------------------------
def test_normal_run_exports_what_a_snapshot_needs():
    result, snapshot = _run_and_snapshot()
    out = result.output
    assert {"target_table": "person", "source_table": None} in out["plain_field_scopes"]
    assert {"target_table": "condition_occurrence", "source_table": "DIAGNOSES"} in out["plain_field_scopes"]
    assert {"target_table": "person", "target_field": "gender_concept_id",
            "source_table": "PATIENTS", "source_field": "gender"} in out["vocab_field_sources"]
    assert "replay" not in out  # a normal run reports no replay

    frozen = snapshot["frozen"]
    plain = {(p["target_table"], p["target_field"]): p["source_field"] for p in frozen["plain_fields"]}
    assert plain[("person", "year_of_birth")] == "birth_year"
    assert plain[("condition_occurrence", "condition_start_date")] == "start"


def test_replay_never_calls_the_model_and_resolves_new_values_normally():
    first, _ = _run_and_snapshot()
    agent, replayed = _replay(_batch2())  # ForbiddenLLM: any model call fails the test

    # same structural decisions as the original run
    def plain(output):
        return {(r["target_table"], r["target_field"]): (r["source_table"], r["source_field"])
                for r in output["structural_target_mappings"] if r["source_value"] is None and r["source_table"]}

    assert plain(replayed.output) == plain(first.output)

    # the gender value "M" did not exist in batch 1: found by the normal vocabulary search
    gender = {r["source_value"]: r["target_concept_id"] for r in replayed.output["structural_target_mappings"]
              if r["target_field"] == "gender_concept_id" and r["source_value"] is not None}
    assert gender == {"M": 8507, "F": 8532}
    # and so is the new ICD code "300"
    semantic = {r["source_value"]: r["target_concept_id"]
                for r in replayed.output["per_table"]["DIAGNOSES"]["semantic_mapping"]}
    assert semantic == {"100": 1001, "300": 3003}

    report = replayed.output["replay"]
    assert report["fallbacks"] == [] and report["rejected"] == []
    # gender_concept_id AND gender_source_concept_id are both read from the same column: two sources
    assert len(first.output["vocab_field_sources"]) == 2
    assert report["reused"]["plain_fields"] == 3
    assert report["reused"]["vocab_sources"] == len(first.output["vocab_field_sources"])
    assert report["value_drift"]["new_values"] >= 2 and report["value_drift"]["changed"] == 0
    assert "Replayed snapshot 'v1'" in replayed.reasoning_summary


def test_replay_report_is_written_in_the_markdown_report(env):
    _run_and_snapshot()
    _replay(_batch2())
    report = (env / "runs" / "RUN-X" / "mapping" / "report.md").read_text(encoding="utf-8")
    assert "## Replayed mapping" in report and "`v1`" in report


def test_replay_translates_table_and_column_case():
    _run_and_snapshot()
    lowered = {
        "patients": pd.DataFrame({"GENDER": ["F"], "BIRTH_YEAR": ["1980"]}),
        "diagnoses": pd.DataFrame({"icd": ["100"], "START": ["2020-01-01"]}),
    }
    _, replayed = _replay(lowered)
    mapped = {(r["target_table"], r["target_field"]): (r["source_table"], r["source_field"])
              for r in replayed.output["structural_target_mappings"] if r["source_value"] is None and r["source_table"]}
    assert mapped[("person", "year_of_birth")] == ("patients", "BIRTH_YEAR")
    assert mapped[("condition_occurrence", "condition_start_date")] == ("diagnoses", "START")


def test_missing_column_falls_back_to_the_model_for_that_field_only():
    _run_and_snapshot()
    drifted = _batch2()
    drifted["PATIENTS"] = drifted["PATIENTS"].rename(columns={"birth_year": "yob"})  # column renamed
    llm = StubLLM({"person": [_plain("year_of_birth", "PATIENTS", "yob")]})

    _, replayed = _replay(drifted, llm=llm)

    assert llm.asked == ["person"]  # asked once, and only about the field the snapshot could not provide
    mapped = {r["target_field"]: r["source_field"] for r in replayed.output["structural_target_mappings"]
              if r["target_table"] == "person" and r["source_value"] is None and r["source_table"]}
    assert mapped["year_of_birth"] == "yob" and mapped["gender_source_value"] == "gender"
    (fallback,) = replayed.output["replay"]["fallbacks"]
    assert fallback["kind"] == "plain_field" and "birth_year" in fallback["detail"]


def test_strict_mode_stops_instead_of_asking_the_model():
    _run_and_snapshot()
    drifted = _batch2()
    drifted["PATIENTS"] = drifted["PATIENTS"].rename(columns={"birth_year": "yob"})
    with pytest.raises(ms.MappingReplayError, match="on_mismatch is 'fail'"):
        _replay(drifted, on_mismatch="fail")


def test_new_contributing_source_table_is_resolved_by_the_model():
    """Another table feeds condition_occurrence for the first time: the snapshot says nothing about it."""
    _run_and_snapshot()
    tables = _batch2()
    tables["OTHER"] = pd.DataFrame({"icd": ["200"], "start": ["2021-05-05"]})
    state = _state(tables)
    state["batch_metadata"]["tables"]["other"] = {"icd": "ICD10"}
    llm = StubLLM({"condition_occurrence": [_plain("condition_start_date", "OTHER", "start")]})
    agent = MappingAgent(llm=llm)
    state["mapping_replay"] = {"name": "v1", "on_mismatch": "fallback"}
    result = agent.run(state)

    # Only the new scope is asked (the usual second look at unresolved fields included);
    # person and the DIAGNOSES scope were replayed.
    assert set(llm.asked) == {"condition_occurrence"}
    kinds = [f["kind"] for f in result.output["replay"]["fallbacks"]]
    assert kinds == ["plain_scope"]


def test_replay_of_another_source_is_refused():
    _, snapshot = _run_and_snapshot()
    other = _state(_batch2(), replay={"name": "v1"}, source="other_hospital")
    ms.save_snapshot({**snapshot, "source_name": "other_hospital"})  # same content filed under another source
    # the file says 'other_hospital' but the content claims 'hosp' -> refused
    path = ms.snapshot_path("other_hospital", "v1")
    data = json.loads(path.read_text())
    data["source_name"] = "hosp"
    path.write_text(json.dumps(data))
    with pytest.raises(ms.MappingReplayError, match="belongs to source 'hosp'"):
        MappingAgent(llm=ForbiddenLLM()).run(other)


def test_value_drift_reveals_a_changed_concept(monkeypatch):
    _run_and_snapshot()

    def updated_vocabulary(value, standard):
        concept = {"concept_id": 9999, "domain_id": "Condition", "concept_name": value, "_match_confidence": 1.0}
        return {"source_concept": concept, "standard_concept": concept}

    monkeypatch.setattr("app.agents.mapping.resolve_concept_pair", updated_vocabulary)
    _, replayed = _replay(_batch1())
    drift = replayed.output["replay"]["value_drift"]
    assert drift["changed"] == 2  # codes "100" and "200" now map elsewhere
    assert {e["source_value"] for e in drift["changed_examples"]} == {"100", "200"}
    assert drift["changed_examples"][0]["now"] == 9999


def test_replaying_a_replay_gives_an_identical_snapshot_core():
    """Saving a replayed run must not drift the frozen decisions."""
    _, original = _run_and_snapshot()
    _, replayed = _replay(_batch1())
    again = ms.derive_frozen(replayed.output)
    assert again["plain_fields"] == original["frozen"]["plain_fields"]
    assert again["vocab_sources"] == original["frozen"]["vocab_sources"]
    assert again["plain_field_scopes"] == original["frozen"]["plain_field_scopes"]


# ----------------------------------------------------------------------
# Local vocabulary joins
# ----------------------------------------------------------------------
JOIN = {"join_table": "D_ITEMS", "join_key_source": "itemid", "join_key_target": "itemid",
        "resolved_column": "code", "resolved_kind": "code", "resolved_standards": ["ICD10"],
        "confidence": 0.9, "reason": "dictionary"}


def _local_state(tables, replay=None):
    state = _state(tables, replay)
    state["batch_metadata"] = {"tables": {"events": {"itemid": "local"}}, "format": "csv"}
    return state


def _local_tables(ids, dictionary_ids):
    return {
        "EVENTS": pd.DataFrame({"itemid": ids}),
        "D_ITEMS": pd.DataFrame({"itemid": dictionary_ids, "code": ["100"] * len(dictionary_ids)}),
    }


def test_local_join_is_replayed_without_the_model(monkeypatch):
    calls = []
    monkeypatch.setattr("app.agents.mapping.resolve_local_vocab_join", lambda *a, **k: calls.append(1) or dict(JOIN))
    tables = _local_tables(["1", "2"], ["1", "2"])
    state = _local_state(tables)
    first = MappingAgent(llm=StubLLM()).run(state)
    assert calls == [1] and "EVENTS.itemid" in first.output["local_vocab_joins"]

    snapshot = ms.build_snapshot(
        name="v1", source_name="hosp", execution_id="RUN-1", batch_folder=None, mapping_output=first.output,
        tables=tables, batch_cfg=state["batch_metadata"], source_folder=None, cdm_version="5.4")
    ms.save_snapshot(snapshot)

    monkeypatch.setattr(
        "app.agents.mapping.resolve_local_vocab_join",
        lambda *a, **k: pytest.fail("the join must come from the snapshot"),
    )
    second = MappingAgent(llm=ForbiddenLLM()).run(
        _local_state(_local_tables(["2", "3", "1"], ["1", "2", "3"]), replay={"name": "v1"}))
    assert second.output["local_vocab_joins"]["EVENTS.itemid"]["join_table"] == "D_ITEMS"
    assert second.output["replay"]["reused"]["local_joins"] == 1
    assert second.output["local_vocab_join_failures"] == {}


def test_replayed_join_that_does_not_fit_the_new_batch_is_rejected_and_reported(monkeypatch):
    monkeypatch.setattr("app.agents.mapping.resolve_local_vocab_join", lambda *a, **k: dict(JOIN))
    tables = _local_tables(["1", "2"], ["1", "2"])
    state = _local_state(tables)
    first = MappingAgent(llm=StubLLM()).run(state)
    ms.save_snapshot(ms.build_snapshot(
        name="v1", source_name="hosp", execution_id="RUN-1", batch_folder=None, mapping_output=first.output,
        tables=tables, batch_cfg=state["batch_metadata"], source_folder=None, cdm_version="5.4"))

    unrelated = _local_tables(["7", "8", "9"], ["1", "2"])  # 0% key overlap on this batch
    second = MappingAgent(llm=ForbiddenLLM()).run(_local_state(unrelated, replay={"name": "v1"}))
    assert "EVENTS.itemid" in second.output["local_vocab_join_failures"]
    assert second.output["replay"]["rejected"][0]["kind"] == "local_join"

    with pytest.raises(ms.MappingReplayError, match="was rejected"):
        MappingAgent(llm=ForbiddenLLM()).run(
            _local_state(unrelated, replay={"name": "v1", "on_mismatch": "fail"}))


def test_a_join_that_had_failed_in_the_snapshot_is_not_asked_again(monkeypatch):
    monkeypatch.setattr("app.agents.mapping.resolve_local_vocab_join", lambda *a, **k: None)  # model finds nothing
    tables = _local_tables(["1"], ["1"])
    state = _local_state(tables)
    first = MappingAgent(llm=StubLLM()).run(state)
    assert "EVENTS.itemid" in first.output["local_vocab_join_failures"]
    ms.save_snapshot(ms.build_snapshot(
        name="v1", source_name="hosp", execution_id="RUN-1", batch_folder=None, mapping_output=first.output,
        tables=tables, batch_cfg=state["batch_metadata"], source_folder=None, cdm_version="5.4"))

    monkeypatch.setattr(
        "app.agents.mapping.resolve_local_vocab_join", lambda *a, **k: pytest.fail("must not be asked again"))
    second = MappingAgent(llm=ForbiddenLLM()).run(_local_state(tables, replay={"name": "v1"}))
    assert "replayed" in second.output["local_vocab_join_failures"]["EVENTS.itemid"].lower()
