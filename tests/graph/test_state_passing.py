"""Regression test: LangGraph only persists what a node RETURNS, not
in-place mutations agents make on the `state` dict they receive. Each
node wrapping an agent that stashes internal handoff data (e.g.
_raw_tables, _transformed_tables) on `state` must explicitly return that
key too, or it's silently lost between steps."""
from unittest.mock import MagicMock

from app.graph.nodes import profiling_node, transformation_node


def test_profiling_node_forwards_raw_tables(monkeypatch):
    fake_result = MagicMock(output={"status": "FOUND"})

    monkeypatch.setattr(
        "app.graph.nodes.profiling_agent.run",
        lambda state: (state.update({"_raw_tables": {"PATIENTS": "fake_df"}, "source_path": "/some/folder"}) or fake_result),
    )

    update = profiling_node({"execution_id": "X", "source_name": "test"})

    assert update["_raw_tables"] == {"PATIENTS": "fake_df"}
    assert update["source_path"] == "/some/folder"


def test_transformation_node_forwards_transformed_tables(monkeypatch):
    fake_result = MagicMock(output={"per_table_applied_transforms": {}})

    monkeypatch.setattr(
        "app.graph.nodes.transformation_agent.run",
        lambda state: (state.update({"_transformed_tables": {"PATIENTS": "fake_df"}}) or fake_result),
    )

    update = transformation_node({"execution_id": "X", "_raw_tables": {}})

    assert update["_transformed_tables"] == {"PATIENTS": "fake_df"}
