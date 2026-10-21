"""
Runs the complete, standard set of table comparisons against an
external reference (e.g. ETL-Synthea) and produces ONE consolidated
report - an executive summary table across all 9 OMOP tables, followed
by the full per-table detail already produced by compare_content.py's
row_content mode.

Builds the patient crosswalk ONCE and reuses it across every table,
rather than rebuilding the identical bridge nine times.

Usage:
    python scripts/run_full_comparison.py \
        --patients-csv data/raw/hospital_a/batch007/patients.csv \
        --b0-db-host localhost --b0-db-name omop_cdm \
        --b0-schema cdm_synthea10 --b0-db-user synthea_user \
        --b0-db-password changeme \
        --output reports/batch007/full_comparison.md
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compare_content import build_crosswalk, compare_table, _remote_session_scope

# The standard 9-table comparison configuration - one entry per OMOP table this
# project builds. Edit here once to change what every future run compares.
#
# Each table is described by:
#   key         the fields, beyond the person, that identify a row on both sides
#   content    what the row MEANS: concept ids, dates, measured values, units.
#               These fields make up the agreement score.
#   provenance  how the source WROTE it (*_source_value, *_source_concept_id).
#               Reported field by field, but never part of the score: two exports
#               of the same data legitimately write 'female' and 'F'.
#   ignored     fixed ETL conventions (the type_concept_id of a table tests the
#               choice of a convention, not the quality of a mapping).
# and, for every compared field, how two values are judged equal:
#   concept   a concept id (0 = no matching concept = missing)
#   date      the calendar day
#   datetime  the day if either side has no time of day, the second otherwise
#   number    equal within the rounding of the less precise side
#   text      case and spacing ignored
#   exact     numeric-aware equality (a year, a month)
# A column that does not exist in BOTH schemas is skipped and reported, so a
# field can be listed here even if one of the two systems lacks it.
TABLE_CONFIGS = [
    {
        "table": "person",
        "key": ["person_source_value"],
        "content": {
            "gender_concept_id": "concept", "year_of_birth": "exact", "month_of_birth": "exact",
            "day_of_birth": "exact", "birth_datetime": "datetime",
            "race_concept_id": "concept", "ethnicity_concept_id": "concept",
        },
        "provenance": {
            "gender_source_value": "text", "race_source_value": "text", "ethnicity_source_value": "text",
            "gender_source_concept_id": "concept", "race_source_concept_id": "concept",
            "ethnicity_source_concept_id": "concept",
        },
        "ignored": [],
    },
    {
        "table": "visit_occurrence",
        "key": ["visit_concept_id", "visit_start_date"],
        "content": {
            "visit_start_datetime": "datetime", "visit_end_date": "date", "visit_end_datetime": "datetime",
        },
        "provenance": {"visit_source_value": "text", "visit_source_concept_id": "concept"},
        "ignored": ["visit_type_concept_id"],
    },
    {
        "table": "condition_occurrence",
        "key": ["condition_concept_id", "condition_start_date"],
        "content": {
            "condition_start_datetime": "datetime", "condition_end_date": "date",
            "condition_end_datetime": "datetime",
        },
        "provenance": {"condition_source_value": "text", "condition_source_concept_id": "concept"},
        "ignored": ["condition_type_concept_id"],
    },
    {
        "table": "drug_exposure",
        "key": ["drug_concept_id", "drug_exposure_start_date", "drug_exposure_end_date"],
        "content": {
            "drug_exposure_start_datetime": "datetime", "drug_exposure_end_datetime": "datetime",
            "quantity": "number", "days_supply": "number",
        },
        "provenance": {"drug_source_value": "text", "drug_source_concept_id": "concept"},
        "ignored": ["drug_type_concept_id"],
    },
    {
        "table": "procedure_occurrence",
        "key": ["procedure_concept_id", "procedure_date"],
        "content": {"procedure_datetime": "datetime", "quantity": "number"},
        "provenance": {"procedure_source_value": "text", "procedure_source_concept_id": "concept"},
        "ignored": ["procedure_type_concept_id"],
    },
    {
        "table": "measurement",
        "key": ["measurement_concept_id", "measurement_date"],
        "content": {
            "measurement_datetime": "datetime", "value_as_number": "number",
            "value_as_concept_id": "concept", "unit_concept_id": "concept",
        },
        "provenance": {
            "measurement_source_value": "text", "measurement_source_concept_id": "concept",
            "unit_source_value": "text", "value_source_value": "text",
        },
        "ignored": ["measurement_type_concept_id"],
    },
    {
        "table": "observation",
        "key": ["observation_concept_id", "observation_date"],
        "content": {
            "observation_datetime": "datetime", "value_as_number": "number", "value_as_string": "text",
            "value_as_concept_id": "concept", "unit_concept_id": "concept",
        },
        "provenance": {
            "observation_source_value": "text", "observation_source_concept_id": "concept",
            "unit_source_value": "text",
        },
        "ignored": ["observation_type_concept_id"],
    },
    {
        "table": "death",
        "key": ["death_date"],
        "content": {"death_datetime": "datetime", "cause_concept_id": "concept"},
        "provenance": {"cause_source_value": "text", "cause_source_concept_id": "concept"},
        "ignored": ["death_type_concept_id"],
    },
    {
        "table": "observation_period",
        "key": ["observation_period_start_date"],
        "content": {"observation_period_end_date": "date"},
        "provenance": {},
        "ignored": ["period_type_concept_id"],
    },
]


FIELD_DETAIL_COLUMNS = [
    "table", "field", "role", "kind", "status", "matched_rows", "present_b1", "present_b0", "both_present",
    "agree", "differ", "only_b1", "only_b0", "agree_pct", "cause_auto", "example_b1", "example_b0",
    "cause_manual", "note",
]


def write_field_details(all_summaries: list[dict], path: Path) -> int:
    """One row per (table, field): the agreement and the cause of each
    disagreement. `cause_auto` comes from rules; `cause_manual` and `note` are
    left empty for the human reading of the cases a rule cannot decide
    (an alternative but valid source column, or a mapping error)."""
    rows = [d for s in all_summaries for d in s.get("field_details", [])]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELD_DETAIL_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({**{c: "" for c in FIELD_DETAIL_COLUMNS}, **{k: ("" if v is None else v) for k, v in row.items()}})
    return len(rows)


def field_agreement_section(all_summaries: list[dict]) -> list[str]:
    """Per table, the unweighted mean of the agreement of the compared content
    fields (the main figure), and the number of fields behind it. Never one
    overall figure: a table with many fields would weigh more than one with few."""
    lines = ["## Field agreement by table (unweighted mean over the compared content fields)", "",
             "| Table | Fields compared | Mean field agreement | Fields below 100% |", "|---|---|---|---|"]
    for s in all_summaries:
        if s.get("error"):
            continue
        fields = [(f, v) for f, v in s.get("per_field", {}).items() if v["role"] == "content"]
        below = [f for f, v in fields if v["pct"] is not None and v["pct"] < 100]
        mean = f"{s['field_mean_pct']}%" if s.get("field_mean_pct") is not None else "n/a"
        lines.append(f"| {s['table']} | {len(fields)} | {mean} | {', '.join(below) if below else '-'} |")
    lines += ["", "The per-field detail with the cause of each disagreement is in the `*_fields.csv` file next to this report. "
              "Provenance fields are in that file too, flagged `provenance`, and are not part of the mean.", ""]
    return lines


def _fraction(part, whole) -> str:
    return f"{part}/{whole} ({round(100 * part / whole, 1)}%)" if whole else "n/a"


def build_executive_summary(all_summaries: list[dict]) -> list[str]:
    """One row per table, then three figures for the whole comparison. The
    figures answer three DIFFERENT questions, which one score used to blur:
      coverage   how much of the reference exists here at all;
      agreement  among the rows that exist on both sides, how many mean the
                 same thing (content fields only);
      reproduced the share of the reference's rows that exist here AND mean the
                 same thing: the one figure that needs both."""
    lines = ["# Full Comparison Report", "", "## Executive Summary", ""]
    lines.append("| Table | Rows (B1) | Rows (B0) | Matched | Coverage of B0 | "
                 "Content agreement | Provenance (not scored) | Note |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for s in all_summaries:
        if s.get("error"):
            lines.append(f"| {s['table']} | - | - | - | - | - | - | {s['error']} |")
            continue
        coverage = _fraction(s["matched_rows"], s["b0_rows"])
        agreement = (_fraction(s["content_agree_rows"], s["matched_rows"])
                     if s["content_agree_pct"] is not None else "n/a")
        provenance = f"{s['provenance_cell_pct']}%" if s["provenance_cell_pct"] is not None else "n/a"
        notes = []
        if s["b1_duplicates"] > 0 or s["b0_duplicates"] > 0:
            notes.append(f"non-unique key ({s['b1_duplicates']}/{s['b0_duplicates']} dupes, paired by signature)")
        if s.get("date_shifted_keys"):
            notes.append(f"{s['date_shifted_keys']} events found with another date")
        if s["only_b1_count"] > 0 or s["only_b0_count"] > 0:
            notes.append(f"{s['only_b1_count']} B1-only / {s['only_b0_count']} B0-only keys")
        lines.append(
            f"| {s['table']} | {s['b1_total_rows']} | {s['b0_total_rows']} | {s['matched_rows']} | "
            f"{coverage} | {agreement} | {provenance} | {'; '.join(notes)} |"
        )
    lines.append("")

    ok = [s for s in all_summaries if not s.get("error") and s["b0_rows"]]
    total_reference = sum(s["b0_rows"] for s in ok)
    total_matched = sum(s["matched_rows"] for s in ok)
    scored = [s for s in ok if s["content_agree_pct"] is not None]
    matched_scored = sum(s["matched_rows"] for s in scored)
    agreeing = sum(s["content_agree_rows"] for s in scored)
    if total_reference:
        lines.append(f"**Coverage of B0 (B0 rows found in B1 / B0 rows): "
                     f"{_fraction(total_matched, total_reference)}**")
        lines.append("")
    if matched_scored:
        lines.append(f"**Content agreement (matched rows whose content fields all agree, weighted by rows): "
                     f"{_fraction(agreeing, matched_scored)}**")
        lines.append("")
    if total_reference and scored:
        lines.append(f"**B0 rows reproduced with the same content (found AND agreeing): "
                     f"{_fraction(agreeing, sum(s['b0_rows'] for s in scored))}**")
        lines.append("")
    lines.append("Provenance fields (`*_source_value`, `*_source_concept_id`) are listed per table but are not part of "
                 "any figure above: they record how the source wrote a value, which two faithful exports may do differently.")
    lines.append("")
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--b1-schema", "--our-schema", dest="b1_schema", default="omop_temp")
    parser.add_argument("--b0-db-host", "--their-db-host", dest="b0_db_host", required=True)
    parser.add_argument("--b0-db-port", "--their-db-port", dest="b0_db_port", default="5432")
    parser.add_argument("--b0-db-name", "--their-db-name", dest="b0_db_name", required=True)
    parser.add_argument("--b0-db-user", "--their-db-user", dest="b0_db_user", required=True)
    parser.add_argument("--b0-db-password", "--their-db-password", dest="b0_db_password", default=None)
    parser.add_argument("--b0-schema", "--their-schema", dest="b0_schema", default="public")
    parser.add_argument("--patients-csv", required=True)
    parser.add_argument("--b1-source-column", "--our-source-column", dest="b1_source_column", default="Id")
    parser.add_argument("--b0-source-column", "--their-source-column", dest="b0_source_column", default="Id")
    parser.add_argument("--output", required=True)
    parser.add_argument("--listed-fields-only", action="store_true",
                        help="compare only the fields listed in TABLE_CONFIGS (default: every field of the tables, "
                             "except record types, out-of-scope foreign keys and surrogate identifiers)")
    args = parser.parse_args()

    password = args.b0_db_password or os.environ.get("DB_PASSWORD", "")
    b0_url = f"postgresql://{args.b0_db_user}:{password}@{args.b0_db_host}:{args.b0_db_port}/{args.b0_db_name}"
    b0_session_scope = lambda: _remote_session_scope(b0_url)

    print("Building the patient crosswalk (once, reused for all tables)...")
    crosswalk = build_crosswalk(
        args.patients_csv, args.b1_source_column, args.b0_source_column,
        args.b1_schema, b0_session_scope, args.b0_schema,
    )
    print(f"  {len(crosswalk)} patient matches found.")

    all_summaries = []
    detail_sections: list[str] = []
    for config in TABLE_CONFIGS:
        config = {**config, "all_fields": not args.listed_fields_only}
        print(f"Comparing {config['table']}...")
        lines, summary = compare_table(
            config, crosswalk, args.b1_schema, b0_session_scope, args.b0_schema,
        )
        all_summaries.append(summary)
        detail_sections.extend(lines)
        detail_sections.append("---")
        detail_sections.append("")

    report = (build_executive_summary(all_summaries) + field_agreement_section(all_summaries)
              + ["## Per-Table Detail", ""] + detail_sections)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report), encoding="utf-8")
    fields_path = output_path.with_name(output_path.stem + "_fields.csv")
    n = write_field_details(all_summaries, fields_path)
    print(f"\nFull report written: {output_path}\nField detail ({n} rows): {fields_path}")


if __name__ == "__main__":
    main()
