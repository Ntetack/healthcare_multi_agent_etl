"""
Wraps each Agent as a LangGraph node: a plain function of
(state) -> partial state update, calling agent.run() and merging its
AgentResult.output back into state for the next node.

Every stage-running node uses _safe_run(): any unhandled exception is
caught and converted into a FailureEvent rather than crashing the whole
pipeline - this is what lets the Root Cause Analyzer intervene on ANY
stage's failure, not just a failing DQD validation. On success, a node
explicitly clears failure_event (sets it to None) so a stale failure
from an earlier retry never leaks into the next stage's routing check.
"""
from __future__ import annotations

import subprocess

from app.agents.coordinator import CoordinatorAgent
from app.agents.loading import LoadingAgent
from app.agents.mapping import MappingAgent
from app.agents.profiling import ProfilingAgent
from app.agents.root_cause import RootCauseAnalyzerAgent
from app.agents.transformation import TransformationAgent
from app.agents.validation import ValidationAgent
from app.schemas.agent_result import AgentResult
from app.schemas.failure_event import FailureEvent

coordinator = CoordinatorAgent()
profiling_agent = ProfilingAgent()
mapping_agent = MappingAgent()
transformation_agent = TransformationAgent()
validation_agent = ValidationAgent()
root_cause_agent = RootCauseAnalyzerAgent()
loading_agent = LoadingAgent()


def _safe_run(agent, state: dict, stage_name: str) -> tuple[AgentResult | None, FailureEvent | None]:
    """Runs an agent, converting EITHER an unhandled exception OR a
    controlled FAIL status (an agent returning normally, but with
    status != SUCCESS - e.g. Loading's own "Could not resolve
    person_source_value" failure) into a FailureEvent. Both must route
    to root_cause identically - a clean, well-reported failure is not
    somehow SAFER to ignore than a crash; if anything, it deserves MORE
    trust, since the agent diagnosed its own failure precisely instead
    of throwing. Confirmed in production: without this check, a Loading
    failure like this one was silently treated as a success, letting
    the pipeline reach Validation (which trivially "passed" against an
    empty/unchanged OMOP_TEMP) and the whole run report SUCCESS despite
    nothing having been loaded at all.

    Returns (result, failure_event) - exactly one of the two is None."""
    try:
        result = agent.run(state)
    except Exception as exc:  # noqa: BLE001 - deliberately broad: any agent failure must route to RCA, not crash
        message = str(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            # str(exc) alone is a generic "returned non-zero exit status"
            # message - the ACTUAL reason (e.g. the R script's real
            # error) lives in stderr/stdout, already captured by
            # subprocess.run(capture_output=True) but never surfaced
            # anywhere until now.
            details = (exc.stderr or exc.stdout or "").strip()
            if details:
                message = f"{message}\n--- subprocess output ---\n{details[-3000:]}"
        event = FailureEvent(
            execution_id=state.get("execution_id", "unknown"),
            stage=stage_name,
            operation="run",
            status="FAILURE",
            error_type=type(exc).__name__,
            message=message[:4000],
        )
        return None, event

    status = getattr(result, "status", None)
    status_value = getattr(status, "value", status)
    if isinstance(status_value, str) and status_value != "SUCCESS":
        existing = state.get("failure_event")
        if existing:
            # The agent already self-reported a richer diagnostic (e.g.
            # ValidationAgent sets this itself on a DQD FAIL) - never
            # overwrite it with a generic synthesized one.
            return result, existing
        message = ""
        if isinstance(result.output, dict):
            message = str(result.output.get("error") or result.output)
        else:
            message = str(result.output)
        event = FailureEvent(
            execution_id=state.get("execution_id", "unknown"),
            stage=stage_name,
            operation="run",
            status="FAILURE",
            error_type="AgentReportedFailure",
            message=message[:4000],
        )
        return result, event

    return result, None


def coordinator_node(state: dict) -> dict:
    result = coordinator.run(state)
    return {"next_stage": result.output["next_stage"]}


def profiling_node(state: dict) -> dict:
    result, failure = _safe_run(profiling_agent, state, "profiling")
    if failure:
        return {"failure_event": failure}
    return {
        "profiling_output": result.output,
        "source_path": state.get("source_path"),
        "_raw_tables": state.get("_raw_tables"),
        "batch_metadata": state.get("batch_metadata"),
        "failure_event": None,
    }


def mapping_node(state: dict) -> dict:
    result, failure = _safe_run(mapping_agent, state, "mapping")
    if failure:
        return {"failure_event": failure}
    return {
        "mapping_output": result.output,
        "_enriched_tables": state.get("_enriched_tables"),
        "failure_event": None,
    }


def transformation_node(state: dict) -> dict:
    result, failure = _safe_run(transformation_agent, state, "transformation")
    if failure:
        return {"failure_event": failure}
    return {
        "transformation_output": result.output,
        "_transformed_tables": state.get("_transformed_tables"),
        "failure_event": None,
    }


def loading_node(state: dict) -> dict:
    """Loads the current batch into OMOP_TEMP - runs BEFORE validation,
    since the DQD (Validation Agent) needs OMOP_TEMP already populated
    with this batch to validate it."""
    state["loading_mode"] = "load_temp"
    result, failure = _safe_run(loading_agent, state, "loading")
    if failure:
        return {"failure_event": failure}
    return {"loading_output": result.output, "failure_event": None}


def validation_node(state: dict) -> dict:
    """ValidationAgent sets state["failure_event"] itself on a DQD FAIL
    (a normal, expected outcome - not an exception); _safe_run also
    guards against the DQD subprocess itself crashing unexpectedly."""
    result, failure = _safe_run(validation_agent, state, "validation")
    if failure:
        return {"failure_event": failure}
    return {
        "validation_passed": result.status == "SUCCESS",
        "validation_output": result.output,
        "failure_event": state.get("failure_event"),  # set internally by ValidationAgent on DQD FAIL
    }


def root_cause_node(state: dict) -> dict:
    result = root_cause_agent.run(state)
    # Track attempts per failing stage, so after_root_cause's retry
    # budget (MAX_RETRIES) can actually trigger - without this, retries
    # never increment and a repeatedly-failing stage could loop
    # indefinitely between itself and root_cause.
    failing_stage = state["failure_event"].stage if state.get("failure_event") else "unknown"
    retry_counts = dict(state.get("retry_counts", {}))
    retry_counts[failing_stage] = retry_counts.get(failing_stage, 0) + 1
    return {"root_cause_output": result.output, "retry_counts": retry_counts}


def promote_final_node(state: dict) -> dict:
    """Appends OMOP_TEMP -> OMOP_FINAL - runs only after a passing DQD
    (see after_validation routing)."""
    state["loading_mode"] = "promote_final"
    result, failure = _safe_run(loading_agent, state, "promote_final")
    if failure:
        return {"failure_event": failure}
    return {"promote_output": result.output, "failure_event": None}
