"""
Validation Agent (architecture doc v6, section 13 + DQD decision).
Orchestrates and interprets DQD - it does not implement its own parallel
collection of mapping/type/quality validators. Runs strictly against
OMOP_TEMP, which was truncated then loaded with only the current batch.
"""
from __future__ import annotations

from typing import Any

from app.agents.base import BaseAgent
from app.schemas.agent_result import AgentResult, AgentStatus
from app.schemas.failure_event import FailureEvent
from app.tools.validation.dqd_check import run_dqd_checks, summarize_dqd_result


class ValidationAgent(BaseAgent):
    name = "validation_agent"
    stage = "validation"

    def run(self, state: dict[str, Any]) -> AgentResult:
        execution_id = state["execution_id"]

        raw_dqd_result = run_dqd_checks(execution_id)
        summary = summarize_dqd_result(raw_dqd_result)

        status = AgentStatus.SUCCESS if summary["passed"] else AgentStatus.FAIL

        if not summary["passed"]:
            state["failure_event"] = FailureEvent(
                execution_id=execution_id,
                stage="validation",
                operation="dqd",
                status="FAILURE",
                error_type="DQDFatalCheckFailure",
                message=f"{summary['failed_fatal']} FATAL DQD check(s) failed out of {summary['total_checks']}.",
                inputs={"details": summary.get("details", {}).get("FATAL", [])[:20]},  # cap payload size
            )

        result = AgentResult(
            execution_id=execution_id,
            agent_name=self.name,
            status=status,
            output=summary,
            tools_used=["run_dqd_checks", "summarize_dqd_result"],
            reasoning_summary=(
                f"DQD ran {summary['total_checks']} checks; "
                f"{summary['failed_fatal']} FATAL failures "
                f"({'PASS' if summary['passed'] else 'FAIL'})."
            ),
        )
        return self.persist(result)
