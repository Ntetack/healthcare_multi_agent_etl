"""
Fixed, human-curated value mappings - a raw source value -> concept_id
lookup that takes ABSOLUTE PRIORITY over the LLM/vocabulary search
mechanism, for fields where that automatic mechanism has proven
unreliable (e.g. Ethnicity/Visit, where the LLM's own choice of
concept has been observed to vary between otherwise-identical runs,
and where fields like MIMIC's ADMISSIONS.ethnicity conflate race and
ethnicity into a single column needing careful, deliberate splitting).

ONE consistent structure covers every fixed mapping in this project,
regardless of which resolution mechanism consumes it:

  - A VOCAB-FIELD, resolved via a PAIRED source_value field (e.g.
    race_concept_id, ethnicity_concept_id, visit_concept_id), keyed by
    the raw text value of that paired field (e.g. "WHITE", "EMERGENCY").

  - A LOCAL VOCAB field, resolved via a join to a dictionary table
    (e.g. OUTPUTEVENTS.itemid, DATETIMEEVENTS.itemid), keyed by the RAW
    ITEM IDENTIFIER itself, BEFORE any join even happens - simpler and
    more robust than matching on a resolved free-text label, since the
    identifier is a clean, unambiguous key with no whitespace/casing
    risk. Confirmed necessary in production: several MIMIC event
    tables' item labels are too source-specific to match any standard
    vocabulary by text search, yet a human-curated mapping (verified
    against real OMOP concepts, not a text-matching heuristic) DOES
    exist for many of them.

Both cases use the exact same resolve_fixed_value() function and the
exact same metadata.yaml declaration shape - only the column names
differ, never the mechanism itself.

Declared per batch in metadata.yaml, never hardcoded in code. The
mapping_file itself lives alongside the batch's metadata.yaml. A raw
value NOT found in a CSV falls through to the normal automatic
resolution - this mechanism only ever overrides values a human has
explicitly curated, never claims to cover every possible value.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def get_fixed_mapping_spec(batch_cfg: dict, target_table: str, target_field: str) -> dict | None:
    """Returns this batch's declared fixed-mapping spec for
    (target_table, target_field), or None if not declared - the
    normal, unmodified path for every field not explicitly curated."""
    return (
        batch_cfg.get("fixed_value_mappings", {})
        .get(target_table, {})
        .get(target_field)
    )


def get_fixed_mapping_spec_by_source(batch_cfg: dict, source_table: str, source_field: str) -> dict | None:
    """Like get_fixed_mapping_spec, but looked up the OTHER direction -
    by (source_table, source_field) instead of (target_table,
    target_field). Needed for mechanism 1's local vocab fields (e.g.
    OUTPUTEVENTS.itemid): unlike a vocab-field such as race_concept_id
    (whose target is always person.race_concept_id, fixed in advance),
    a local vocab field's target table is only known AFTER routing by
    the resolved concept's own domain - so at the point a fixed mapping
    would apply, only the SOURCE table/field is known yet.

    Searches every declared (target_table, target_field) entry for one
    whose own source_table/source_field matches - a small, one-time
    scan over this batch's own declarations, never a performance
    concern given how few fixed mappings a single batch declares."""
    for fields in batch_cfg.get("fixed_value_mappings", {}).values():
        for spec in fields.values():
            if spec.get("source_table") == source_table and spec.get("source_field") == source_field:
                return spec
    return None


def get_concept_domain(concept_id: int) -> str | None:
    """Looks up a KNOWN concept_id's own domain_id directly - used to
    route a fixed-mapping's already-resolved concept_id to its correct
    target table (via resolve_target), without needing any text search
    at all (the concept_id is already certain, provided by a human-
    curated CSV, not something to search for)."""
    from sqlalchemy import text as sql_text

    from app.tools.database.db import session_scope

    with session_scope() as session:
        row = session.execute(
            sql_text("SELECT domain_id FROM cdm_vocab.concept WHERE concept_id = :concept_id"),
            {"concept_id": concept_id},
        ).mappings().first()
        return row["domain_id"] if row else None


def load_fixed_mapping_table(source_folder: Path, spec: dict) -> pd.DataFrame | None:
    """Loads the CSV declared in a fixed-mapping spec, from the
    SOURCE's own root folder (data/raw/<source_name>/) - NOT the batch
    folder. These mappings are a property of the source itself (e.g.
    MIMIC's ADMISSIONS.ethnicity/admission_type values never change
    between batches), so the CSV lives once, shared across every batch
    of that source, rather than being duplicated per batch. Returns
    None if the file is missing - a human declared this mapping but
    the file isn't there, which should be visible as a failure, not a
    silent fallback."""
    mapping_path = Path(source_folder) / spec["mapping_file"]
    if not mapping_path.exists():
        return None
    return pd.read_csv(mapping_path, dtype=str)


def resolve_fixed_value(raw_value: str, mapping_table: pd.DataFrame, spec: dict) -> dict | None:
    """Looks up raw_value against the fixed mapping table's key column
    (the source field's own column name in the CSV, e.g. 'ETHNICITY',
    or a raw item identifier like 'itemid'), case-insensitively and
    whitespace-normalized (curated CSVs and raw source data don't
    always agree on casing, and neither do CSV headers vs
    metadata.yaml's own source_field casing convention). Returns a
    candidate dict shaped like map_concept()'s own return value, or
    None if this exact raw value isn't covered by the CSV - the caller
    should then fall through to the normal automatic resolution.

    A single, consistent structure covers every fixed mapping in this
    project, regardless of which mechanism consumes it (a vocab-field
    like race_concept_id, keyed by a paired source_value's raw text; or
    a local-vocab field like OUTPUTEVENTS.itemid, keyed by the raw item
    identifier itself, before any dictionary join even happens) - the
    lookup logic is identical either way, just column names differ.

    `source_concept_column` is optional: some curated files (e.g. for
    an observation derived from a local vocabulary) also provide a
    source_concept_id alongside the main resolved concept_id - if
    declared and present, it's included in the returned dict too."""
    if raw_value is None:
        return None

    key_column_declared = spec.get("source_field_column", spec["source_field"])
    value_column_declared = spec["mapping_column"]

    columns_by_lower = {c.lower(): c for c in mapping_table.columns}
    key_column = columns_by_lower.get(key_column_declared.lower())
    value_column = columns_by_lower.get(value_column_declared.lower())
    if key_column is None or value_column is None:
        return None

    normalized = str(raw_value).strip().upper()
    matches = mapping_table[mapping_table[key_column].str.strip().str.upper() == normalized]
    if matches.empty:
        return None

    concept_id = matches.iloc[0][value_column]
    if pd.isna(concept_id):
        return None

    result = {
        "concept_id": int(concept_id),
        "_match_confidence": 1.0,
        "_fixed_mapping": True,  # lets the caller distinguish this from an automatic match in its reason text
    }

    source_concept_column_declared = spec.get("source_concept_column")
    if source_concept_column_declared:
        source_concept_column = columns_by_lower.get(source_concept_column_declared.lower())
        if source_concept_column:
            source_concept_id = matches.iloc[0][source_concept_column]
            if not pd.isna(source_concept_id):
                result["source_concept_id"] = int(source_concept_id)

    return result
