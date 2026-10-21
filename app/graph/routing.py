"""
Conditional edges: transitions, retry/loop logic. Every stage transition
checks for a failure_event first - if any stage's node caught an
exception (or, for validation, a real DQD FAIL), the run routes to
root_cause instead of continuing, regardless of which stage failed.
"""
from __future__ import annotations


def after_profiling(state: dict) -> str:
    """A caught exception routes to root_cause. Otherwise: no new batch
    found -> stop the run cleanly, no error; else continue to mapping."""
    if state.get("failure_event"):
        return "root_cause"
    status = state.get("profiling_output", {}).get("status")
    return "stop" if status == "NOTHING_TO_PROCESS" else "mapping"


def after_mapping(state: dict) -> str:
    return "root_cause" if state.get("failure_event") else "transformation"


def after_transformation(state: dict) -> str:
    return "root_cause" if state.get("failure_event") else "loading"


def after_loading(state: dict) -> str:
    return "root_cause" if state.get("failure_event") else "validation"


def after_validation(state: dict) -> str:
    """Validation PASS -> promote OMOP_TEMP to OMOP_FINAL. FAIL (or a
    caught exception) -> root_cause."""
    if state.get("failure_event"):
        return "root_cause"
    return "promote" if state.get("validation_passed") else "root_cause"


def after_root_cause(state: dict) -> str:
    """Always routes to the Coordinator, which makes the actual
    resume/stop decision (retry budget + translating the recommended
    action into a concrete stage) - see app/agents/coordinator.py."""
    return "coordinator"


def after_coordinator(state: dict) -> str:
    """Reads the Coordinator's decision - validated against the real
    graph node names, never trusted blindly."""
    next_stage = state.get("next_stage")
    valid_stages = {"profiling", "mapping", "transformation", "loading", "validation"}
    return next_stage if next_stage in valid_stages else "stop"
