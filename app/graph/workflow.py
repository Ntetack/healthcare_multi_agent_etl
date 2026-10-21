"""
Builds the LangGraph StateGraph wiring the seven agents together,
following the reference flow (architecture doc v6, section 21 + the
"validation par DQD uniquement" flow).
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    coordinator_node,
    loading_node,
    mapping_node,
    profiling_node,
    promote_final_node,
    root_cause_node,
    transformation_node,
    validation_node,
)
from app.graph.routing import (
    after_coordinator,
    after_loading,
    after_mapping,
    after_profiling,
    after_root_cause,
    after_transformation,
    after_validation,
)
from app.graph.state import PipelineState


def build_workflow():
    graph = StateGraph(PipelineState)

    graph.add_node("coordinator", coordinator_node)
    graph.add_node("profiling", profiling_node)
    graph.add_node("mapping", mapping_node)
    graph.add_node("transformation", transformation_node)
    graph.add_node("loading", loading_node)
    graph.add_node("validation", validation_node)
    graph.add_node("root_cause", root_cause_node)
    graph.add_node("promote_final", promote_final_node)

    graph.set_entry_point("coordinator")

    graph.add_conditional_edges("coordinator", after_coordinator, {
        "profiling": "profiling",
        "mapping": "mapping",
        "transformation": "transformation",
        "loading": "loading",
        "validation": "validation",
        "stop": END,
    })

    graph.add_conditional_edges("profiling", after_profiling, {
        "mapping": "mapping",
        "root_cause": "root_cause",
        "stop": END,
    })

    graph.add_conditional_edges("mapping", after_mapping, {
        "transformation": "transformation",
        "root_cause": "root_cause",
    })

    graph.add_conditional_edges("transformation", after_transformation, {
        "loading": "loading",
        "root_cause": "root_cause",
    })

    graph.add_conditional_edges("loading", after_loading, {
        "validation": "validation",
        "root_cause": "root_cause",
    })

    graph.add_conditional_edges("validation", after_validation, {
        "promote": "promote_final",
        "root_cause": "root_cause",
    })

    graph.add_conditional_edges("root_cause", after_root_cause, {
        "coordinator": "coordinator",
    })

    graph.add_edge("promote_final", END)

    return graph.compile()
