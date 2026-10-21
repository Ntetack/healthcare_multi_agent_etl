"""CoordinatorAgent tests - no LLM/DB needed, pure decision logic."""
from app.agents.coordinator import CoordinatorAgent, MAX_RETRIES_PER_STAGE
from app.schemas.failure_event import FailureEvent


def _agent():
    return CoordinatorAgent(llm=None)


def test_fresh_run_starts_at_profiling():
    state = {"execution_id": "RUN-1"}
    result = _agent().run(state)
    assert result.output["next_stage"] == "profiling"


def test_resumes_at_recommended_stage_within_budget():
    state = {
        "execution_id": "RUN-1",
        "failure_event": FailureEvent(execution_id="RUN-1", stage="mapping", operation="run",
                                       error_type="ValueError", message="x"),
        "retry_counts": {"mapping": 0},
        "root_cause_output": {"recommended_action": "resume_stage", "resume_from_stage": "mapping"},
    }
    result = _agent().run(state)
    assert result.output["next_stage"] == "mapping"


def test_recompute_mapping_action_routes_to_mapping():
    state = {
        "execution_id": "RUN-1",
        "failure_event": FailureEvent(execution_id="RUN-1", stage="mapping", operation="run",
                                       error_type="ValueError", message="x"),
        "retry_counts": {"mapping": 0},
        "root_cause_output": {"recommended_action": "recompute_mapping", "resume_from_stage": None},
    }
    result = _agent().run(state)
    assert result.output["next_stage"] == "mapping"


def test_human_intervention_stops():
    state = {
        "execution_id": "RUN-1",
        "failure_event": FailureEvent(execution_id="RUN-1", stage="loading", operation="run",
                                       error_type="ValueError", message="x"),
        "retry_counts": {"loading": 0},
        "root_cause_output": {"recommended_action": "human_intervention", "resume_from_stage": None},
    }
    result = _agent().run(state)
    assert result.output["next_stage"] == "stop"


def test_retry_budget_exhausted_stops_even_if_action_says_retry():
    state = {
        "execution_id": "RUN-1",
        "failure_event": FailureEvent(execution_id="RUN-1", stage="mapping", operation="run",
                                       error_type="ValueError", message="x"),
        "retry_counts": {"mapping": MAX_RETRIES_PER_STAGE},
        "root_cause_output": {"recommended_action": "retry", "resume_from_stage": "mapping"},
    }
    result = _agent().run(state)
    assert result.output["next_stage"] == "stop"


def test_invalid_resume_stage_falls_back_to_stop():
    state = {
        "execution_id": "RUN-1",
        "failure_event": FailureEvent(execution_id="RUN-1", stage="mapping", operation="run",
                                       error_type="ValueError", message="x"),
        "retry_counts": {"mapping": 0},
        "root_cause_output": {"recommended_action": "resume_stage", "resume_from_stage": "not_a_real_stage"},
    }
    result = _agent().run(state)
    assert result.output["next_stage"] == "stop"
