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
    machinery (exact code or exact name).
  - "text": the joined value is a free-text description (e.g. D_ITEMS'
    LABEL, "Heart Rate") with no external code - proceeds through
    resolve_concept_exact_by_name(), an exact (case-insensitive) name
    match that also guarantees the concept it hands back as STANDARD
    really is Standard and valid (see its docstring). Matching is exact
    everywhere in this project: no substring, no similarity.
"""
from __future__ import annotations

import json
import math
import re
from typing import Any

import pandas as pd
from sqlalchemy import text as sql_text

from app.prompts.local_vocab_resolution_prompt import LOCAL_VOCAB_RESOLUTION_PROMPT
from app.prompts.local_vocab_name_pattern_prompt import LOCAL_VOCAB_NAME_PATTERN_PROMPT
from app.prompts.local_vocab_standards_prompt import LOCAL_VOCAB_STANDARDS_PROMPT
from app.tools.common.llm_utils import parse_json_response
from app.tools.database.db import session_scope
from app.tools.mapping.mapping_cache import get_cached_resolution, store_resolution

MIN_JOIN_OVERLAP = 0.5

CACHE_KIND = "local_vocab_join"
STANDARDS_CACHE_KIND = "local_vocab_standards"
NAME_PATTERN_CACHE_KIND = "local_vocab_name_pattern"

# How many distinct labels the vocabulary question is shown.
LABEL_SAMPLE_SIZE = 10

# A qualifier is only worth deciding on when it is consistent across the field:
# it must exist for at least this share of the sampled labels.
MIN_SUFFIX_COVERAGE = 0.5
MAX_SUFFIXES_SHOWN = 8
CONTEXT_ROWS = 5


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

    # The overlap is measured on the rows that actually CARRY a key. A
    # legitimately sparse key (e.g. MICROBIOLOGYEVENTS.ab_itemid is empty
    # for every culture without an antibiogram) must not make a correct
    # join look wrong: counting the empty cells as "no match" would
    # reject it. A join whose filled keys do not match is still rejected,
    # and a column with no key at all has nothing to join.
    keys = fact_df[key_fact]
    filled = keys.notna() & (keys.astype(str).str.strip() != "")
    if not filled.any():
        return None
    overlap = keys[filled].isin(dictionary_df[key_dict]).mean()
    if overlap < MIN_JOIN_OVERLAP:
        return None

    dictionary_deduped = dictionary_df.drop_duplicates(subset=[key_dict], keep="first")
    merged = fact_df[[key_fact]].merge(
        dictionary_deduped[[key_dict, value_col]], left_on=key_fact, right_on=key_dict, how="left"
    )
    return merged[value_col]


_NAME_CANDIDATES_SQL = """
    SELECT concept_id, concept_name, concept_code, vocabulary_id, domain_id,
           standard_concept, invalid_reason
    FROM cdm_vocab.concept
    WHERE vocabulary_id = ANY(:vocab_ids)
      AND lower(concept_name) = lower(:value)
    ORDER BY (standard_concept = 'S') DESC NULLS LAST,
             (invalid_reason IS NULL) DESC,
             concept_id
    LIMIT 50
"""

# How many non-standard candidates are followed through 'Maps to' before
# giving up on a vocabulary: a name shared by many deprecated concepts
# must not trigger an unbounded number of lookups.
MAX_MAPS_TO_LOOKUPS = 5


def resolve_concept_exact_by_name(text_value: str, standards: list[str]) -> dict:
    """For a resolved value that is free TEXT (not a code) - e.g. a
    local dictionary's descriptive label. Deliberately STRICTER than a
    code lookup: only an exact (case-insensitive, whitespace-normalized)
    concept_name match is accepted - no substring, no similarity. A full
    clinical phrase is far more likely to coincidentally resemble an
    unrelated concept than a short categorical value is, so this
    project's explicit choice is: no match at all is better than a
    silently wrong one here.

    Several concepts can share a name (the LOINC concept "Heart rate"
    exists both as a Standard concept and as a Classification one, and
    deprecated concepts keep their old names). The returned pair
    therefore follows the OMOP convention instead of taking whichever
    row comes first:
      - source_concept: the concept the text names (a Standard, valid
        one if the name has any; otherwise a non-standard one);
      - standard_concept: a Standard, valid concept - the source concept
        itself when it is one, else its 'Maps to' target - or None when
        no Standard equivalent exists. A non-standard concept is NEVER
        returned as the standard one.

    Accepts MULTIPLE candidate standards, tried IN ORDER - the first one
    that yields a Standard concept wins. This is what lets a single
    field mix different kinds of values correctly: e.g. a drug/fluid
    administration table's item names are usually drugs, but sometimes a
    lab value - searching ["RxNorm", "LOINC"] finds "Dopamine" under
    RxNorm while "Heart Rate" (absent from RxNorm) falls through and is
    found under LOINC. The resulting domain (Drug vs Measurement) is
    what downstream routing uses to send each row to the right target
    table. If no vocabulary yields a Standard concept, the first
    non-standard match found (if any) is returned as the source concept
    alone, so the value stays traceable without a wrong standard id.

    Returns {"source_concept": dict | None, "standard_concept": dict | None}."""
    from app.tools.mapping.semantic.semantic_mapper import (
        STANDARD_TO_VOCABULARY,
        find_standard_concept_via_maps_to,
        is_placeholder,
        normalize_text,
    )

    none = {"source_concept": None, "standard_concept": None}
    if is_placeholder(text_value) or not standards:
        return none

    normalized = normalize_text(text_value)
    non_standard_fallback = None
    for standard in standards:
        vocab_ids = STANDARD_TO_VOCABULARY.get(standard, [])
        if not vocab_ids:
            continue
        with session_scope() as session:
            rows = [dict(r) for r in session.execute(
                sql_text(_NAME_CANDIDATES_SQL), {"vocab_ids": vocab_ids, "value": normalized}
            ).mappings().all()]
        if not rows:
            continue

        # Standard and valid: it is both the source and the standard concept.
        # (Picked in Python as well, so the choice does not depend on the
        # row order the database returned.)
        for row in rows:
            if row.get("standard_concept") == "S" and row.get("invalid_reason") is None:
                row["_match_confidence"] = 1.0
                return {"source_concept": row, "standard_concept": row}

        # Only non-standard concepts carry this name: follow 'Maps to'.
        valid_first = sorted(rows, key=lambda r: r.get("invalid_reason") is not None)
        for row in valid_first[:MAX_MAPS_TO_LOOKUPS]:
            mapped = find_standard_concept_via_maps_to(row["concept_id"])
            if mapped:
                row["_match_confidence"] = 1.0
                mapped = dict(mapped)
                mapped["_match_confidence"] = 1.0
                return {"source_concept": row, "standard_concept": mapped}

        if non_standard_fallback is None:
            non_standard_fallback = dict(valid_first[0], _match_confidence=1.0)

    if non_standard_fallback is not None:
        return {"source_concept": non_standard_fallback, "standard_concept": None}
    return none


def search_concept_exact_only(text_value: str, standards: list[str]) -> dict | None:
    """The Standard concept for a free-text value (see
    resolve_concept_exact_by_name), or None. Kept for callers that only
    need the standard concept."""
    return resolve_concept_exact_by_name(text_value, standards)["standard_concept"]


# --- Vocabulary choice from the real labels -------------------------------

def sample_distinct_labels(labels: pd.Series, n: int = LABEL_SAMPLE_SIZE) -> tuple[list[str], int]:
    """Picks up to `n` DISTINCT labels to show the LLM, deterministically
    (same data, same sample - a random sample would make the vocabulary
    choice, and so the run, non-reproducible).

    Half of the sample is the most frequent labels (they carry the most
    rows), the other half is spread evenly over the remaining labels in
    alphabetical order, so a long tail of a different kind is not hidden
    by the head of the distribution. Returns (sample, n_distinct)."""
    cleaned = labels.dropna().astype(str).str.strip()
    cleaned = cleaned[cleaned != ""]
    counts = cleaned.value_counts()
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    distinct = [label for label, _ in ordered]
    if len(distinct) <= n:
        return distinct, len(distinct)

    head = distinct[: (n + 1) // 2]
    tail = sorted(distinct[len(head):])
    wanted = n - len(head)
    if wanted == 1:
        spread = [tail[len(tail) // 2]]
    else:
        # both ends of the alphabetical tail are included
        spread = [tail[round(i * (len(tail) - 1) / (wanted - 1))] for i in range(wanted)]
    return head + spread, len(distinct)


def resolve_standards_from_labels(
    llm: Any, table: str, field: str, labels: list[str], n_distinct: int,
    source_name: str, fallback: list[str], context_rows: list[dict] | None = None,
) -> list[str]:
    """Chooses the vocabularies to search from a sample of the real
    labels, once per (source, table, field) - cached like the join, so
    the same data never gets two different answers. Falls back to the
    list the join proposal carried (`fallback`) when the answer is
    unusable, so this step can only refine, never break, the pipeline.

    A deliberately EMPTY list is kept as such: it is the honest answer
    for labels too source-specific to exist in any vocabulary."""
    from app.tools.mapping.semantic.semantic_mapper import STANDARD_TO_VOCABULARY

    cached = get_cached_resolution(source_name, STANDARDS_CACHE_KIND, table, field)
    if cached is not None and isinstance(cached.get("resolved_standards"), list):
        return cached["resolved_standards"]
    if not labels:
        return fallback

    prompt = LOCAL_VOCAB_STANDARDS_PROMPT.format(
        table=table, field=field, n_labels=len(labels), n_distinct=n_distinct,
        labels=json.dumps(labels, ensure_ascii=False, indent=2),
        rows=json.dumps(context_rows or [], ensure_ascii=False, indent=2),
    )
    try:
        parsed = parse_json_response(llm.invoke(prompt).content)
    except ValueError:
        return fallback

    proposed = parsed.get("resolved_standards")
    if not isinstance(proposed, list):
        return fallback
    known = [s for s in proposed if isinstance(s, str) and s in STANDARD_TO_VOCABULARY]
    if proposed and not known:
        return fallback  # only names the framework cannot search
    parsed["resolved_standards"] = known
    parsed["sample_labels"] = labels
    store_resolution(source_name, STANDARDS_CACHE_KIND, table, field, parsed)
    return known


# --- Declared, source-specific policy (metadata.yaml) ----------------------

def get_local_vocab_override(batch_cfg: dict, table: str, field: str) -> dict | None:
    """The policy a source declares for one local field in metadata.yaml:

        local_vocab_overrides:
          MICROBIOLOGYEVENTS:
            ab_itemid:
              resolved_standards: [LOINC]
              name_templates:
                - "{label} [Susceptibility] by Minimum inhibitory concentration (MIC)"
                - "{label} [Susceptibility]"
              name_aliases:
                "PIPERACILLIN/TAZO": "Piperacillin+Tazobactam"

    It lives in the source's configuration, not in the cache: the cache
    holds what the LLM suggested and can be rebuilt at any time, while
    this is a decision a person took and must survive that. Table and
    field names are matched case-insensitively."""
    overrides = (batch_cfg or {}).get("local_vocab_overrides") or {}
    for table_key, fields in overrides.items():
        if str(table_key).lower() != table.lower() or not isinstance(fields, dict):
            continue
        for field_key, spec in fields.items():
            if str(field_key).lower() == field.lower():
                return spec
    return None


def resolve_concept_with_policy(
    text_value: str, standards: list[str],
    name_templates: list[str] | None = None, name_aliases: dict[str, str] | None = None,
) -> dict:
    """resolve_concept_exact_by_name, preceded by the source's declared
    policy: the label is first replaced through `name_aliases` (a label
    that is not spelled like its concept, e.g. an abbreviation), then
    each of `name_templates` is tried IN ORDER ({label} is the label) and
    the first one that yields a Standard concept wins - a template list
    is how a source states which VARIANT of a concept it means and what
    to fall back on. Matching stays exact everywhere.

    Without templates or aliases this is exactly resolve_concept_exact_by_name.
    The extra key "matched_name" records the concept name that was looked
    up, so the choice can be traced."""
    from app.tools.mapping.semantic.semantic_mapper import is_placeholder, normalize_text

    if is_placeholder(text_value):
        return {"source_concept": None, "standard_concept": None, "matched_name": None}

    label = normalize_text(str(text_value))
    if name_aliases:
        by_lower = {normalize_text(str(k)).casefold(): str(v) for k, v in name_aliases.items()}
        label = by_lower.get(label.casefold(), label)

    candidates = [t.replace("{label}", label) for t in name_templates] if name_templates else [label]

    fallback = None
    for name in candidates:
        result = resolve_concept_exact_by_name(name, standards)
        if result["standard_concept"] is not None:
            return dict(result, matched_name=name)
        if fallback is None and result["source_concept"] is not None:
            fallback = dict(result, matched_name=name)
    return fallback or {"source_concept": None, "standard_concept": None, "matched_name": None}


# --- Rows shown to the model as context ---------------------------------------

_IDENTIFYING_COLUMN = re.compile(r"(^|_)id$|itemid$|date|time", re.IGNORECASE)


def sample_context_rows(fact_df: pd.DataFrame, key_field: str, n: int = CONTEXT_ROWS) -> list[dict]:
    """A few real rows of the table the field belongs to, so the model can see
    what a row RECORDS (a label alone can look like something it is not).
    Identifier and date/time columns are left out - nothing that identifies a
    patient or an event leaves the machine - and values are truncated.
    Rows are spread evenly over the rows that carry a key: same data, same
    rows."""
    columns = [
        c for c in fact_df.columns
        if c != key_field and not str(c).startswith("_") and not _IDENTIFYING_COLUMN.search(str(c))
    ]
    if not columns or key_field not in fact_df.columns:
        return []
    keys = fact_df[key_field]
    filled = keys.notna() & (keys.astype(str).str.strip() != "")
    rows = fact_df.loc[filled, columns]
    if rows.empty:
        return []
    count = min(n, len(rows))
    positions = sorted({round(i * (len(rows) - 1) / max(count - 1, 1)) for i in range(count)})
    return [{c: str(v)[:40] for c, v in rows.iloc[i].items()} for i in positions]


# --- Which variant of a concept the source means -------------------------------

_PREFIX_SQL = """
    SELECT concept_name, domain_id, vocabulary_id
    FROM cdm_vocab.concept
    WHERE vocabulary_id = ANY(:vocab_ids)
      AND standard_concept = 'S'
      AND invalid_reason IS NULL
      AND lower(left(concept_name, length(:label))) = lower(:label)
    ORDER BY length(concept_name), concept_name
    LIMIT 200
"""


def find_name_extensions(label: str, vocab_ids: list[str]) -> list[dict]:
    """Standard, valid concepts whose name BEGINS with `label` (case-
    insensitive): the label itself and its variants. `left()` is used rather
    than LIKE so that '%' or '_' inside a label can never act as a wildcard."""
    with session_scope() as session:
        return [dict(r) for r in session.execute(
            sql_text(_PREFIX_SQL), {"vocab_ids": vocab_ids, "label": label}
        ).mappings().all()]


def collect_suffix_candidates(labels: list[str], standards: list[str]) -> list[dict]:
    """The qualifiers (what follows the label in a concept name) found in the
    vocabulary for the sampled labels, with how many labels have each.
    Returns [{"suffix", "coverage", "domains"}] for the qualifiers present for
    at least MIN_SUFFIX_COVERAGE of the labels, widest coverage first. "" is
    the label itself. Empty when nothing is consistent across the field."""
    from app.tools.mapping.semantic.semantic_mapper import STANDARD_TO_VOCABULARY

    vocab_ids = sorted({v for st in standards for v in STANDARD_TO_VOCABULARY.get(st, [])})
    if not vocab_ids or not labels:
        return []

    seen: dict[str, dict] = {}
    for label in labels:
        for row in find_name_extensions(label, vocab_ids):
            suffix = row["concept_name"][len(label):]
            if suffix and suffix[0] not in " [(,-/:+":
                continue  # a longer word, not a qualifier (Heart -> Heartburn)
            entry = seen.setdefault(suffix.casefold(), {"suffix": suffix, "labels": set(), "domains": {}})
            entry["labels"].add(label)
            entry["domains"][row["domain_id"]] = entry["domains"].get(row["domain_id"], 0) + 1

    needed = max(1, math.ceil(MIN_SUFFIX_COVERAGE * len(labels)))
    kept = [
        {"suffix": e["suffix"], "coverage": len(e["labels"]), "domains": e["domains"]}
        for e in seen.values() if len(e["labels"]) >= needed
    ]
    kept.sort(key=lambda e: (-e["coverage"], len(e["suffix"]), e["suffix"]))
    return kept[:MAX_SUFFIXES_SHOWN]


def discover_name_templates(
    llm: Any, table: str, field: str, labels: list[str], standards: list[str],
    context_rows: list[dict], source_name: str,
) -> list[str] | None:
    """Lets the agent find out WHICH VARIANT of a concept the source means,
    instead of a person declaring it.

    The vocabulary is searched for the sampled labels; the qualifiers found
    for most of them (e.g. ' [Susceptibility] by Minimum inhibitory
    concentration (MIC)') are shown to the model together with real rows, and
    it picks the ones the rows support, in order of preference. It can only
    choose a qualifier that was actually found. The result is a list of name
    templates ('{label}' + qualifier) applied by EXACT name to every label.

    Returns None when there is nothing to decide (no qualifier is consistent
    across the labels, or the model finds none that fits) - the lookup then
    stays a plain exact-name search. Cached per (source, table, field) as an
    'llm_suggested' entry a person can confirm or correct."""
    cached = get_cached_resolution(source_name, NAME_PATTERN_CACHE_KIND, table, field)
    if cached is not None and isinstance(cached.get("name_templates"), list):
        return cached["name_templates"] or None

    candidates = collect_suffix_candidates(labels, standards)
    if not any(c["suffix"] for c in candidates):
        return None  # nothing but the label itself: no variant to choose from

    listing = "\n".join(
        f"  - {json.dumps(c['suffix'], ensure_ascii=False)}  "
        f"({c['coverage']}/{len(labels)} labels, domain: "
        f"{', '.join(f'{d} x{n}' for d, n in sorted(c['domains'].items(), key=lambda kv: -kv[1]))})"
        for c in candidates
    )
    prompt = LOCAL_VOCAB_NAME_PATTERN_PROMPT.format(
        table=table, field=field, labels=", ".join(labels[:3]), n_labels=len(labels),
        suffixes=listing, rows=json.dumps(context_rows, ensure_ascii=False, indent=2),
    )
    try:
        parsed = parse_json_response(llm.invoke(prompt).content)
    except ValueError:
        return None

    offered = {c["suffix"] for c in candidates}
    chosen = parsed.get("suffixes")
    if not isinstance(chosen, list):
        return None
    suffixes = [x for x in chosen if isinstance(x, str) and x in offered]
    templates = ["{label}" + x for x in dict.fromkeys(suffixes)]  # order kept, no duplicates

    parsed["name_templates"] = templates
    parsed["offered_suffixes"] = [c["suffix"] for c in candidates]
    store_resolution(source_name, NAME_PATTERN_CACHE_KIND, table, field, parsed)
    return templates or None
