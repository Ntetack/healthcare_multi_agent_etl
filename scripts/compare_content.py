"""
Compares ACTUAL CONTENT (not just row counts) between two OMOP
databases - typically this project's own restricted 9-table pipeline
vs a fuller reference like ETL-Synthea, which isn't restricted to a
9-table scope and therefore populates more tables/fields.

Two independent comparisons - use either or both:

  1. SCHEMA COVERAGE (--mode coverage): for each of the 9 tables of B1, which
     fields does the reference populate that we don't (and vice
     versa), and for fields both populate, their respective null
     rates. No join needed - purely structural.

  2. ROW-LEVEL CONTENT (--mode content, --mode row_content): for a given
     table, compares actual field values person-by-person. Since person_id is an
     independently auto-generated surrogate key in EACH system (never
     directly comparable), a CROSSWALK is built first from the
     ORIGINAL source file (e.g. patients.csv), which has every raw
     identifier BOTH systems might have chosen as person_source_value
     (Id, SSN, etc.) - this is the only reliable bridge, regardless of
     which convention either system happened to use.

How a row-level comparison is scored (see compare_frames):
  - A field is either CONTENT (what the row means: concept ids, dates, measured
    values, units) or PROVENANCE (how the source wrote it: *_source_value,
    *_source_concept_id). Only the content fields make up the agreement score.
    A provenance field legitimately differs between two representations of the
    same data ('female' and 'F'), so it is reported apart and never lowers the score.
  - Two values are compared with the rule of their kind (see values_agree): a
    date by its day, a measured value within the rounding of the less precise
    side, a label without regard to case or spacing, a concept by its id.
  - The existence of the rows is a separate question from their content, and
    is reported as coverage: how much of the reference was found at all.

Usage:
    # Schema coverage - no crosswalk needed
    python scripts/compare_content.py --mode coverage \\
        --b0-db-host localhost --b0-db-name etl_synthea_db --b0-schema public

    # Content comparison - needs the original patients.csv as the bridge
    python scripts/compare_content.py --mode content --table condition_occurrence \\
        --patients-csv data/raw/hospital_a/batch054/patients.csv \\
        --b1-source-column Id --b0-source-column Id \\
        --b0-db-host localhost --b0-db-name etl_synthea_db --b0-schema public
"""
from __future__ import annotations

import argparse
import contextlib
import os
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.tools.database.db import session_scope as b1_session_scope

# The 9 tables this project builds - coverage is only ever compared
# for these, never the reference's other tables (LOCATION, PROVIDER,
# COST, ...) which this project doesn't attempt at all.
OUR_TABLES = [
    "person", "visit_occurrence", "condition_occurrence", "drug_exposure",
    "measurement", "procedure_occurrence", "observation", "death", "observation_period",
]


@contextlib.contextmanager
def _remote_session_scope(db_url: str):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _get_columns(session, schema: str, table: str) -> dict[str, dict]:
    rows = session.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table"
        ),
        {"schema": schema, "table": table},
    ).fetchall()
    return {r[0] for r in rows}


def _null_rate(session, schema: str, table: str, column: str) -> float | None:
    total = session.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}")).scalar_one()
    if total == 0:
        return None
    nulls = session.execute(
        text(f"SELECT COUNT(*) FROM {schema}.{table} WHERE {column} IS NULL")
    ).scalar_one()
    return 100 * nulls / total


def compare_coverage(b1_schema: str, b0_session_scope, b0_schema: str) -> list[str]:
    lines = ["# Schema scope comparison (fields/tables)", ""]
    with b1_session_scope() as b1_session, b0_session_scope() as b0_session:
        for table in OUR_TABLES:
            b1_cols = _get_columns(b1_session, b1_schema, table)
            b0_cols = _get_columns(b0_session, b0_schema, table)

            if not b0_cols:
                lines.append(f"## {table} — absent from B0 (or named differently)\n")
                continue
            if not b1_cols:
                lines.append(f"## {table} — absent from B1\n")
                continue

            only_b0 = b0_cols - b1_cols
            only_b1 = b1_cols - b0_cols
            common = b1_cols & b0_cols

            lines.append(f"## {table}")
            if only_b0:
                lines.append(f"  Fields populated by B0 but absent from B1 : {sorted(only_b0)}")
            if only_b1:
                lines.append(f"  Fields present in B1 but absent from B0 : {sorted(only_b1)}")

            lines.append("  Taux de NULL sur les champs communs :")
            for col in sorted(common):
                b1_rate = _null_rate(b1_session, b1_schema, table, col)
                b0_rate = _null_rate(b0_session, b0_schema, table, col)
                if b1_rate is None or b0_rate is None:
                    continue
                marker = "  ⚠️" if abs(b1_rate - b0_rate) > 20 else "  "
                lines.append(f"{marker} {col}: B1={b1_rate:.0f}% NULL, B0={b0_rate:.0f}% NULL")
            lines.append("")
    return lines


def build_crosswalk(
    patients_csv: str, b1_source_column: str, b0_source_column: str,
    b1_schema: str, b0_session_scope, b0_schema: str,
) -> pd.DataFrame:
    """Builds b1_person_id <-> b0_person_id via the ORIGINAL
    patients.csv - the only reliable bridge, since each system's
    person_source_value may follow a DIFFERENT convention (UUID, SSN,
    ...) that the other system never sees."""
    patients = pd.read_csv(patients_csv, dtype=str)

    with b1_session_scope() as b1_session:
        b1_person = pd.read_sql(
            text(f"SELECT person_id, person_source_value FROM {b1_schema}.person"), b1_session.connection()
        )
    with b0_session_scope() as b0_session:
        b0_person = pd.read_sql(
            text(f"SELECT person_id, person_source_value FROM {b0_schema}.person"), b0_session.connection()
        )

    # Built with explicitly distinct names, even when
    # b1_source_column and b0_source_column happen to be the SAME
    # real column (e.g. both "Id") - selecting the same column twice
    # via patients[[col, col]] produces a DataFrame with duplicate
    # column labels, which breaks pandas' merge() with a confusing
    # "column label is not unique" error.
    bridge = patients[[b1_source_column, b0_source_column]].copy()
    bridge.columns = ["_bridge_our", "_bridge_their"]
    bridge = bridge.drop_duplicates()
    crosswalk = bridge.merge(
        b1_person, left_on="_bridge_our", right_on="person_source_value", how="inner"
    ).rename(columns={"person_id": "b1_person_id"})
    crosswalk = crosswalk.merge(
        b0_person, left_on="_bridge_their", right_on="person_source_value", how="inner",
        suffixes=("_our", "_their"),
    ).rename(columns={"person_id": "b0_person_id"})

    return crosswalk[["b1_person_id", "b0_person_id"]]


def compare_content(
    table: str, fields: list[str], crosswalk: pd.DataFrame,
    b1_schema: str, b0_session_scope, b0_schema: str,
) -> list[str]:
    lines = [f"# Content comparison — {table}", ""]
    lines.append(f"Patient matches found : {len(crosswalk)}")
    lines.append("")

    field_list = ", ".join(fields)
    with b1_session_scope() as b1_session:
        b1_rows = pd.read_sql(
            text(f"SELECT person_id, {field_list} FROM {b1_schema}.{table}"), b1_session.connection()
        )
    with b0_session_scope() as b0_session:
        b0_rows = pd.read_sql(
            text(f"SELECT person_id, {field_list} FROM {b0_schema}.{table}"), b0_session.connection()
        )

    b1_rows = b1_rows.merge(crosswalk, left_on="person_id", right_on="b1_person_id")
    b0_rows = b0_rows.merge(crosswalk, left_on="person_id", right_on="b0_person_id")

    for field in fields:
        b1_values = set(b1_rows[field].dropna().astype(str))
        b0_values = set(b0_rows[field].dropna().astype(str))
        common = b1_values & b0_values
        only_b1 = b1_values - b0_values
        only_b0 = b0_values - b1_values
        lines.append(f"## {field}")
        lines.append(f"  Common values : {len(common)}")
        lines.append(f"  Values ONLY in B1 : {len(only_b1)} (ex: {list(only_b1)[:5]})")
        lines.append(f"  Values ONLY in B0 : {len(only_b0)} (ex: {list(only_b0)[:5]})")
        lines.append("")
    return lines


# ---------------------------------------------------------------------------
# How two values are judged equal
# ---------------------------------------------------------------------------
# The rule that decides whether two values agree depends on what the field IS:
#   concept   a concept id; 0 is "no matching concept" and counts as missing
#   date      a date: only the calendar day is compared
#   datetime  a timestamp: the day when either side has no time of day (a date
#             stored as midnight), the second otherwise
#   number    a measured value: equal within the rounding of the LESS precise
#             side (19.38 and 19.4 agree, 1.0 and 3.0 do not)
#   text      a label: case and spacing are ignored
#   exact     anything else (a year, a month): numeric-aware equality

KINDS = ("concept", "date", "datetime", "number", "text", "exact")
NUMBER_FIELDS = {"value_as_number", "quantity", "range_low", "range_high", "days_supply", "refills"}

AGREE, DIFFER, ONE_MISSING, BOTH_MISSING = "agree", "differ", "one_missing", "both_missing"


def infer_kind(field: str) -> str:
    """The comparison rule of a field, from its name: a convention of the
    OMOP CDM, used when a table is described by a plain list of fields."""
    if field.endswith("_concept_id"):
        return "concept"
    if field.endswith("_datetime"):
        return "datetime"
    if field.endswith("_date"):
        return "date"
    if field in NUMBER_FIELDS:
        return "number"
    if field.endswith("_source_value") or field in {"value_as_string", "stop_reason"}:
        return "text"
    return "exact"


def is_missing(value, kind: str = "exact") -> bool:
    """None, NaN, NaT, an empty string, and for a concept the id 0."""
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass
    if isinstance(value, str) and not value.strip():
        return True
    if kind == "concept":
        try:
            return int(value) == 0
        except (TypeError, ValueError):
            return False
    return False


def _normalise_text(value) -> str:
    return " ".join(str(value).split()).casefold()


def _decimals(value) -> int:
    try:
        exponent = Decimal(str(value).strip()).as_tuple().exponent
    except InvalidOperation:
        return 0
    return max(0, -exponent) if isinstance(exponent, int) else 0


def _has_time_of_day(ts: pd.Timestamp) -> bool:
    return (ts.hour, ts.minute, ts.second, ts.microsecond) != (0, 0, 0, 0)


def values_agree(kind: str, a, b) -> bool:
    """Whether two PRESENT values agree under the rule of their kind."""
    if kind == "concept":
        try:
            return int(a) == int(b)
        except (TypeError, ValueError):
            return _normalise_text(a) == _normalise_text(b)
    if kind in ("date", "datetime"):
        ta, tb = pd.to_datetime(a, errors="coerce"), pd.to_datetime(b, errors="coerce")
        if pd.isna(ta) or pd.isna(tb):
            return _normalise_text(a) == _normalise_text(b)
        if kind == "datetime" and _has_time_of_day(ta) and _has_time_of_day(tb):
            return ta.floor("s") == tb.floor("s")
        return ta.date() == tb.date()
    if kind == "number":
        try:
            fa, fb = float(a), float(b)
        except (TypeError, ValueError):
            return _normalise_text(a) == _normalise_text(b)
        digits = min(_decimals(a), _decimals(b))
        return abs(fa - fb) <= 0.5 * 10 ** (-digits) + 1e-9
    if kind == "text":
        return _normalise_text(a) == _normalise_text(b)
    try:                                       # exact: 1976 and 1976.0 are the same year
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def _field_states(kind: str, b1: pd.Series, b0: pd.Series) -> np.ndarray:
    """For each pair of values: agree, differ, one_missing or both_missing."""
    states = []
    for a, b in zip(b1.tolist(), b0.tolist()):
        missing_a, missing_b = is_missing(a, kind), is_missing(b, kind)
        if missing_a and missing_b:
            states.append(BOTH_MISSING)
        elif missing_a or missing_b:
            states.append(ONE_MISSING)
        else:
            states.append(AGREE if values_agree(kind, a, b) else DIFFER)
    return np.array(states, dtype=object)


def _pct(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 1) if whole else None


def spec_from_lists(table: str, natural_key_fields: list[str], compare_fields: list[str], exclude_fields: list[str]) -> dict:
    """A table description from the plain lists of the command line: the kind of
    each field is inferred from its name, and a *_source_value or
    *_source_concept_id is a provenance field."""
    content, provenance = {}, {}
    for field in compare_fields:
        if field in natural_key_fields or field in exclude_fields:
            continue
        target = provenance if field.endswith(("_source_value", "_source_concept_id")) else content
        target[field] = infer_kind(field)
    return {"table": table, "key": natural_key_fields, "content": content,
            "provenance": provenance, "ignored": list(exclude_fields)}


# ---------------------------------------------------------------------------
# Which fields are compared when EVERY field of a table is compared
# ---------------------------------------------------------------------------
# A field is left out when comparing it would test something other than the
# quality of the mapping:
#   - a record type concept (*_type_concept_id): a convention the batch metadata
#     declares, applied to every row, never derived from the data;
#   - a foreign key to a table outside the scope of the study (provider, care
#     site, location, visit detail);
#   - a surrogate identifier (person_id, drug_exposure_id, ...): each system
#     generates its own, so two correct databases never share them.
OUT_OF_SCOPE_FIELDS = {
    "provider_id", "care_site_id", "location_id", "visit_detail_id",
    "preceding_visit_occurrence_id", "preceding_visit_detail_id",
}


def is_excluded_field(field: str) -> bool:
    """True for a field that is set by convention, out of scope, or a surrogate key."""
    if field.endswith("_type_concept_id") or field in OUT_OF_SCOPE_FIELDS:
        return True
    return field.endswith("_id") and not field.endswith("_concept_id")


def expand_spec(spec: dict, b1_columns: set, b0_columns: set) -> dict:
    """The spec of a table extended to EVERY field either schema has, except the
    key, the fields the spec ignores and the excluded fields (see
    is_excluded_field). A field already described keeps its kind; a new one gets
    the kind inferred from its name, and is provenance if it is a source value."""
    key, ignored = set(spec["key"]), set(spec.get("ignored", []))
    content, provenance = dict(spec.get("content", {})), dict(spec.get("provenance", {}))
    for field in sorted(set(b1_columns) | set(b0_columns)):
        if field in key or field in ignored or field in content or field in provenance or is_excluded_field(field):
            continue
        target = provenance if field.endswith(("_source_value", "_source_concept_id")) else content
        target[field] = infer_kind(field)
    return {**spec, "content": content, "provenance": provenance}


# Why two systems differ on a field, as far as a rule can tell. The remaining
# causes (an alternative but valid source column, or a mapping error of B1)
# need a human reading of examples: they are left as `to_review`.
CAUSES = (
    "agree", "provenance", "baseline_not_populated", "b1_not_populated", "empty_both",
    "baseline_not_populated_on_some_rows", "b1_not_populated_on_some_rows", "baseline_constant", "to_review",
)


def auto_cause(role: str, status: str, differ: int, only_b1: int, only_b0: int, reference_values_when_differ: set) -> str:
    """The first cause that applies. `status` is compared, empty_both, never_b1 or only_b1."""
    if status == "empty_both":
        return "empty_both"
    if status == "never_b1":
        return "b1_not_populated"
    if status == "only_b1":
        return "baseline_not_populated"
    if not (differ or only_b1 or only_b0):
        return "agree"
    if role == "provenance":
        return "provenance"
    if only_b1 and not differ and not only_b0:
        return "baseline_not_populated_on_some_rows"
    if only_b0 and not differ and not only_b1:
        return "b1_not_populated_on_some_rows"
    if differ and len(reference_values_when_differ) == 1 and not (only_b1 or only_b0):
        return "baseline_constant"
    return "to_review"


def _signature(frame: pd.DataFrame, fields: dict[str, str]) -> list[str]:
    """A sortable text for each row, made of its compared values: it brings
    identical rows next to each other, so that duplicates of a key are paired
    with their true counterpart and not with whichever row came first."""
    columns = [frame[f].tolist() for f in fields]
    return ["|".join("" if is_missing(v) else _normalise_text(v) for v in row) for row in zip(*columns)] if columns else [""] * len(frame)


def compare_frames(
    spec: dict, b1_rows_all: pd.DataFrame, b0_rows_all: pd.DataFrame, crosswalk: pd.DataFrame,
    skipped_columns: list[str] | tuple = (),
) -> tuple[list[str], dict]:
    """Row-level comparison of one table, on frames already read from the two
    systems (each with a `person_id` column and the columns of the spec).
    Pure: it neither reads a database nor writes a file.

    Reports, in order: the volumes on each side, whether each row EXISTS on the
    other side (coverage), then how the matched rows AGREE on their content
    fields (the score), and on their provenance fields (reported apart).

    Returns (lines, summary): `lines` is the human-readable report and
    `summary` the same facts as a dict, for the cross-table report."""
    table, key = spec["table"], list(spec["key"])
    ignored = set(spec.get("ignored", [])) | set(key)
    content = {f: k for f, k in spec.get("content", {}).items() if f not in ignored}
    provenance = {f: k for f, k in spec.get("provenance", {}).items() if f not in ignored}
    present = set(b1_rows_all.columns) & set(b0_rows_all.columns)
    content = {f: k for f, k in content.items() if f in present}
    provenance = {f: k for f, k in provenance.items() if f in present}

    lines = [f"# Row-level comparison — {table}", "", f"Natural key: person + {key}", ""]
    summary: dict = {
        "table": table, "natural_key": key,
        "b1_total_rows": len(b1_rows_all), "b0_total_rows": len(b0_rows_all),
        "b1_rows": 0, "b0_rows": 0, "matched_rows": 0,
        "b1_duplicates": 0, "b0_duplicates": 0, "only_b1_count": 0, "only_b0_count": 0,
        "coverage_pct": None, "precision_pct": None,
        "content_agree_rows": None, "content_agree_pct": None,
        "content_cells": None, "content_cell_pct": None, "provenance_cell_pct": None,
        "per_field": {}, "gaps": {}, "date_shifted_keys": 0,
        "field_details": [], "field_mean_pct": None,
    }
    # The key fields identify the rows: they agree by construction, so they are
    # listed (to show they were not compared) and never scored.
    for field in key:
        summary["field_details"].append({
            "table": table, "field": field, "role": "key", "kind": infer_kind(field), "status": "in_key",
            "matched_rows": None, "present_b1": None, "present_b0": None, "both_present": None,
            "agree": None, "differ": None, "only_b1": None, "only_b0": None, "agree_pct": None,
            "cause_auto": "matched_by_construction", "example_b1": "", "example_b0": "",
        })

    lines += ["## Raw volumes (before any filtering)",
              f"  B1: {len(b1_rows_all)} rows", f"  B0: {len(b0_rows_all)} rows",
              f"  Patient matches available (through the patient bridge) : {len(crosswalk)}", ""]

    b1_rows = b1_rows_all.merge(crosswalk, left_on="person_id", right_on="b1_person_id")
    b0_rows = b0_rows_all.merge(crosswalk, left_on="person_id", right_on="b0_person_id")
    summary["b1_rows"], summary["b0_rows"] = len(b1_rows), len(b0_rows)
    lines += ["## Volumes after restriction to the common patients",
              f"  B1: {len(b1_rows)} rows ({len(b1_rows_all) - len(b1_rows)} excluded - patient not matched)",
              f"  B0: {len(b0_rows)} rows ({len(b0_rows_all) - len(b0_rows)} excluded - patient not matched)", ""]

    join_keys = ["b1_person_id"] + key
    b1_dupes = int(b1_rows.duplicated(subset=join_keys).sum())
    b0_dupes = int(b0_rows.duplicated(subset=join_keys).sum())
    summary["b1_duplicates"], summary["b0_duplicates"] = b1_dupes, b0_dupes
    if b1_dupes or b0_dupes:
        lines += [f"⚠️  NON-UNIQUE KEY: {b1_dupes} duplicate(s) in B1, {b0_dupes} in B0, on "
                  f"(person + {key}). Rows sharing a key are paired by the SIGNATURE of their values "
                  f"(identical rows are paired together), but a key that really identifies a row "
                  f"- with a date or a time added - would make the comparison more reliable.", ""]

    b1_keys_series = b1_rows[join_keys].apply(tuple, axis=1) if len(b1_rows) else pd.Series([], dtype=object)
    b0_keys_series = b0_rows[join_keys].apply(tuple, axis=1) if len(b0_rows) else pd.Series([], dtype=object)
    b1_keys, b0_keys = set(b1_keys_series), set(b0_keys_series)
    only_b1_keys, only_b0_keys, common_keys = b1_keys - b0_keys, b0_keys - b1_keys, b1_keys & b0_keys
    summary["only_b1_count"], summary["only_b0_count"] = len(only_b1_keys), len(only_b0_keys)

    lines += ["## Existence des rows (avant de comparer leur contenu)",
              f"  Keys present on both sides : {len(common_keys)}",
              f"  Keys ONLY in B1 : {len(only_b1_keys)}",
              f"  Keys ONLY in B0 : {len(only_b0_keys)}"]
    if only_b1_keys:
        lines.append(f"    ex: {list(only_b1_keys)[:3]}")
    if only_b0_keys:
        lines.append(f"    ex: {list(only_b0_keys)[:3]}")

    # Same person and same event, but another date: a different problem from a
    # row that is simply absent, and the first thing to rule out.
    relaxed = [k for k in key if infer_kind(k) not in ("date", "datetime")]
    if relaxed != key and (only_b1_keys or only_b0_keys):
        relaxed_columns = ["b1_person_id"] + relaxed
        b1_relaxed = {tuple(r) for r in b1_rows[b1_keys_series.isin(only_b1_keys)][relaxed_columns].values}
        b0_relaxed = {tuple(r) for r in b0_rows[b0_keys_series.isin(only_b0_keys)][relaxed_columns].values}
        shifted = len(b1_relaxed & b0_relaxed)
        summary["date_shifted_keys"] = shifted
        if shifted:
            lines.append(
                f"  Parmi elles, {shifted} combinaison(s) (personne + {relaxed}) existent des DEUX côtés avec une "
                f"AUTRE date : probablement le même événement, daté différemment, plutôt qu'une ligne absente."
            )
    lines.append("")

    # Pairing inside a group of duplicated keys: rows are sorted by the
    # signature of their values first, then paired rank to rank, which gives
    # at most one counterpart to each row (no cartesian product).
    all_fields = {**content, **provenance}
    b1_rows, b0_rows = b1_rows.copy(), b0_rows.copy()
    b1_rows["_signature"], b0_rows["_signature"] = _signature(b1_rows, all_fields), _signature(b0_rows, all_fields)
    b1_rows = b1_rows.sort_values(join_keys + ["_signature"], kind="mergesort")
    b0_rows = b0_rows.sort_values(join_keys + ["_signature"], kind="mergesort")
    b1_rows["_dup_rank"] = b1_rows.groupby(join_keys, dropna=False).cumcount()
    b0_rows["_dup_rank"] = b0_rows.groupby(join_keys, dropna=False).cumcount()
    matched = b1_rows.merge(b0_rows, on=join_keys + ["_dup_rank"], how="inner", suffixes=("_b1", "_b0"))
    summary["matched_rows"] = len(matched)
    summary["coverage_pct"] = _pct(len(matched), len(b0_rows))
    summary["precision_pct"] = _pct(len(matched), len(b1_rows))
    lines.append(f"Matched rows (same person + same natural key) : {len(matched)}")
    if summary["coverage_pct"] is not None:
        lines.append(f"  Coverage of B0: {len(matched)}/{len(b0_rows)} ({summary['coverage_pct']}%) - "
                     f"share of the B0 rows found in B1")
        lines.append(f"  Row precision: {len(matched)}/{len(b1_rows)} ({summary['precision_pct']}%) - "
                     f"share of the B1 rows that also exist in B0")
    lines.append("")

    if matched.empty:
        lines.append("No matched row: the content cannot be compared.")
        lines.append("")
        return lines, summary

    # ----- field by field
    scored = {"content": {}, "provenance": {}}
    for role, fields in (("content", content), ("provenance", provenance)):
        for field, kind in fields.items():
            if f"{field}_b1" not in matched.columns or f"{field}_b0" not in matched.columns:
                continue
            b1_values, b0_values = matched[f"{field}_b1"].tolist(), matched[f"{field}_b0"].tolist()
            states = _field_states(kind, matched[f"{field}_b1"], matched[f"{field}_b0"])
            present_b1 = np.array([not is_missing(v, kind) for v in b1_values], dtype=bool)
            present_b0 = np.array([not is_missing(v, kind) for v in b0_values], dtype=bool)
            n_ours, n_theirs = int(present_b1.sum()), int(present_b0.sum())
            if n_ours == 0 and n_theirs == 0:
                summary["gaps"][field] = "empty on both sides"
                status = "empty_both"
            elif n_ours == 0:
                summary["gaps"][field] = "never populated in B1"
                status = "never_b1"
            elif n_theirs == 0:
                summary["gaps"][field] = "populated only in B1"
                status = "only_b1"
            else:
                scored[role][field] = (kind, states)
                status = "compared"
            differ_idx = np.where(states == DIFFER)[0]
            only_b1 = int((present_b1 & ~present_b0).sum())
            only_b0 = int((~present_b1 & present_b0).sum())
            compared_rows = int((states != BOTH_MISSING).sum())
            agree = int((states == AGREE).sum())
            first = next(iter(np.where((states == DIFFER) | (states == ONE_MISSING))[0]), None)
            summary["field_details"].append({
                "table": table, "field": field, "role": role, "kind": kind, "status": status,
                "matched_rows": len(matched), "present_b1": n_ours, "present_b0": n_theirs,
                "both_present": int((present_b1 & present_b0).sum()), "agree": agree,
                "differ": int(len(differ_idx)), "only_b1": only_b1, "only_b0": only_b0,
                "agree_pct": _pct(agree, compared_rows) if status == "compared" else None,
                "cause_auto": auto_cause(
                    role, status, int(len(differ_idx)), only_b1, only_b0,
                    {_normalise_text(b0_values[i]) for i in differ_idx[:2000]}),
                "example_b1": "" if first is None else repr(b1_values[first]),
                "example_b0": "" if first is None else repr(b0_values[first]),
            })

    def field_lines(role: str, heading: str) -> None:
        if not scored[role]:
            return
        lines.append(heading)
        lines.append("")
        for field, (kind, states) in scored[role].items():
            relevant = states != BOTH_MISSING
            total, agree = int(relevant.sum()), int((states == AGREE).sum())
            pct = _pct(agree, total)
            summary["per_field"][field] = {"role": role, "kind": kind, "agree": agree, "total": total, "pct": pct}
            lines.append(f"## {field} : {agree}/{total} lignes concordent ({pct}%)  [{kind}]")
            bad = np.where((states == DIFFER) | (states == ONE_MISSING))[0]
            for i in bad[:3]:
                row = matched.iloc[i]
                lines.append(f"    ex: B1={row[f'{field}_b1']!r} vs B0={row[f'{field}_b0']!r}")
            lines.append("")

    field_lines("content", "# Content fields (what the row means) - they make up the score")
    field_lines("provenance", "# Provenance fields (how the source writes it) - reported apart, not scored")

    if summary["gaps"]:
        lines += ["# Scope gaps (fields left out of the score)", ""]
        for field, why in summary["gaps"].items():
            lines.append(f"  {field} : {why}")
    if skipped_columns:
        lines.append(f"  Columns missing from one of the two schemas (not compared) : {sorted(skipped_columns)}")
    if summary["gaps"] or skipped_columns:
        lines.append("")

    # ----- scores
    sem = scored["content"]
    if sem:
        bad_row = np.zeros(len(matched), dtype=bool)
        cells = agree_cells = 0
        for _, (_, states) in sem.items():
            bad_row |= (states == DIFFER) | (states == ONE_MISSING)
            cells += int((states != BOTH_MISSING).sum())
            agree_cells += int((states == AGREE).sum())
        agree_rows = int((~bad_row).sum())
        summary.update(content_agree_rows=agree_rows, content_agree_pct=_pct(agree_rows, len(matched)),
                       content_cells=cells, content_cell_pct=_pct(agree_cells, cells))
    field_pcts = [v["pct"] for v in summary["per_field"].values() if v["role"] == "content" and v["pct"] is not None]
    if field_pcts:
        summary["field_mean_pct"] = round(sum(field_pcts) / len(field_pcts), 1)
    prov = scored["provenance"]
    if prov:
        cells = sum(int((st != BOTH_MISSING).sum()) for _, (_, st) in prov.items())
        agree_cells = sum(int((st == AGREE).sum()) for _, (_, st) in prov.items())
        summary["provenance_cell_pct"] = _pct(agree_cells, cells)

    lines.append("## Summary")
    if summary["coverage_pct"] is not None:
        lines.append(f"  Coverage of B0: {summary['coverage_pct']}%")
    if sem:
        lines.append(f"  Row-level agreement (matched rows whose content fields ALL agree) : "
                     f"{summary['content_agree_rows']}/{len(matched)} ({summary['content_agree_pct']}%)")
        lines.append(f"  Content agreement by value (all compared values) : {summary['content_cell_pct']}%")
        lines.append(f"  Mean field agreement (unweighted mean of the {len(field_pcts)} compared content fields) : "
                     f"{summary['field_mean_pct']}%")
    else:
        lines.append("  Content agreement: no comparable content field.")
    if prov:
        lines.append(f"  Provenance agreement (not scored) : {summary['provenance_cell_pct']}%")
    lines.append("")
    return lines, summary


def _comparable_columns(requested: list[str], b1_columns: set, b0_columns: set) -> tuple[list[str], list[str]]:
    """The requested columns that exist in BOTH schemas, and those that do not."""
    usable = [c for c in requested if c in b1_columns and c in b0_columns]
    return usable, [c for c in requested if c not in usable]


def compare_table(
    spec: dict, crosswalk: pd.DataFrame, b1_schema: str, b0_session_scope, b0_schema: str,
) -> tuple[list[str], dict]:
    """Reads a table from both schemas, restricted to the columns they both
    have, and compares it (see compare_frames)."""
    table = spec["table"]
    with b1_session_scope() as b1_session:
        b1_columns = _get_columns(b1_session, b1_schema, table)
    with b0_session_scope() as b0_session:
        b0_columns = _get_columns(b0_session, b0_schema, table)
    if spec.get("all_fields"):
        spec = expand_spec(spec, b1_columns, b0_columns)
    requested = list(dict.fromkeys(
        ["person_id"] + list(spec["key"]) + list(spec.get("content", {})) + list(spec.get("provenance", {}))
    ))
    usable, skipped = _comparable_columns(requested, b1_columns, b0_columns)
    missing_key = [c for c in ["person_id"] + list(spec["key"]) if c in skipped]
    if missing_key:
        lines = [f"# Row-level comparison — {table}", "",
                 f"Comparison impossible: key column(s) missing from one of the schemas : {missing_key}", ""]
        return lines, {"table": table, "natural_key": list(spec["key"]), "error": f"missing key columns {missing_key}"}

    field_list = ", ".join(usable)
    with b1_session_scope() as b1_session:
        b1_frame = pd.read_sql(text(f"SELECT {field_list} FROM {b1_schema}.{table}"), b1_session.connection())
    with b0_session_scope() as b0_session:
        b0_frame = pd.read_sql(text(f"SELECT {field_list} FROM {b0_schema}.{table}"), b0_session.connection())
    lines, summary = compare_frames(spec, b1_frame, b0_frame, crosswalk, skipped_columns=skipped)
    # A field one schema does not have at all is a gap of scope too: listed with its cause.
    for field in skipped:
        if field == "person_id" or field in spec["key"]:
            continue
        side = "b1_not_populated" if field not in b1_columns else "baseline_not_populated"
        role = "provenance" if field.endswith(("_source_value", "_source_concept_id")) else "content"
        summary.setdefault("field_details", []).append({
            "table": table, "field": field, "role": role, "kind": infer_kind(field),
            "status": "absent_from_b1_schema" if field not in b1_columns else "absent_from_baseline_schema",
            "matched_rows": None, "present_b1": None, "present_b0": None, "both_present": None,
            "agree": None, "differ": None, "only_b1": None, "only_b0": None, "agree_pct": None,
            "cause_auto": side, "example_b1": "", "example_b0": "",
        })
    return lines, summary


def compare_content_by_row(
    table: str, natural_key_fields: list[str], compare_fields: list[str], exclude_fields: list[str],
    crosswalk: pd.DataFrame, b1_schema: str, b0_session_scope, b0_schema: str,
) -> tuple[list[str], dict]:
    """Row-level comparison described by plain lists of fields (the command
    line form): the kind of each field is inferred from its name. See
    compare_table for the full description with explicit roles and kinds."""
    spec = spec_from_lists(table, natural_key_fields, compare_fields, exclude_fields)
    return compare_table(spec, crosswalk, b1_schema, b0_session_scope, b0_schema)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["coverage", "content", "row_content"], required=True)
    parser.add_argument("--b1-schema", "--our-schema", dest="b1_schema", default="omop_temp")
    parser.add_argument("--b0-db-host", "--their-db-host", dest="b0_db_host", required=True)
    parser.add_argument("--b0-db-port", "--their-db-port", dest="b0_db_port", default="5432")
    parser.add_argument("--b0-db-name", "--their-db-name", dest="b0_db_name", required=True)
    parser.add_argument("--b0-db-user", "--their-db-user", dest="b0_db_user", required=True)
    parser.add_argument("--b0-db-password", "--their-db-password", dest="b0_db_password", default=None)
    parser.add_argument("--b0-schema", "--their-schema", dest="b0_schema", default="public")
    parser.add_argument("--table", default=None, help="Required for --mode content/row_content")
    parser.add_argument("--fields", default=None, help="Comma-separated fields to compare")
    parser.add_argument("--natural-key", default=None,
                         help="Comma-separated fields (beyond person) forming a natural key for --mode row_content, e.g. 'condition_concept_id'")
    parser.add_argument("--exclude-fields", default="",
                         help="Comma-separated fields to skip even if requested (e.g. a fixed type_concept_id)")
    parser.add_argument("--patients-csv", default=None, help="Required for --mode content/row_content")
    parser.add_argument("--b1-source-column", "--our-source-column", dest="b1_source_column", default="Id", help="Column in patients.csv matching the person_source_value of B1")
    parser.add_argument("--b0-source-column", "--their-source-column", dest="b0_source_column", default="Id", help="Column in patients.csv matching the person_source_value of B0")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    password = args.b0_db_password or os.environ.get("DB_PASSWORD", "")
    b0_url = f"postgresql://{args.b0_db_user}:{password}@{args.b0_db_host}:{args.b0_db_port}/{args.b0_db_name}"
    b0_session_scope = lambda: _remote_session_scope(b0_url)

    if args.mode == "coverage":
        lines = compare_coverage(args.b1_schema, b0_session_scope, args.b0_schema)
    elif args.mode == "content":
        if not (args.table and args.fields and args.patients_csv):
            parser.error("--mode content requires --table, --fields, and --patients-csv")
        crosswalk = build_crosswalk(
            args.patients_csv, args.b1_source_column, args.b0_source_column,
            args.b1_schema, b0_session_scope, args.b0_schema,
        )
        lines = compare_content(
            args.table, args.fields.split(","), crosswalk,
            args.b1_schema, b0_session_scope, args.b0_schema,
        )
    else:  # row_content
        if not (args.table and args.fields and args.natural_key and args.patients_csv):
            parser.error("--mode row_content requires --table, --fields, --natural-key, and --patients-csv")
        crosswalk = build_crosswalk(
            args.patients_csv, args.b1_source_column, args.b0_source_column,
            args.b1_schema, b0_session_scope, args.b0_schema,
        )
        lines, _ = compare_content_by_row(
            args.table, args.natural_key.split(","), args.fields.split(","),
            [f for f in args.exclude_fields.split(",") if f],
            crosswalk, args.b1_schema, b0_session_scope, args.b0_schema,
        )

    report = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written : {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
