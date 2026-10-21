"""Every stage must route to root_cause on failure - not just
validation. Covers the exception-safety net (_safe_run) and the
extended routing functions."""
from app.graph.nodes import _safe_run
from app.graph.routing import after_loading, after_mapping, after_profiling, after_transformation, after_validation


class _FakeAgent:
    def __init__(self, raise_error=None, result=None):
        self._raise_error = raise_error
        self._result = result

    def run(self, state):
        if self._raise_error:
            raise self._raise_error
        return self._result


def test_safe_run_catches_exception_into_failure_event():
    agent = _FakeAgent(raise_error=ValueError("something broke"))
    result, failure = _safe_run(agent, {"execution_id": "RUN-1"}, "mapping")

    assert result is None
    assert failure is not None
    assert failure.stage == "mapping"
    assert failure.error_type == "ValueError"
    assert "something broke" in failure.message


def test_safe_run_passes_through_on_success():
    agent = _FakeAgent(result="ok")
    result, failure = _safe_run(agent, {"execution_id": "RUN-1"}, "mapping")
    assert result == "ok"
    assert failure is None


def test_every_stage_routes_to_root_cause_on_failure_event():
    state_with_failure = {"failure_event": object()}
    assert after_profiling(state_with_failure) == "root_cause"
    assert after_mapping(state_with_failure) == "root_cause"
    assert after_transformation(state_with_failure) == "root_cause"
    assert after_loading(state_with_failure) == "root_cause"
    assert after_validation(state_with_failure) == "root_cause"


def test_normal_routing_when_no_failure():
    assert after_mapping({}) == "transformation"
    assert after_transformation({}) == "loading"
    assert after_loading({}) == "validation"
    assert after_validation({"validation_passed": True}) == "promote"
    assert after_validation({"validation_passed": False}) == "root_cause"


def test_after_root_cause_always_goes_to_coordinator():
    from app.graph.routing import after_root_cause
    assert after_root_cause({}) == "coordinator"
    assert after_root_cause({"anything": "irrelevant"}) == "coordinator"


def test_after_coordinator_routes_to_valid_stage():
    from app.graph.routing import after_coordinator
    assert after_coordinator({"next_stage": "mapping"}) == "mapping"
    assert after_coordinator({"next_stage": "profiling"}) == "profiling"


def test_after_coordinator_rejects_invalid_stage():
    from app.graph.routing import after_coordinator
    assert after_coordinator({"next_stage": "not_a_real_stage"}) == "stop"
    assert after_coordinator({}) == "stop"
