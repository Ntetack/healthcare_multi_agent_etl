"""
Resolves a field explicitly declared as "local" in metadata.yaml - an
internal reference (e.g. MIMIC-III's D_ITEMS/D_LABITEMS-style ITEMID)
that must be joined to a dictionary table in the SAME batch before it
can be searched against any vocabulary. This is a GENERIC mechanism -
it never hardcodes any source-specific table/column name; everything
is discovered per batch, from whatever tables and columns are actually
present.

Two distinct outcomes after the join, handled very differently:
  - "code": the joined value is a REAL external code (e.g. D_LABITEMS'
    LOINC_CODE) - proceeds through the normal, existing search_concept()
    machinery (exact match, then substring, then fuzzy trigram fallback).
  - "text": the joined value is a free-text description (e.g. D_ITEMS'
    LABEL, "Heart Rate") with no external code - proceeds through
    search_concept_exact_only() instead, which NEVER falls back to
    substring or fuzzy matching. A full clinical phrase has a much
    higher chance of coincidentally resembling an unrelated concept
    than a short categorical value (e.g. "WHITE") does, so an
    approximate match here is a real risk of silently wrong data - the
    project's own explicit decision is to produce no match at all
    rather than a wrong one in this case.
"""
from __future__ import annotations

import json
from typing import Any

import pandas as pd
from sqlalchemy import text as sql_text

from app.prompts.local_vocab_resolution_prompt import LOCAL_VOCAB_RESOLUTION_PROMPT
from app.tools.common.llm_utils import parse_json_response
from app.tools.database.db import session_scope
from app.tools.mapping.mapping_cache import get_cached_resolution, store_resolution

MIN_JOIN_OVERLAP = 0.5

CACHE_KIND = "local_vocab_join"


def resolve_local_vocab_join(
    llm: Any, table: str, field: str, sample_values: list, tables_summary: dict, source_name: str
) -> dict | None:
    """Asks the LLM to identify the dictionary table/column for a field
    declared "local", and whether the resolved value is a real code or
    free text. Returns None if the LLM's proposal is incomplete (can't
    be acted on safely) - the caller falls back to treating the field
    as unresolved, never guesses further.

    Checked against the persistent mapping cache FIRST, scoped to
    `source_name`: this exact (table, field) relationship never changes
    between batches of the same source (e.g. MIMIC-III's
    labevents.ITEMID always joins to D_LABITEMS, batch after batch), so
    re-asking the LLM every single run would be wasteful and, worse,
    non-deterministic (nothing guarantees an LLM answers identically
    twice). A cache hit - whether 'llm_suggested' or 'human_confirmed'
    - is used immediately, with NO further LLM call: the pipeline never
    blocks on human review, it only benefits from it when available.
    A cache miss falls through to the LLM exactly as before, and the
    fresh discovery is stored for every future batch of this source."""
    cached = get_cached_resolution(source_name, CACHE_KIND, table, field)
    if cached is not None:
        cached.pop("_cache_status", None)
        return cached

    prompt = LOCAL_VOCAB_RESOLUTION_PROMPT.format(
        table=table, field=field,
        sample_values=json.dumps(sample_values, default=str),
        tables_summary=json.dumps(tables_summary, indent=2, default=str),
    )
    response = llm.invoke(prompt)
    try:
        parsed = parse_json_response(response.content)
    except ValueError:
        return None

    required = ("join_table", "join_key_source", "join_key_target", "resolved_column", "resolved_kind")
    if not all(parsed.get(k) for k in required):
        return None
    if parsed["resolved_kind"] not in ("code", "text"):
        return None
    if not isinstance(parsed.get("resolved_standards"), list):
        parsed["resolved_standards"] = []

    store_resolution(source_name, CACHE_KIND, table, field, parsed)
    return parsed


def apply_local_vocab_join(fact_df: pd.DataFrame, dictionary_df: pd.DataFrame, join_spec: dict) -> pd.Series | None:
    """Executes the proposed join and returns the resolved column,
    aligned to fact_df's rows - or None if the join fails a minimum
    real-overlap check (the same safety principle used everywhere else
    in this project: a plausible-looking but wrong join must never be
    trusted blindly). Defensively de-duplicates the dictionary side on
    its join key first, so a duplicate key can never multiply fact_df's
    rows during the merge."""
    key_fact = join_spec["join_key_source"]
    key_dict = join_spec["join_key_target"]
    value_col = join_spec["resolved_column"]

    if key_fact not in fact_df.columns or key_dict not in dictionary_df.columns or value_col not in dictionary_df.columns:
        return None

    overlap = fact_df[key_fact].isin(dictionary_df[key_dict]).mean()
    if overlap < MIN_JOIN_OVERLAP:
        return None

    dictionary_deduped = dictionary_df.drop_duplicates(subset=[key_dict], keep="first")
    merged = fact_df[[key_fact]].merge(
        dictionary_deduped[[key_dict, value_col]], left_on=key_fact, right_on=key_dict, how="left"
    )
    return merged[value_col]


def search_concept_exact_only(text_value: str, standards: list[str]) -> dict | None:
    """For a resolved value that is free TEXT (not a code) - e.g. a
    local dictionary's descriptive label. Deliberately STRICTER than
    the normal search_concept(): only an exact (case-insensitive,
    whitespace-normalized) concept_name match is accepted - no
    substring, no fuzzy trigram fallback. A full clinical phrase is far
    more likely to coincidentally resemble an unrelated concept via
    substring/fuzzy matching than a short categorical value is, so this
    project's explicit choice is: no match at all is better than a
    silently wrong one here.

    Accepts MULTIPLE candidate standards, tried IN ORDER - the first
    one with a real match wins. This is what lets a single field mix
    different kinds of values correctly: e.g. a drug/fluid
    administration table's item names are usually drugs, but sometimes
    a lab value - searching ["RxNorm", "LOINC"] finds "Dopamine" under
    RxNorm (a real drug) while "Heart Rate" (absent from RxNorm) falls
    through and is found under LOINC instead, for the SAME field,
    without forcing one vocabulary choice for the whole column. The
    resulting domain (Drug vs Measurement) is what downstream routing
    (mechanism 1) uses to send each row to the right target table."""
    from app.tools.mapping.semantic.semantic_mapper import STANDARD_TO_VOCABULARY, normalize_text

    if not text_value or not text_value.strip():
        return None
    if not standards:
        return None

    normalized = normalize_text(text_value)
    with session_scope() as session:
        for standard in standards:
            vocab_ids = STANDARD_TO_VOCABULARY.get(standard, [])
            if not vocab_ids:
                continue
            row = session.execute(
                sql_text(
                    """
                    SELECT concept_id, concept_name, concept_code, vocabulary_id, domain_id, standard_concept
                    FROM cdm_vocab.concept
                    WHERE vocabulary_id = ANY(:vocab_ids)
                      AND lower(concept_name) = lower(:value)
                    LIMIT 1
                    """
                ),
                {"vocab_ids": vocab_ids, "value": normalized},
            ).mappings().first()
            if row is not None:
                result = dict(row)
                result["_match_confidence"] = 1.0  # exact match only - no lower-confidence tier exists here
                return result
    return None
