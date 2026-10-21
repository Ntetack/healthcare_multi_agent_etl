"""The replay request set at launch must reach the Mapping node through LangGraph."""
from langgraph.graph import END, StateGraph

from app.graph.state import PipelineState


def test_mapping_replay_key_is_delivered_to_a_node():
    seen = {}

    def node(state):
        seen["replay"] = state.get("mapping_replay")
        return {}

    graph = StateGraph(PipelineState)
    graph.add_node("probe", node)
    graph.set_entry_point("probe")
    graph.add_edge("probe", END)
    graph.compile().invoke(
        {"execution_id": "R", "source_name": "s", "mapping_replay": {"name": "v1", "on_mismatch": "fail"}}
    )
    assert seen["replay"] == {"name": "v1", "on_mismatch": "fail"}


def test_mapping_replay_is_declared_in_the_state_schema():
    assert "mapping_replay" in PipelineState.__annotations__
