"""
Root Cause Analyzer (RCA) - transversal by design: any FailureEvent from
any stage can be routed here. Analyzes the probable cause and severity,
and recommends ONE action - it never executes a fix itself, and it
never blindly retries a failure that looks like a deterministic code or
configuration defect (retrying identical inputs against identical code
produces the same failure; only genuinely transient or tolerable issues
warrant a retry/resume).

Currently wired for the one path the graph actually routes here today:
a failing DQD validation (see app/agents/validation.py, which builds the
FailureEvent on FAIL). Routing unhandled exceptions from other stages
(profiling/mapping/transformation/loading) here as well would need those
stages wrapped in the graph with their own conditional edges - not yet
done, and explicitly NOT claimed as covered.
"""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.prompts.root_cause_prompt import ROOT_CAUSE_PROMPT
from app.schemas.agent_result import AgentResult, AgentStatus
from app.schemas.failure_event import FailureEvent
from app.tools.common.llm_utils import parse_json_response
from app.tools.data.folder_watcher import mark_status

RECOMMENDED_ACTIONS = {"retry", "recompute_mapping", "resume_stage", "human_intervention", "stop_run"}
VALID_RESUME_STAGES = {"mapping", "transformation", "loading", "validation"}
TERMINAL_ACTIONS = {"human_intervention", "stop_run"}


class RootCauseAnalyzerAgent(BaseAgent):
    name = "root_cause_analyzer"
    stage = "root_cause"

    def run(self, state: dict[str, Any]) -> AgentResult:
        event: FailureEvent = state["failure_event"]
        retry_count = state.get("retry_counts", {}).get(event.stage, 0)

        analysis = self._analyze(event, retry_count)

        source_path = state.get("source_path")
        if analysis["recommended_action"] in TERMINAL_ACTIONS and source_path:
            mark_status(state["source_name"], source_path, "FAILED")

        result = AgentResult(
            execution_id=state["execution_id"],
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            input_summary=event.model_dump(mode="json"),
            output=analysis,
            tools_used=["llm_reasoning"],
            reasoning_summary=(
                f"Analyzed failure at stage '{event.stage}' (severity: {analysis['severity']}); "
                f"recommending '{analysis['recommended_action']}'."
            ),
        )
        return self.persist(result)

    def _analyze(self, event: FailureEvent, retry_count: int) -> dict:
        prompt = ROOT_CAUSE_PROMPT.format(
            failure_details=event.model_dump_json(indent=2),
            retry_count=retry_count,
            max_retries=2,
        )
        response = self.llm.invoke(prompt)
        try:
            parsed = parse_json_response(response.content)
        except ValueError:
            # LLM reasoning unavailable/unparseable - fail safe toward
            # human review rather than guessing an action.
            return {
                "probable_cause": "LLM analysis unavailable (parse error).",
                "severity": "serious",
                "recommended_action": "human_intervention",
                "resume_from_stage": None,
            }

        action = parsed.get("recommended_action")
        if action not in RECOMMENDED_ACTIONS:
            action = "human_intervention"

        resume_stage = parsed.get("resume_from_stage")
        if resume_stage not in VALID_RESUME_STAGES:
            resume_stage = None

        return {
            "probable_cause": parsed.get("probable_cause", ""),
            "severity": parsed.get("severity", "serious"),
            "recommended_action": action,
            "resume_from_stage": resume_stage,
        }
