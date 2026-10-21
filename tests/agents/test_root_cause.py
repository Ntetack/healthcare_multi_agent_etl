"""RootCauseAnalyzerAgent tests - LLM mocked, no DB needed."""
import json
from unittest.mock import MagicMock

from app.agents.root_cause import RootCauseAnalyzerAgent
from app.schemas.failure_event import FailureEvent


def _fake_llm_response(payload):
    return MagicMock(content=json.dumps(payload))


def _build_event(stage="validation"):
    return FailureEvent(
        execution_id="RUN-1", stage=stage, operation="dqd",
        error_type="DQDFatalCheckFailure", message="2 FATAL checks failed",
    )


def test_tolerable_failure_recommends_resume():
    agent = RootCauseAnalyzerAgent(llm=MagicMock())
    agent.llm.invoke.return_value = _fake_llm_response({
        "probable_cause": "A handful of unmapped drug codes, non-critical.",
        "severity": "tolerable",
        "recommended_action": "resume_stage",
        "resume_from_stage": "loading",
    })

    state = {
        "execution_id": "RUN-1", "source_name": "hospital_a",
        "failure_event": _build_event(), "retry_counts": {},
    }
    result = agent.run(state)

    assert result.output["recommended_action"] == "resume_stage"
    assert result.output["resume_from_stage"] == "loading"
    assert result.status.value == "SUCCESS"


def test_fatal_failure_marks_folder_failed(monkeypatch):
    marked = {}
    monkeypatch.setattr(
        "app.agents.root_cause.mark_status",
        lambda source_name, path, status: marked.update(source_name=source_name, path=path, status=status),
    )

    agent = RootCauseAnalyzerAgent(llm=MagicMock())
    agent.llm.invoke.return_value = _fake_llm_response({
        "probable_cause": "Systematic mapping failure across most patients.",
        "severity": "fatal",
        "recommended_action": "human_intervention",
        "resume_from_stage": None,
    })

    state = {
        "execution_id": "RUN-1", "source_name": "hospital_a", "source_path": "/data/batch1",
        "failure_event": _build_event(), "retry_counts": {},
    }
    agent.run(state)

    assert marked == {"source_name": "hospital_a", "path": "/data/batch1", "status": "FAILED"}


def test_invalid_llm_action_falls_back_to_human_intervention():
    """An LLM response outside the allowed action set must not be
    trusted blindly - fail safe toward human review."""
    agent = RootCauseAnalyzerAgent(llm=MagicMock())
    agent.llm.invoke.return_value = _fake_llm_response({
        "probable_cause": "...", "severity": "serious",
        "recommended_action": "just_ignore_it",  # not a real action
        "resume_from_stage": None,
    })
    state = {"execution_id": "RUN-1", "source_name": "hospital_a", "failure_event": _build_event(), "retry_counts": {}}
    result = agent.run(state)
    assert result.output["recommended_action"] == "human_intervention"


def test_invalid_resume_stage_is_rejected():
    """resume_from_stage must be one of the real graph node names, or
    None - never trusted as an arbitrary string."""
    agent = RootCauseAnalyzerAgent(llm=MagicMock())
    agent.llm.invoke.return_value = _fake_llm_response({
        "probable_cause": "...", "severity": "tolerable",
        "recommended_action": "resume_stage",
        "resume_from_stage": "some_made_up_stage",
    })
    state = {"execution_id": "RUN-1", "source_name": "hospital_a", "failure_event": _build_event(), "retry_counts": {}}
    result = agent.run(state)
    assert result.output["resume_from_stage"] is None


def test_unparseable_llm_response_fails_safe():
    agent = RootCauseAnalyzerAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content="not json at all")
    state = {"execution_id": "RUN-1", "source_name": "hospital_a", "failure_event": _build_event(), "retry_counts": {}}
    result = agent.run(state)
    assert result.output["recommended_action"] == "human_intervention"


def test_root_cause_node_increments_retry_count():
    """Without this, MAX_RETRIES could never trigger - retry_counts
    would stay at 0 forever, risking an infinite loop between a
    repeatedly-failing stage and root_cause."""
    from unittest.mock import patch
    from app.graph.nodes import root_cause_node

    state = {
        "execution_id": "RUN-1", "source_name": "hospital_a",
        "failure_event": _build_event(stage="mapping"),
        "retry_counts": {"mapping": 1},
    }
    fake_result = MagicMock(output={"recommended_action": "retry", "resume_from_stage": "mapping"})
    with patch("app.graph.nodes.root_cause_agent.run", return_value=fake_result):
        update = root_cause_node(state)

    assert update["retry_counts"]["mapping"] == 2
