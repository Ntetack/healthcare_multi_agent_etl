"""
Traceability record for an LLM-proposed structural target mapping: which
source (table, field) fills a given OMOP target field, for the tables
that have no concept to search (PERSON, VISIT_OCCURRENCE,
OBSERVATION_PERIOD, DEATH - see app/tools/mapping/omop_target_schema.py).
Distinct from MappingRecord, which is for concept/standard-driven
semantic mapping.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class StructuralTargetMapping(BaseModel):
    target_table: str
    target_field: str
    source_table: str | None = None
    source_field: str | None = None
    # The raw source value this record's target_concept_id was resolved
    # from - set only for vocabulary-field records (one record per
    # distinct value), None for plain-field records (one record per
    # field). Lets the Transformation Agent rebuild the
    # value -> concept_id mapping without re-querying anything.
    source_value: str | None = None
    # Populated only for concept fields backed by a fixed OMOP vocabulary
    # (e.g. gender_concept_id) - see
    # app/tools/mapping/omop_target_schema.py::find_paired_source_value_field.
    target_concept_id: int | None = None
    # The REAL SQL type of target_field, introspected from the
    # already-instantiated OMOP DDL (never guessed) - lets the
    # Transformation Agent cast without a second DB round-trip.
    data_type: str | None = None
    confidence: float | None = None
    reason: str = ""
    agent: str = "mapping_agent"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
