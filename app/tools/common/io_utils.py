"""
Common I/O helpers used by every agent to persist its AgentResult as
result.json + report.md under runs/<execution_id>/<stage>/.
"""
from __future__ import annotations

import json
from pathlib import Path

from app.schemas.agent_result import AgentResult

RUNS_DIR = Path("runs")


def run_dir(execution_id: str, stage: str) -> Path:
    d = RUNS_DIR / execution_id / stage
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_result(result: AgentResult, stage: str) -> Path:
    """Writes result.json for the given stage. Returns the file path."""
    d = run_dir(result.execution_id, stage)
    path = d / "result.json"
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return path


def write_report(execution_id: str, stage: str, markdown: str) -> Path:
    """Writes a human-readable report.md for the given stage."""
    d = run_dir(execution_id, stage)
    path = d / "report.md"
    path.write_text(markdown, encoding="utf-8")
    return path


def default_report(result: AgentResult) -> str:
    """Fallback minimal report.md generator, used when an agent doesn't
    build a richer, stage-specific report."""
    lines = [
        f"# {result.agent_name} Report",
        "",
        "## Execution",
        f"- Execution ID: {result.execution_id}",
        f"- Status: {result.status}",
        f"- Timestamp: {result.timestamp}",
        "",
        "## Reasoning summary",
        result.reasoning_summary or "_(none)_",
        "",
        "## Decisions",
        *([f"- {d}" for d in result.decisions] or ["_(none)_"]),
        "",
        "## Tools used",
        *([f"- {t}" for t in result.tools_used] or ["_(none)_"]),
    ]
    if result.errors:
        lines += ["", "## Errors", *(f"- {e}" for e in result.errors)]
    return "\n".join(lines)
