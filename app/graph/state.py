"""
Shared LangGraph state threaded through all seven agent nodes.
Kept as a plain TypedDict (not pydantic) since LangGraph mutates it
node-to-node; validated data lives inside AgentResult/MappingRecord etc.
"""
from __future__ import annotations

from typing import Any, TypedDict

from app.schemas.failure_event import FailureEvent


class PipelineState(TypedDict, total=False):
    execution_id: str
    source_name: str
    source_path: str          # concrete batch folder chosen by the Profiling Agent's detection step
    folder_detection_output: dict[str, Any]  # {"status": "NOTHING_TO_PROCESS" | "FOUND", ...}

    # Set by Profiling, consumed by Mapping/Transformation
    _raw_tables: Any        # dict[str, pd.DataFrame] - one entry per discovered table
    batch_metadata: dict[str, Any]  # THIS batch's own metadata.yaml content (format + fields)
    profiling_output: dict[str, Any]

    # Set at launch (see app/main.py --replay-mapping): replay the model's mapping decisions
    # saved in a snapshot instead of asking the model again. {"name": ..., "on_mismatch": ...}
    mapping_replay: dict[str, Any]

    # Set by Mapping (staging-enriched with *_concept_id columns), consumed by Transformation
    _enriched_tables: Any    # dict[str, pd.DataFrame]
    mapping_output: dict[str, Any]

    # Set by Transformation, consumed by Loading
    _transformed_tables: Any  # dict[str, pd.DataFrame]
    transformation_output: dict[str, Any]

    # Coordinator / routing bookkeeping
    next_stage: str
    retry_counts: dict[str, int]

    # Loading
    loading_mode: str          # "load_temp" | "promote_final"
    promotion_table: str
    loading_output: dict[str, Any]
    promote_output: dict[str, Any]

    # Validation -> RCA
    validation_passed: bool
    validation_output: dict[str, Any]
    failure_event: FailureEvent
    root_cause_output: dict[str, Any]
