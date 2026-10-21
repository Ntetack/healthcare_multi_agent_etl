"""
Standard structured output every agent must produce (see architecture
doc v6, section 18). Persisted as result.json, and rendered as a
human-readable report.md alongside it.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


class AgentResult(BaseModel):
    execution_id: str
    agent_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: AgentStatus
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    decisions: list[str] = Field(default_factory=list)
    # Synthetic, auditable justification - NOT the raw chain-of-thought.
    reasoning_summary: str = ""
    tools_used: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
