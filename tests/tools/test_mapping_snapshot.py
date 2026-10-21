"""Mapping snapshots: files, compatibility checks, saving policy and the
--save-mapping / --replay-mapping options of app/main.py. No database."""
from __future__ import annotations

import json
import sys

import pandas as pd
import pytest

from app import main as main_module
from app.tools.mapping import mapping_snapshot as ms


@pytest.fixture(autouse=True)
def snapshot_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("MAPPING_SNAPSHOT_DIR", str(tmp_path / "mappings"))
    monkeypatch.setattr(ms, "get_vocabulary_version", lambda: "v-test")
    return tmp_path


def _tables(**cols):
    return {name: pd.DataFrame({c: ["x"] for c in columns}) for name, columns in cols.items()}


def _snapshot(tables=None, **overrides):
    tables = tables if tables is not None else _tables(PATIENTS=["gender", "birth_year"])
    mapping_output = {
        "per_table": {},
        "structural_target_mappings": [
            {"target_table": "person", "target_field": "year_of_birth", "source_table": "PATIENTS",
             "source_field": "birth_year", "source_value": None, "confidence": 0.9, "reason": "r"},
        ],
        "plain_field_scopes": [{"target_table": "person", "source_table": None}],
        "vocab_field_sources": [],
        "local_vocab_joins": {},
        "local_vocab_join_failures": {},
    }
    snapshot = ms.build_snapshot(
        name="v1", source_name="hosp", execution_id="RUN-1", batch_folder="data/raw/hosp/batch1",
        mapping_output=mapping_output, tables=tables,
        batch_cfg={"tables": {"patients": {"gender": "Gender"}}}, source_folder=None,
        llm_provider="openrouter", llm_model="m", cdm_version="5.4", vocabulary_version="v-test",
    )
    snapshot.update(overrides)
    return snapshot


def _plan(snapshot, tables=None, batch_cfg=None, source="hosp", **kwargs):
    return ms.ReplayPlan(
        snapshot, tables=tables if tables is not None else _tables(PATIENTS=["gender", "birth_year"]),
        batch_cfg=batch_cfg if batch_cfg is not None else {"tables": {"patients": {"gender": "Gender"}}},
        source_name=source, cdm_version="5.4", vocabulary_version="v-test", **kwargs,
    )


# ---------------------------------------------------------------- files
@pytest.mark.parametrize("bad", ["../escape", "a/b", "", ".hidden", "with space"])
def test_unsafe_names_are_refused(bad):
    with pytest.raises(ValueError):
        ms.snapshot_path("hosp", bad)
    with pytest.raises(ValueError):
        ms.snapshot_path(bad, "v1")


def test_save_then_load_round_trip_and_overwrite_policy():
    path = ms.save_snapshot(_snapshot())
    assert path.name == "v1.json" and path.parent.name == "hosp"
    assert ms.load_snapshot("hosp", "v1")["created_from"]["batch"] == "batch1"
    with pytest.raises(FileExistsError):
        ms.save_snapshot(_snapshot())
    ms.save_snapshot(_snapshot(), overwrite=True)


def test_loading_an_unknown_snapshot_says_where_it_looked():
    with pytest.raises(FileNotFoundError, match="not found for source 'hosp'"):
        ms.load_snapshot("hosp", "nope")


def test_snapshot_keeps_the_complete_mapping_and_the_frozen_decisions():
    snap = _snapshot()
    assert snap["mapping"]["structural_target_mappings"]
    assert snap["frozen"]["plain_fields"][0]["source_field"] == "birth_year"
    assert snap["fingerprint"]["tables"] == {"patients": ["birth_year", "gender"]}


# ---------------------------------------------------------- compatibility
def test_other_source_is_refused():
    with pytest.raises(ms.MappingReplayError, match="belongs to source 'hosp', not 'elsewhere'"):
        _plan(_snapshot(), source="elsewhere")


def test_unknown_format_and_other_cdm_version_are_refused():
    with pytest.raises(ms.MappingReplayError, match="unsupported snapshot format"):
        _plan(_snapshot(snapshot_format=99))
    snap = _snapshot()
    snap["environment"]["cdm_version"] = "5.3"
    with pytest.raises(ms.MappingReplayError, match="CDM version differs"):
        _plan(snap)


def test_drift_is_reported_as_warnings_not_errors(tmp_path):
    plan = _plan(
        _snapshot(),
        tables=_tables(PATIENTS=["gender", "yob"], NEWTABLE=["a"]),
        batch_cfg={"tables": {"patients": {"gender": "Gender", "yob": "X"}}},
    )
    text = " | ".join(plan.report["warnings"])
    assert "not in the snapshot's batch: newtable" in text
    assert "new column(s) yob" in text and "missing column(s) birth_year" in text
    assert "coded-field declarations differ" in text


def test_vocabulary_release_and_curated_file_changes_are_warned(tmp_path):
    source_folder = tmp_path / "src"
    source_folder.mkdir()
    (source_folder / "race.csv").write_text("a,b\n1,2\n")
    cfg = {"tables": {}, "fixed_value_mappings": {"person": {"race_concept_id": {"mapping_file": "race.csv"}}}}
    tables = _tables(PATIENTS=["gender"])
    snap = ms.build_snapshot(
        name="v1", source_name="hosp", execution_id="R", batch_folder=None, mapping_output={},
        tables=tables, batch_cfg=cfg, source_folder=source_folder, cdm_version="5.4", vocabulary_version="OLD",
    )
    (source_folder / "race.csv").write_text("a,b\n1,3\n")  # curated file edited afterwards
    plan = ms.ReplayPlan(
        snap, tables=tables, batch_cfg=cfg, source_name="hosp", source_folder=source_folder,
        cdm_version="5.4", vocabulary_version="NEW",
    )
    text = " | ".join(plan.report["warnings"])
    assert "vocabulary release differs" in text and "curated mapping file 'race.csv' changed" in text


def test_invalid_policy_is_rejected():
    with pytest.raises(ValueError):
        _plan(_snapshot(), on_mismatch="maybe")


# ------------------------------------------------------------ saving policy
def _final_state(**overrides):
    state = {
        "source_name": "hosp", "execution_id": "RUN-9", "source_path": "data/raw/hosp/b9",
        "mapping_output": _snapshot()["mapping"], "_raw_tables": _tables(PATIENTS=["gender"]),
        "batch_metadata": {"tables": {}}, "promote_output": {"status": "ok"}, "failure_event": None,
    }
    state.update(overrides)
    return state


def test_a_run_that_did_not_reach_promotion_is_not_saved():
    path, message = ms.save_snapshot_from_final_state(_final_state(promote_output=None), "v1")
    assert path is None and "did not reach promotion" in message
    path, _ = ms.save_snapshot_from_final_state(_final_state(failure_event=object()), "v1")
    assert path is None
    assert not (ms.snapshot_dir() / "hosp").exists()


def test_a_promoted_run_is_saved_with_its_provenance(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "qwen/test-model")
    path, message = ms.save_snapshot_from_final_state(_final_state(), "v1")
    assert message == "saved" and path.exists()
    saved = json.loads(path.read_text())
    assert saved["created_from"]["execution_id"] == "RUN-9"
    assert saved["created_from"]["llm_model"] == "qwen/test-model"
    assert saved["environment"]["vocabulary_version"] == "v-test"


# --------------------------------------------------------------------- CLI
class _FakeWorkflow:
    def __init__(self, final_state):
        self.final_state, self.initial_state = final_state, None

    def invoke(self, initial_state):
        self.initial_state = initial_state
        return self.final_state


@pytest.fixture
def cli(monkeypatch):
    def run(argv, final_state=None):
        workflow = _FakeWorkflow(final_state or _final_state())
        monkeypatch.setattr(main_module, "build_workflow", lambda: workflow)
        monkeypatch.setattr(main_module, "_build_execution_id", lambda source: "RUN-CLI")
        monkeypatch.setattr(main_module, "write_summary", lambda *a, **k: None)
        monkeypatch.setattr(main_module, "summarize_run", lambda *a, **k: {"agents": []})
        monkeypatch.setattr(sys, "argv", ["main", *argv])
        main_module.main()
        return workflow

    return run


def test_cli_replay_flag_reaches_the_state(cli):
    ms.save_snapshot(_snapshot())
    workflow = cli(["--source", "hosp", "--replay-mapping", "v1", "--replay-on-mismatch", "fail"])
    assert workflow.initial_state["mapping_replay"] == {"name": "v1", "on_mismatch": "fail"}


def test_cli_without_replay_flag_adds_nothing_to_the_state(cli):
    assert "mapping_replay" not in cli(["--source", "hosp"]).initial_state


def test_cli_unknown_snapshot_stops_before_the_run(cli):
    with pytest.raises(SystemExit):
        cli(["--source", "hosp", "--replay-mapping", "ghost"])


def test_cli_existing_snapshot_is_not_overwritten_unless_asked(cli):
    ms.save_snapshot(_snapshot())
    with pytest.raises(SystemExit):
        cli(["--source", "hosp", "--save-mapping", "v1"])
    cli(["--source", "hosp", "--save-mapping", "v1", "--overwrite-mapping"])  # allowed


def test_cli_saves_after_a_promoted_run_and_says_so_otherwise(cli, capsys):
    cli(["--source", "hosp", "--save-mapping", "fresh"])
    assert ms.snapshot_path("hosp", "fresh").exists()
    assert "Mapping snapshot saved" in capsys.readouterr().out

    cli(["--source", "hosp", "--save-mapping", "never"], final_state=_final_state(promote_output=None))
    assert not ms.snapshot_path("hosp", "never").exists()
    assert "NOT saved" in capsys.readouterr().out


def test_a_vocabulary_field_keeps_every_source_column_of_the_snapshot():
    tables = _tables(CHARTEVENTS=["valueuom"], LABEVENTS=["valueuom"], PROCEDUREEVENTS_MV=["valueuom"])
    snap = _snapshot(tables=tables)
    snap["frozen"]["vocab_sources"] = [
        {"target_table": "measurement", "target_field": "unit_concept_id", "source_table": t, "source_field": "valueuom"}
        for t in ("CHARTEVENTS", "LABEVENTS", "PROCEDUREEVENTS_MV")
    ]
    plan = _plan(snap, tables=tables)
    assert plan.vocab_sources("measurement", "unit_concept_id") == [
        ("CHARTEVENTS", "valueuom"), ("LABEVENTS", "valueuom"), ("PROCEDUREEVENTS_MV", "valueuom"),
    ]
    assert plan.vocab_source("measurement", "unit_concept_id") == ("CHARTEVENTS", "valueuom")


def test_a_missing_snapshot_column_is_left_out_without_hiding_the_others():
    tables = _tables(CHARTEVENTS=["valueuom"], LABEVENTS=["other"])
    snap = _snapshot(tables=tables)
    snap["frozen"]["vocab_sources"] = [
        {"target_table": "measurement", "target_field": "unit_concept_id", "source_table": t, "source_field": "valueuom"}
        for t in ("CHARTEVENTS", "LABEVENTS")
    ]
    plan = _plan(snap, tables=tables)
    assert plan.vocab_sources("measurement", "unit_concept_id") == [("CHARTEVENTS", "valueuom")]
    assert plan.report["fallbacks"]
