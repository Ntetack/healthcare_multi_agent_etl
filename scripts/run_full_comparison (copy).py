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
        --their-db-host localhost --their-db-name omop_cdm \
        --their-schema cdm_synthea10 --their-db-user synthea_user \
        --their-db-password changeme \
        --output reports/batch007/full_comparison.md
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compare_content import build_crosswalk, compare_content_by_row, _remote_session_scope

# The standard 9-table comparison configuration - one entry per OMOP
# table this project builds. Edit here once to change what every future
# run compares, rather than maintaining nine separate shell invocations.
TABLE_CONFIGS = [
    {
        "table": "person",
        "fields": ["gender_concept_id", "year_of_birth", "month_of_birth", "day_of_birth",
                   "race_concept_id", "ethnicity_concept_id", "gender_source_value",
                   "race_source_value", "ethnicity_source_value", "person_source_value"],
        "natural_key": ["person_source_value"],
        "exclude_fields": [],
    },
    {
        "table": "visit_occurrence",
        "fields": ["visit_concept_id", "visit_start_date", "visit_end_date",
                   "visit_source_value", "visit_source_concept_id"],
        "natural_key": ["visit_concept_id", "visit_start_date"],
        "exclude_fields": ["visit_type_concept_id"],
    },
    {
        "table": "condition_occurrence",
        "fields": ["condition_concept_id", "condition_source_value", "condition_source_concept_id",
                   "condition_start_date", "condition_end_date"],
        "natural_key": ["condition_concept_id", "condition_start_date"],
        "exclude_fields": ["condition_type_concept_id"],
    },
    {
        "table": "drug_exposure",
        "fields": ["drug_concept_id", "drug_source_value", "drug_source_concept_id",
                   "drug_exposure_start_date", "drug_exposure_end_date", "quantity"],
        "natural_key": ["drug_concept_id", "drug_exposure_start_date", "drug_exposure_end_date"],
        "exclude_fields": ["drug_type_concept_id"],
    },
    {
        "table": "procedure_occurrence",
        "fields": ["procedure_concept_id", "procedure_source_value", "procedure_source_concept_id",
                   "procedure_date", "quantity"],
        "natural_key": ["procedure_concept_id", "procedure_date"],
        "exclude_fields": ["procedure_type_concept_id"],
    },
    {
        "table": "measurement",
        "fields": ["measurement_concept_id", "measurement_date", "value_as_number",
                   "unit_concept_id", "measurement_source_value"],
        "natural_key": ["measurement_concept_id", "measurement_date"],
        "exclude_fields": ["measurement_type_concept_id"],
    },
    {
        "table": "observation",
        "fields": ["observation_concept_id", "observation_date", "value_as_number",
                   "value_as_string", "observation_source_value"],
        "natural_key": ["observation_concept_id", "observation_date"],
        "exclude_fields": ["observation_type_concept_id"],
    },
    {
        "table": "death",
        "fields": ["death_date", "death_datetime", "cause_concept_id", "cause_source_value"],
        "natural_key": ["death_date"],
        "exclude_fields": ["death_type_concept_id"],
    },
    {
        "table": "observation_period",
        "fields": ["observation_period_start_date", "observation_period_end_date"],
        "natural_key": ["observation_period_start_date"],
        "exclude_fields": ["period_type_concept_id"],
    },
]


def build_executive_summary(all_summaries: list[dict]) -> list[str]:
    """One row per table - the scientific, at-a-glance view: sample
    sizes, match rate, and any structural warning, before anyone reads
    a single per-table detail section."""
    lines = ["# Full Comparison Report", "", "## Executive Summary", ""]
    lines.append("| Table | Rows (ours) | Rows (reference) | Matched | Fully Identical | Warning |")
    lines.append("|---|---|---|---|---|---|")
    for s in all_summaries:
        identical = (
            f"{s['fully_identical_rows']}/{s['matched_rows']} ({s['fully_identical_pct']}%)"
            if s["fully_identical_pct"] is not None else "n/a"
        )
        warning = ""
        if s["our_duplicates"] > 0 or s["their_duplicates"] > 0:
            warning = f"⚠️ non-unique key ({s['our_duplicates']}/{s['their_duplicates']} dupes)"
        elif s["only_ours_count"] > 0 or s["only_theirs_count"] > 0:
            warning = f"{s['only_ours_count']} ours-only / {s['only_theirs_count']} reference-only"
        lines.append(
            f"| {s['table']} | {s['our_total_rows']} | {s['their_total_rows']} | "
            f"{s['matched_rows']} | {identical} | {warning} |"
        )
    lines.append("")

    # A single aggregate figure across every table with a DEFINED
    # identical-rate - weighted by matched row count rather than
    # averaging table percentages naively (a 100-row table and a
    # 10,000-row table should not count equally). Tables where the rate
    # is undefined (non-unique key, see the warning column) are
    # EXCLUDED from both the numerator and denominator - including them
    # as an implicit 0% would silently and wrongly drag down the
    # overall figure for a table that simply couldn't be scored.
    scored = [s for s in all_summaries if s["fully_identical_pct"] is not None]
    total_matched = sum(s["matched_rows"] for s in scored)
    total_identical = sum(s["fully_identical_rows"] for s in scored)
    if total_matched > 0:
        overall_pct = round(100 * total_identical / total_matched, 1)
        unscored = len(all_summaries) - len(scored)
        note = f" ({unscored} table(s) excluded - undefined due to a non-unique key)" if unscored else ""
        lines.append(f"**Overall row-level concordance across scored tables: {total_identical}/{total_matched} ({overall_pct}%){note}**")
        lines.append("")

    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--our-schema", default="omop_temp")
    parser.add_argument("--their-db-host", required=True)
    parser.add_argument("--their-db-port", default="5432")
    parser.add_argument("--their-db-name", required=True)
    parser.add_argument("--their-db-user", required=True)
    parser.add_argument("--their-db-password", default=None)
    parser.add_argument("--their-schema", default="public")
    parser.add_argument("--patients-csv", required=True)
    parser.add_argument("--our-source-column", default="Id")
    parser.add_argument("--their-source-column", default="Id")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    password = args.their_db_password or os.environ.get("DB_PASSWORD", "")
    their_url = f"postgresql://{args.their_db_user}:{password}@{args.their_db_host}:{args.their_db_port}/{args.their_db_name}"
    their_session_scope = lambda: _remote_session_scope(their_url)

    print("Building the patient crosswalk (once, reused for all tables)...")
    crosswalk = build_crosswalk(
        args.patients_csv, args.our_source_column, args.their_source_column,
        args.our_schema, their_session_scope, args.their_schema,
    )
    print(f"  {len(crosswalk)} patient matches found.")

    all_summaries = []
    detail_sections: list[str] = []
    for config in TABLE_CONFIGS:
        print(f"Comparing {config['table']}...")
        lines, summary = compare_content_by_row(
            config["table"], config["natural_key"], config["fields"], config["exclude_fields"],
            crosswalk, args.our_schema, their_session_scope, args.their_schema,
        )
        all_summaries.append(summary)
        detail_sections.extend(lines)
        detail_sections.append("---")
        detail_sections.append("")

    report = build_executive_summary(all_summaries) + ["## Per-Table Detail", ""] + detail_sections
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report), encoding="utf-8")
    print(f"\nFull report written: {output_path}")


if __name__ == "__main__":
    main()
