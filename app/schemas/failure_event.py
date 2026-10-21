"""
Structured failure/anomaly event. Any agent or tool that fails emits one
of these; the Coordinator may route it to the Root Cause Analyzer.
(architecture doc v6, section 24 - "Root Cause Analyzer transversal")
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class FailureEvent(BaseModel):
    execution_id: str
    stage: str            # e.g. "profiling", "mapping.semantic", "loading", "dqd"
    operation: str         # e.g. "search_concept", "load_to_omop"
    status: str = "FAILURE"  # FAILURE | ANOMALY
    error_type: str
    message: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
