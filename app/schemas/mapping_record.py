"""Traceability record for a single mapped field (architecture doc v6, 10.3)."""
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class MappingRecord(BaseModel):
    source: str
    field: str
    standard: str | None = None
    source_value: str | None = None
    # The STANDARD concept (after following "Maps to" if the source
    # vocabulary is itself non-standard, e.g. ICD9CM) - what belongs in
    # the OMOP target's own *_concept_id field.
    target_concept_id: int | None = None
    # The concept representing source_value AS-IS in its OWN declared
    # vocabulary (standard or not) - what belongs in *_source_concept_id.
    # None if source_value couldn't be found in its own vocabulary at all.
    source_concept_id: int | None = None
    target_source_concept_field: str | None = None
    # Resolved OMOP destination for this value, for the 5 domain-driven
    # event tables (condition_occurrence, drug_exposure, measurement,
    # procedure_occurrence, observation) - see
    # app/tools/mapping/omop_target_schema.py. None for tables that need
    # structural (non-concept-driven) declaration instead, e.g. PERSON.
    target_table: str | None = None
    target_concept_field: str | None = None
    target_source_value_field: str | None = None
    confidence: float | None = None
    reason: str = ""
    agent: str = "mapping"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    mapping_version: str = "v1"
