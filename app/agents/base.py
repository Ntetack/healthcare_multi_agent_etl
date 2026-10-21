"""
Shared base for the seven agents. An Agent reasons/decides/plans; it
calls Tools to actually read/write/search/transform/validate
(architecture doc v6, section 5). This base class only standardizes the
boilerplate (LLM access, AgentResult persistence) - each agent's `run()`
holds its actual reasoning/tool-orchestration logic.
"""
from __future__ import annotations

import functools
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from app.models.factory import get_llm
from app.schemas.agent_result import AgentResult, AgentStatus
from app.tools.common.io_utils import default_report, write_report, write_result
from app.tools.common.metrics import LLMUsage, append_metrics_record


def _is_rate_limit_error(exc: Exception) -> bool:
    """Detects rate-limit errors across LLM providers without importing
    every possible provider-specific exception class - checks the
    exception's own type name and message for the common signals
    (HTTP 429, 'TooManyRequests', 'RateLimit')."""
    name = type(exc).__name__
    message = str(exc)
    return (
        "TooManyRequests" in name
        or "RateLimit" in name
        or "429" in message
        or "rate limit" in message.lower()
    )


class _RetryingLLM:
    """Wraps an LLM's .invoke() with retry + exponential backoff for
    rate-limit errors specifically - transparent to every caller
    (Mapping, Profiling, etc. all just call self.llm.invoke(prompt) as
    before, no call site needs to change). Some agents (Mapping's
    per-contributing-source-table resolution especially) make many LLM
    calls in quick succession, and a single rate-limited request would
    otherwise crash the entire pipeline run even though the SAME
    request would likely succeed a few seconds later. Non-rate-limit
    errors are NOT retried - they propagate immediately, since retrying
    a genuinely broken request (bad prompt, invalid API key, etc.)
    would only waste time before failing anyway."""

    def __init__(
        self,
        inner: Any,
        max_retries: int = 5,
        base_delay_seconds: float = 2.0,
        usage: LLMUsage | None = None,
    ):
        self._inner = inner
        self._max_retries = max_retries
        self._base_delay_seconds = base_delay_seconds
        # Shared with the owning agent, which resets it at each run().
        self._usage = usage if usage is not None else LLMUsage()

    def invoke(self, *args, **kwargs):
        for attempt in range(self._max_retries + 1):
            started = time.perf_counter()
            try:
                response = self._inner.invoke(*args, **kwargs)
            except Exception as exc:
                self._usage.llm_seconds += time.perf_counter() - started
                self._usage.failed_calls += 1
                if not _is_rate_limit_error(exc) or attempt == self._max_retries:
                    raise
                delay = self._base_delay_seconds * (2 ** attempt)
                self._usage.rate_limit_retries += 1
                self._usage.rate_limit_wait_seconds += delay
                time.sleep(delay)
            else:
                self._usage.llm_seconds += time.perf_counter() - started
                self._usage.add_response(response)
                return response

    def __getattr__(self, name):
        # Delegates any OTHER attribute access (e.g. .model_name) to the
        # real underlying LLM object - only .invoke() itself is wrapped.
        return getattr(self._inner, name)


def _instrument_run(run):
    """Wraps a subclass's run() so that every execution is timed and its
    LLM usage recorded, without any change inside the agents. The record
    is written even when run() raises (status 'EXCEPTION'), so a crashed
    attempt still shows up in the cost of the run."""

    @functools.wraps(run)
    def wrapper(self, state):
        self._begin_metrics(state)
        status = "EXCEPTION"
        try:
            result = run(self, state)
            status = getattr(result.status, "value", str(result.status))
            return result
        finally:
            self._end_metrics(state, status)

    return wrapper


class BaseAgent(ABC):
    name: str = "base_agent"
    stage: str = "base"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        run = cls.__dict__.get("run")
        if run is not None and not getattr(run, "__isabstractmethod__", False):
            cls.run = _instrument_run(run)

    def __init__(self, llm=None):
        self._llm = llm
        self._usage = LLMUsage()
        self._t0: float | None = None
        self._started_at: datetime | None = None
        self._operation: str | None = None

    @property
    def llm(self):
        """Lazily builds the LLM on first access, so instantiating an
        agent (e.g. when wiring the LangGraph nodes) never requires an
        API key unless the agent actually calls the model. Wrapped in
        _RetryingLLM so every agent gets rate-limit resilience for
        free, without any change to how they call it."""
        if self._llm is None:
            self._llm = _RetryingLLM(get_llm(), usage=self._usage)
        return self._llm

    # ------------------------------------------------------------------
    # Metrics: execution time and LLM token usage of one run().
    # An LLM injected through the constructor (tests) is used as is and is
    # not tracked, so stubs keep behaving exactly as before.
    # ------------------------------------------------------------------
    def _begin_metrics(self, state: Any) -> None:
        self._usage.reset()
        self._t0 = time.perf_counter()
        self._started_at = datetime.now(timezone.utc)
        # Loading runs twice per pipeline (load_temp, promote_final).
        self._operation = state.get("loading_mode") if isinstance(state, dict) else None

    def _metrics_snapshot(self) -> dict[str, Any] | None:
        if self._t0 is None:
            return None
        return {
            "agent": self.name,
            "stage": self.stage,
            "operation": self._operation,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "duration_seconds": round(time.perf_counter() - self._t0, 3),
            "llm": self._usage.as_dict(),
        }

    def _end_metrics(self, state: Any, status: str) -> None:
        snapshot = self._metrics_snapshot()
        if snapshot is None or not isinstance(state, dict):
            return
        retry_counts = state.get("retry_counts") or {}
        snapshot["status"] = status
        # retry_counts is incremented when a failure is analysed, so a first
        # attempt sees 0 here.
        snapshot["attempt"] = retry_counts.get(self.stage, 0) + 1
        append_metrics_record(state.get("execution_id"), snapshot)

    @abstractmethod
    def run(self, state: dict[str, Any]) -> AgentResult:
        """Executes this agent's step. Receives the shared LangGraph state,
        returns a populated AgentResult. Must not raise for expected
        business failures - emit a FailureEvent / AgentStatus.FAIL instead
        (see app/schemas/failure_event.py); real exceptions are for
        genuinely unexpected technical errors."""
        raise NotImplementedError

    def persist(
        self, result: AgentResult, report_markdown: str | None = None, stage_override: str | None = None
    ) -> AgentResult:
        """Writes result.json/report.md for this agent's stage. Some
        agents (Loading, specifically) perform genuinely distinct
        OPERATIONS within the same stage (load_temp vs promote_final) -
        `stage_override` lets those write to separate paths, so a later
        operation's result never silently overwrites an earlier one's
        (both are worth keeping - load_temp's per-table row-drop
        diagnostics are NOT reproduced in promote_final's own result)."""
        stage = stage_override or self.stage
        # Snapshot at write time: the final figures are the ones appended
        # to metrics.jsonl when run() returns (a few ms later).
        snapshot = self._metrics_snapshot()
        if snapshot is not None:
            result.metadata["metrics"] = snapshot
        write_result(result, stage)
        write_report(result.execution_id, stage, report_markdown or default_report(result))
        return result
