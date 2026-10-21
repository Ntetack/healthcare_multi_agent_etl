"""Small shared helpers for parsing LLM output. Kept separate from
individual agents since every LLM-calling agent needs the same
strict-JSON-with-fallback parsing."""
from __future__ import annotations

import json
import re
from typing import Any

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def parse_json_response(raw_text: str) -> dict[str, Any]:
    """Parses an LLM response expected to be strict JSON, tolerating
    common deviations (markdown code fences, leading/trailing whitespace).
    Raises ValueError with the raw text included if parsing still fails,
    so the caller can log/persist it as a FailureEvent rather than crash
    uninformatively."""
    cleaned = _FENCE_RE.sub("", raw_text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM did not return valid JSON. Raw output: {raw_text!r}") from exc
