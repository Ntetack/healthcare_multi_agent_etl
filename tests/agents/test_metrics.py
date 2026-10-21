"""Execution metrics: token extraction, LLM wrapper counters, per-run timing
and the run-level summary. No real model and no database involved."""
from __future__ import annotations

import json
import time
from types import SimpleNamespace

import pytest

from app.agents.base import BaseAgent, _RetryingLLM
from app.schemas.agent_result import AgentResult, AgentStatus
from app.tools.common import io_utils
from app.tools.common.metrics import (
    LLMUsage,
    extract_token_usage,
    format_summary,
    load_metrics_records,
    summarize_run,
)


def _response(input_tokens=10, output_tokens=5, reasoning=0):
    return SimpleNamespace(
        content="{}",
        usage_metadata={
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "output_token_details": {"reasoning": reasoning},
        },
    )


class _ScriptedLLM:
    """Returns / raises the scripted items in order."""

    def __init__(self, *items):
        self.items = list(items)

    def invoke(self, *_args, **_kwargs):
        item = self.items.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture(autouse=True)
def runs_in_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(io_utils, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(time, "sleep", lambda _s: None)
    return tmp_path / "runs"


def test_extract_usage_from_langchain_usage_metadata():
    assert extract_token_usage(_response(100, 40, reasoning=25)) == (100, 40, 140, 25)


def test_extract_usage_falls_back_to_openai_style_token_usage():
    response = SimpleNamespace(
        usage_metadata=None,
        response_metadata={
            "token_usage": {
                "prompt_tokens": 7,
                "completion_tokens": 3,
                "total_tokens": 10,
                "completion_tokens_details": {"reasoning_tokens": 2},
            }
        },
    )
    assert extract_token_usage(response) == (7, 3, 10, 2)


def test_extract_usage_returns_none_when_provider_reports_nothing():
    assert extract_token_usage(SimpleNamespace(usage_metadata=None, response_metadata={})) is None


def test_wrapper_accumulates_tokens_and_calls():
    usage = LLMUsage()
    llm = _RetryingLLM(_ScriptedLLM(_response(10, 5), _response(20, 8)), usage=usage)
    llm.invoke("a")
    llm.invoke("b")
    assert (usage.calls, usage.input_tokens, usage.output_tokens, usage.total_tokens) == (2, 30, 13, 43)


def test_wrapper_counts_rate_limit_retries_and_only_bills_the_success():
    usage = LLMUsage()
    llm = _RetryingLLM(
        _ScriptedLLM(Exception("429 rate limit"), Exception("429 rate limit"), _response(10, 5)),
        usage=usage,
    )
    llm.invoke("a")
    assert usage.rate_limit_retries == 2
    assert usage.failed_calls == 2
    assert usage.calls == 1
    assert usage.total_tokens == 15
    assert usage.rate_limit_wait_seconds == 2.0 + 4.0  # 2 s then 4 s backoff


def test_wrapper_flags_calls_without_token_counts():
    usage = LLMUsage()
    llm = _RetryingLLM(_ScriptedLLM(SimpleNamespace(usage_metadata=None, response_metadata={})), usage=usage)
    llm.invoke("a")
    assert usage.calls == 1 and usage.calls_without_usage == 1 and usage.total_tokens == 0


class _Agent(BaseAgent):
    name = "demo_agent"
    stage = "mapping"

    def __init__(self, llm_items=(), fail=False):
        super().__init__()
        self._llm = _RetryingLLM(_ScriptedLLM(*llm_items), usage=self._usage)
        self._fail = fail

    def run(self, state):
        if self._fail:
            raise RuntimeError("boom")
        self.llm.invoke("p")
        result = AgentResult(execution_id=state["execution_id"], agent_name=self.name, status=AgentStatus.SUCCESS)
        return self.persist(result)


def test_run_is_timed_and_recorded(runs_in_tmp):
    agent = _Agent([_response(10, 5)])
    result = agent.run({"execution_id": "RUN-T"})

    # embedded in result.json through persist()
    embedded = result.metadata["metrics"]
    assert embedded["llm"]["total_tokens"] == 15 and embedded["agent"] == "demo_agent"

    # appended to metrics.jsonl when run() returns
    (record,) = load_metrics_records("RUN-T")
    assert record["status"] == "SUCCESS" and record["attempt"] == 1
    assert record["duration_seconds"] >= 0
    assert record["llm"]["calls"] == 1 and record["llm"]["input_tokens"] == 10
    assert json.loads((runs_in_tmp / "RUN-T" / "mapping" / "result.json").read_text())["metadata"]["metrics"]


def test_counters_are_reset_between_runs():
    agent = _Agent([_response(10, 5), _response(1, 1)])
    agent.run({"execution_id": "RUN-R"})
    agent.run({"execution_id": "RUN-R"})
    first, second = load_metrics_records("RUN-R")
    assert first["llm"]["total_tokens"] == 15
    assert second["llm"]["total_tokens"] == 2  # not 17


def test_crashed_run_is_still_recorded_and_exception_propagates():
    agent = _Agent(fail=True)
    with pytest.raises(RuntimeError):
        agent.run({"execution_id": "RUN-X"})
    (record,) = load_metrics_records("RUN-X")
    assert record["status"] == "EXCEPTION"


def test_attempt_number_follows_retry_counts():
    agent = _Agent([_response(), _response()])
    agent.run({"execution_id": "RUN-A", "retry_counts": {}})
    agent.run({"execution_id": "RUN-A", "retry_counts": {"mapping": 1}})
    assert [r["attempt"] for r in load_metrics_records("RUN-A")] == [1, 2]


def test_injected_stub_llm_is_left_untouched():
    from unittest.mock import MagicMock

    stub = MagicMock()
    agent = _Agent()
    agent._llm = stub
    assert agent.llm is stub


def test_missing_execution_id_does_not_break_the_run(runs_in_tmp):
    agent = _Agent([_response()])
    # persist() needs an execution id, so use a result-free agent here
    class Quiet(BaseAgent):
        name, stage = "quiet", "coordinator"

        def run(self, state):
            return AgentResult(execution_id="x", agent_name=self.name, status=AgentStatus.SUCCESS)

    Quiet().run({})
    assert not list(runs_in_tmp.glob("**/metrics.jsonl")) if runs_in_tmp.exists() else True


def test_summary_aggregates_retries_and_totals():
    ok = _Agent([_response(10, 5)])
    ok.run({"execution_id": "RUN-S"})
    bad = _Agent([_response(20, 10)])
    bad.name = "demo_agent"
    bad.run({"execution_id": "RUN-S", "retry_counts": {"mapping": 1}})

    summary = summarize_run("RUN-S")
    (row,) = summary["agents"]
    assert row["executions"] == 2 and row["llm_calls"] == 2
    assert row["input_tokens"] == 30 and row["total_tokens"] == 45
    assert summary["totals"]["total_tokens"] == 45
    table = format_summary(summary)
    assert "demo_agent" in table and "**Total**" in table
