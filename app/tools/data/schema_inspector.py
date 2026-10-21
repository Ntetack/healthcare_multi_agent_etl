"""
Profiling tools used by the Profiling Agent (architecture doc v6, section 9).
Pure, deterministic, LLM-free functions: they compute facts about the data.
The Profiling Agent (LLM) interprets these facts, it doesn't recompute them.
"""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

_CODING_PATTERNS = {
    "ICD10": re.compile(r"^[A-Z][0-9]{2}(\.[0-9A-Z]{1,4})?$"),
    "LOINC": re.compile(r"^\d{1,5}-\d$"),
    "SNOMED": re.compile(r"^\d{6,18}$"),
    "RxNorm": re.compile(r"^\d{1,8}$"),
}


def _business_columns(df: pd.DataFrame) -> list[str]:
    """Columns to actually profile/interpret - excludes internal
    bookkeeping columns like `_source_file` added by the loaders for
    provenance, which aren't real source fields."""
    return [c for c in df.columns if not c.startswith("_")]


def inspect_schema(df: pd.DataFrame) -> dict[str, Any]:
    columns = _business_columns(df)
    return {
        "columns": columns,
        "n_rows": len(df),
        "n_columns": len(columns),
    }


def profile_dataset(df: pd.DataFrame) -> dict[str, Any]:
    profile: dict[str, Any] = {}
    for col in _business_columns(df):
        series = df[col].astype(str)
        profile[col] = {
            "missing_count": int((series.str.strip() == "").sum()),
            "distinct_count": int(series.nunique()),
            "sample_values": series[series.str.strip() != ""].unique()[:5].tolist(),
        }
    return profile


def detect_patterns(df: pd.DataFrame) -> dict[str, str]:
    """Very lightweight type/format guess per column (date-like, numeric-like,
    free text, ...). Not a source of truth - just a hint for the LLM."""
    patterns: dict[str, str] = {}
    for col in _business_columns(df):
        sample = df[col].astype(str).head(50)
        if sample.str.match(r"^\d{4}-\d{2}-\d{2}").any():
            patterns[col] = "date_like"
        elif sample.str.match(r"^-?\d+(\.\d+)?$").all():
            patterns[col] = "numeric_like"
        else:
            patterns[col] = "text_like"
    return patterns


def detect_possible_codings(df: pd.DataFrame) -> dict[str, list[str]]:
    """Flags columns whose values match a known coding-system pattern
    (ICD10/LOINC/SNOMED/RxNorm shape). This is a hint, not a decision -
    the actual standard still comes from source_metadata.yaml."""
    hits: dict[str, list[str]] = {}
    for col in _business_columns(df):
        sample = df[col].astype(str).head(50)
        matches = [
            name for name, pattern in _CODING_PATTERNS.items()
            if sample.str.match(pattern).mean() > 0.5
        ]
        if matches:
            hits[col] = matches
    return hits
