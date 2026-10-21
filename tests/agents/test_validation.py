"""ValidationAgent must build a real FailureEvent on DQD FAIL - it was
previously never set, which would have crashed the Root Cause Analyzer
with a KeyError the first time validation actually failed."""
from unittest.mock import MagicMock

from app.agents.validation import ValidationAgent


def test_failure_event_built_on_dqd_fail(monkeypatch):
    monkeypatch.setattr("app.agents.validation.run_dqd_checks", lambda execution_id: {})
    monkeypatch.setattr("app.agents.validation.summarize_dqd_result", lambda raw: {
        "total_checks": 100, "failed_fatal": 3, "failed_convention": 0,
        "failed_characterization": 0, "passed": False, "details": {"FATAL": [{"checkName": "x"}]},
    })

    agent = ValidationAgent(llm=MagicMock())
    state = {"execution_id": "RUN-1"}
    agent.run(state)

    assert "failure_event" in state
    event = state["failure_event"]
    assert event.stage == "validation"
    assert event.error_type == "DQDFatalCheckFailure"
    assert "3 FATAL" in event.message


def test_no_failure_event_when_dqd_passes(monkeypatch):
    monkeypatch.setattr("app.agents.validation.run_dqd_checks", lambda execution_id: {})
    monkeypatch.setattr("app.agents.validation.summarize_dqd_result", lambda raw: {
        "total_checks": 100, "failed_fatal": 0, "failed_convention": 0,
        "failed_characterization": 0, "passed": True, "details": {},
    })

    agent = ValidationAgent(llm=MagicMock())
    state = {"execution_id": "RUN-1"}
    agent.run(state)

    assert "failure_event" not in state
