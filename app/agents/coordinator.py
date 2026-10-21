"""
Coordinator Agent: the single place that decides which stage runs next,
in two situations:
  1. Starting a fresh run (no prior failure) -> always "profiling".
  2. Resuming after the Root Cause Analyzer has diagnosed a failure ->
     translates its recommendation (+ the retry budget for the failing
     stage) into a concrete next stage, or "stop".

This centralizes the retry-budget/resume-stage decision in ONE place
(as an auditable AgentResult, with `decisions` recorded) rather than
splitting it across routing functions - app/graph/routing.py's
conditional edges only read state["next_stage"] that this agent sets;
they don't make the decision themselves.
"""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.schemas.agent_result import AgentResult, AgentStatus

MAX_RETRIES_PER_STAGE = 2
VALID_STAGES = {"profiling", "mapping", "transformation", "loading", "validation"}


class CoordinatorAgent(BaseAgent):
    name = "coordinator"
    stage = "coordinator"

    def run(self, state: dict[str, Any]) -> AgentResult:
        root_cause_output = state.get("root_cause_output")

        if root_cause_output is None:
            next_stage = "profiling"
            decisions = ["Starting a new run at 'profiling'."]
        else:
            next_stage, decisions = self._decide_after_failure(state, root_cause_output)

        result = AgentResult(
            execution_id=state["execution_id"],
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            decisions=decisions,
            reasoning_summary=decisions[-1],
            output={"next_stage": next_stage},
        )
        return self.persist(result)

    def _decide_after_failure(self, state: dict[str, Any], root_cause_output: dict) -> tuple[str, list[str]]:
        failure_event = state.get("failure_event")
        failing_stage = failure_event.stage if failure_event else "unknown"
        retry_counts = state.get("retry_counts", {})
        attempts = retry_counts.get(failing_stage, 0)

        action = root_cause_output.get("recommended_action", "stop_run")
        resume_stage = root_cause_output.get("resume_from_stage")
        decisions = [f"Root Cause Analyzer recommended '{action}' for failing stage '{failing_stage}'."]

        if attempts >= MAX_RETRIES_PER_STAGE:
            decisions.append(f"Retry budget exhausted for '{failing_stage}' ({attempts}/{MAX_RETRIES_PER_STAGE}) - stopping.")
            return "stop", decisions

        if action in ("retry", "resume_stage") and resume_stage in VALID_STAGES:
            decisions.append(f"Resuming at '{resume_stage}' (attempt {attempts + 1}/{MAX_RETRIES_PER_STAGE}).")
            return resume_stage, decisions

        if action == "recompute_mapping":
            decisions.append(f"Recomputing mapping (attempt {attempts + 1}/{MAX_RETRIES_PER_STAGE}).")
            return "mapping", decisions

        decisions.append(f"'{action}' requires stopping the run for human review.")
        return "stop", decisions
