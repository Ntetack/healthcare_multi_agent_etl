"""Execution metrics: wall-clock time and LLM token usage per agent.

Three pieces, all kept free of any agent logic:

* ``LLMUsage``: a mutable counter fed by the LLM wrapper (see
  ``_RetryingLLM`` in app/agents/base.py). One instance per agent, reset
  at the start of every ``run()``.
* ``append_metrics_record``: appends one JSON line per agent execution to
  ``runs/<execution_id>/metrics.jsonl``. The file is append-only on
  purpose: ``result.json`` is overwritten when a stage is retried, so
  the cost of a failed first attempt would otherwise be lost.
* ``summarize_run`` / ``format_summary``: aggregate that file into one
  row per (agent, operation) for the reports and the thesis tables.

Metrics must never be the reason a run fails: every I/O helper here
swallows its own errors.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.tools.common import io_utils

METRICS_FILENAME = "metrics.jsonl"
SUMMARY_FILENAME = "metrics_summary.json"


@dataclass
class LLMUsage:
    """Counters for the LLM calls made during ONE agent run.

    ``output_tokens`` follows the LangChain convention and already
    includes ``reasoning_tokens`` when the provider reports them
    (reasoning models bill their hidden thinking as output).
    """

    calls: int = 0
    calls_without_usage: int = 0  # answered, but the provider reported no token counts
    failed_calls: int = 0  # raised an exception (rate-limit retries included)
    rate_limit_retries: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int = 0
    llm_seconds: float = 0.0  # time spent inside the model call itself
    rate_limit_wait_seconds: float = 0.0  # time spent sleeping between rate-limit retries

    def reset(self) -> None:
        for name, default in asdict(LLMUsage()).items():
            setattr(self, name, default)

    def add_response(self, response: Any) -> None:
        """Registers a successful call and its token counts, if any."""
        self.calls += 1
        counts = extract_token_usage(response)
        if counts is None:
            self.calls_without_usage += 1
            return
        in_tok, out_tok, total_tok, reasoning_tok = counts
        self.input_tokens += in_tok
        self.output_tokens += out_tok
        self.total_tokens += total_tok
        self.reasoning_tokens += reasoning_tok

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["llm_seconds"] = round(d["llm_seconds"], 3)
        d["rate_limit_wait_seconds"] = round(d["rate_limit_wait_seconds"], 3)
        return d


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def extract_token_usage(response: Any) -> tuple[int, int, int, int] | None:
    """Returns (input, output, total, reasoning) tokens for a chat-model
    response, or None when the provider reported nothing.

    Reads LangChain's standard ``usage_metadata`` first, then falls back
    to the raw OpenAI-style ``response_metadata["token_usage"]``.
    """
    usage = getattr(response, "usage_metadata", None)
    if isinstance(usage, dict) and usage:
        in_tok = _as_int(usage.get("input_tokens"))
        out_tok = _as_int(usage.get("output_tokens"))
        total = _as_int(usage.get("total_tokens")) or (in_tok + out_tok)
        details = usage.get("output_token_details") or {}
        reasoning = _as_int(details.get("reasoning")) if isinstance(details, dict) else 0
        return in_tok, out_tok, total, reasoning

    meta = getattr(response, "response_metadata", None)
    raw = meta.get("token_usage") if isinstance(meta, dict) else None
    if isinstance(raw, dict) and raw:
        in_tok = _as_int(raw.get("prompt_tokens"))
        out_tok = _as_int(raw.get("completion_tokens"))
        total = _as_int(raw.get("total_tokens")) or (in_tok + out_tok)
        details = raw.get("completion_tokens_details") or {}
        reasoning = _as_int(details.get("reasoning_tokens")) if isinstance(details, dict) else 0
        return in_tok, out_tok, total, reasoning

    return None


def append_metrics_record(execution_id: str | None, record: dict[str, Any]) -> None:
    """Appends one JSON line to runs/<execution_id>/metrics.jsonl."""
    if not execution_id:
        return
    try:
        path = io_utils.RUNS_DIR / execution_id / METRICS_FILENAME
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except Exception:  # noqa: BLE001 - metrics must never break a run
        pass


def load_metrics_records(execution_id: str, runs_dir: Path | None = None) -> list[dict[str, Any]]:
    path = (runs_dir or io_utils.RUNS_DIR) / execution_id / METRICS_FILENAME
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def summarize_run(execution_id: str, runs_dir: Path | None = None) -> dict[str, Any]:
    """Aggregates metrics.jsonl into one row per (agent, operation).

    ``executions`` counts how many times the agent ran (more than 1 means
    the Coordinator resumed the stage after a failure); durations and
    tokens are summed over all executions, failed ones included.
    """
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for rec in load_metrics_records(execution_id, runs_dir):
        key = (rec.get("agent", "?"), rec.get("operation") or "")
        row = rows.setdefault(
            key,
            {
                "agent": key[0],
                "operation": key[1],
                "executions": 0,
                "failed_executions": 0,
                "duration_seconds": 0.0,
                "llm_seconds": 0.0,
                "llm_calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "total_tokens": 0,
                "rate_limit_retries": 0,
                "calls_without_usage": 0,
            },
        )
        llm = rec.get("llm", {})
        row["executions"] += 1
        row["failed_executions"] += 0 if rec.get("status") == "SUCCESS" else 1
        row["duration_seconds"] += rec.get("duration_seconds", 0.0)
        row["llm_seconds"] += llm.get("llm_seconds", 0.0)
        row["llm_calls"] += llm.get("calls", 0)
        row["input_tokens"] += llm.get("input_tokens", 0)
        row["output_tokens"] += llm.get("output_tokens", 0)
        row["reasoning_tokens"] += llm.get("reasoning_tokens", 0)
        row["total_tokens"] += llm.get("total_tokens", 0)
        row["rate_limit_retries"] += llm.get("rate_limit_retries", 0)
        row["calls_without_usage"] += llm.get("calls_without_usage", 0)

    agents = list(rows.values())
    for row in agents:
        row["duration_seconds"] = round(row["duration_seconds"], 3)
        row["llm_seconds"] = round(row["llm_seconds"], 3)

    totals = {
        "executions": sum(r["executions"] for r in agents),
        "duration_seconds": round(sum(r["duration_seconds"] for r in agents), 3),
        "llm_seconds": round(sum(r["llm_seconds"] for r in agents), 3),
        "llm_calls": sum(r["llm_calls"] for r in agents),
        "input_tokens": sum(r["input_tokens"] for r in agents),
        "output_tokens": sum(r["output_tokens"] for r in agents),
        "reasoning_tokens": sum(r["reasoning_tokens"] for r in agents),
        "total_tokens": sum(r["total_tokens"] for r in agents),
        "rate_limit_retries": sum(r["rate_limit_retries"] for r in agents),
        "calls_without_usage": sum(r["calls_without_usage"] for r in agents),
    }
    return {"execution_id": execution_id, "agents": agents, "totals": totals}


def format_summary(summary: dict[str, Any]) -> str:
    """Renders a summary as a Markdown table."""
    header = (
        "| Agent | Operation | Runs | Time (s) | LLM time (s) | LLM calls "
        "| Input tok. | Output tok. | Reasoning tok. | Total tok. |\n"
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    )

    def line(r: dict[str, Any], agent: str, op: str) -> str:
        return (
            f"| {agent} | {op} | {r['executions']} | {r['duration_seconds']:.2f} "
            f"| {r['llm_seconds']:.2f} | {r['llm_calls']} | {r['input_tokens']} "
            f"| {r['output_tokens']} | {r['reasoning_tokens']} | {r['total_tokens']} |"
        )

    lines = [header]
    lines += [line(r, r["agent"], r["operation"] or "-") for r in summary["agents"]]
    lines.append(line(summary["totals"], "**Total**", ""))
    notes = []
    if summary["totals"]["calls_without_usage"]:
        notes.append(
            f"{summary['totals']['calls_without_usage']} model call(s) returned no token "
            "counts: the token totals are a lower bound."
        )
    if summary["totals"]["rate_limit_retries"]:
        notes.append(f"{summary['totals']['rate_limit_retries']} rate-limit retry(ies) occurred.")
    return "\n".join(lines + ([""] + notes if notes else []))


def write_summary(execution_id: str, extra: dict[str, Any] | None = None) -> Path | None:
    """Writes runs/<execution_id>/metrics_summary.json (and returns its path)."""
    try:
        summary = summarize_run(execution_id)
        if extra:
            summary.update(extra)
        path = io_utils.RUNS_DIR / execution_id / SUMMARY_FILENAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
    except Exception:  # noqa: BLE001
        return None
