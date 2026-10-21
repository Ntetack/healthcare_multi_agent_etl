"""
Full comparison for the FHIR route: agents' OMOP (built from FHIR bundles)
against an external reference (ETL-Synthea), same 9 tables, same report format
as run_full_comparison.py.

Differences with run_full_comparison.py
---------------------------------------
1. NO patients.csv. FHIR has none. The patient crosswalk is built straight from
   the two person tables, on person_source_value. If the two systems write the
   patient identifier differently, pass --bridge-csv (two columns, see below).
2. Date keys. FHIR carries the real time of day (2010-08-18 03:31:44) where the
   Synthea CSV export is at midnight, so a key that contains a *_datetime can
   never match. Every *_datetime field of a key is replaced by its *_date
   counterpart (--key-granularity datetime keeps the original keys). The
   datetime stays a content field: it is compared with the "datetime" rule
   (the day if either side has no time of day, the second otherwise).
3. A diagnostics block at the top of the report: how many patients were bridged,
   and the values of the most frequent keys, so a failed bridge is visible at once
   instead of showing up as 0 % everywhere.

TABLE_CONFIGS is imported from run_full_comparison.py: one place to edit the
fields, for both routes.

Usage:
    python scripts/run_full_comparison_fhir.py \
        --b1-schema omop_temp \
        --b0-db-host localhost --b0-db-name omop_cdm \
        --b0-schema cdm_synthea10 --b0-db-user synthea_user \
        --b0-db-password changeme \
        --output reports/synthea_fhir/full_comparison_fhir.md

    # if person_source_value differs between the two systems:
    #   --bridge-csv bridge.csv   (columns: b1,b0)
"""
from __future__ import annotations

import argparse
import copy
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compare_content import compare_table, _remote_session_scope
from run_full_comparison import (
    TABLE_CONFIGS, build_executive_summary, field_agreement_section, write_field_details,
)
from app.tools.database.db import session_scope as b1_session_scope


def to_date_keys(configs: list[dict]) -> list[dict]:
    """Copy of the configs where every *_datetime field of a key becomes *_date
    (drug_exposure_start_datetime -> drug_exposure_start_date, procedure_datetime
    -> procedure_date). Fields that are already dates are left alone, and a
    duplicate produced by the swap is dropped."""
    result = []
    for config in configs:
        config = copy.deepcopy(config)
        key: list[str] = []
        for field in config["key"]:
            if field.endswith("_datetime"):
                field = field[: -len("_datetime")] + "_date"
            if field not in key:
                key.append(field)
        config["key"] = key
        result.append(config)
    return result


def join_on_source_value(b1_person: pd.DataFrame, b0_person: pd.DataFrame) -> pd.DataFrame:
    """b1_person_id <-> b0_person_id, matching person_source_value exactly
    (stripped, case-sensitive: a UUID is a UUID)."""
    b1_persons = b1_person.assign(_key=b1_person["person_source_value"].astype(str).str.strip())
    b0_persons = b0_person.assign(_key=b0_person["person_source_value"].astype(str).str.strip())
    merged = b1_persons.merge(b0_persons, on="_key", how="inner", suffixes=("_b1", "_b0"))
    return merged.rename(columns={"person_id_b1": "b1_person_id", "person_id_b0": "b0_person_id"})[
        ["b1_person_id", "b0_person_id"]
    ].drop_duplicates()


def join_on_bridge(b1_person: pd.DataFrame, b0_person: pd.DataFrame, bridge: pd.DataFrame) -> pd.DataFrame:
    """Same, through a two-column table (b1, b0) for the case where the
    two systems write the patient identifier differently."""
    bridge = bridge.rename(columns={bridge.columns[0]: "_b1", bridge.columns[1]: "_b0"}).astype(str)
    crosswalk = bridge.merge(b1_person.astype({"person_source_value": str}),
                             left_on="_b1", right_on="person_source_value", how="inner"
                             ).rename(columns={"person_id": "b1_person_id"})[["_b0", "b1_person_id"]]
    crosswalk = crosswalk.merge(b0_person.astype({"person_source_value": str}),
                                left_on="_b0", right_on="person_source_value", how="inner"
                                ).rename(columns={"person_id": "b0_person_id"})
    return crosswalk[["b1_person_id", "b0_person_id"]].drop_duplicates()


def read_persons(b1_schema: str, b0_session_scope, b0_schema: str):
    with b1_session_scope() as session:
        b1_persons = pd.read_sql(text(f"SELECT person_id, person_source_value FROM {b1_schema}.person"),
                           session.connection())
    with b0_session_scope() as session:
        b0_persons = pd.read_sql(text(f"SELECT person_id, person_source_value FROM {b0_schema}.person"),
                             session.connection())
    return b1_persons, b0_persons


def diagnostics(b1_persons: pd.DataFrame, b0_persons: pd.DataFrame, crosswalk: pd.DataFrame, mode: str) -> list[str]:
    lines = ["## Diagnostics of the run", ""]
    lines.append(f"- Patient bridge: {mode}")
    lines.append(f"- Patients: {len(b1_persons)} in B1, {len(b0_persons)} in B0, {len(crosswalk)} bridged")
    if len(crosswalk) < min(len(b1_persons), len(b0_persons)):
        lines.append(f"- WARNING: {min(len(b1_persons), len(b0_persons)) - len(crosswalk)} patients could not be bridged. "
                     "Every table below is restricted to the bridged patients.")
        lines.append(f"  examples B1: {b1_persons['person_source_value'].astype(str).head(3).tolist()}")
        lines.append(f"  examples B0: {b0_persons['person_source_value'].astype(str).head(3).tolist()}")
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
    parser.add_argument("--bridge-csv", default=None,
                        help="optional CSV with two columns (b1,b0) when person_source_value differs")
    parser.add_argument("--key-granularity", choices=["date", "datetime"], default="date")
    parser.add_argument("--output", required=True)
    parser.add_argument("--listed-fields-only", action="store_true",
                        help="compare only the fields listed in TABLE_CONFIGS (default: every field, see run_full_comparison.py)")
    args = parser.parse_args()

    password = args.b0_db_password or os.environ.get("DB_PASSWORD", "")
    b0_url = f"postgresql://{args.b0_db_user}:{password}@{args.b0_db_host}:{args.b0_db_port}/{args.b0_db_name}"
    b0_session_scope = lambda: _remote_session_scope(b0_url)

    print("Building the patient crosswalk from the two person tables...")
    b1_persons, b0_persons = read_persons(args.b1_schema, b0_session_scope, args.b0_schema)
    if args.bridge_csv:
        crosswalk = join_on_bridge(b1_persons, b0_persons, pd.read_csv(args.bridge_csv, dtype=str))
        mode = f"bridge file {args.bridge_csv}"
    else:
        crosswalk = join_on_source_value(b1_persons, b0_persons)
        mode = "person_source_value identical on both sides"
    print(f"  {len(crosswalk)} patient matches found.")
    if crosswalk.empty:
        sys.exit("No patient could be bridged: compare person_source_value in the two schemas "
                 f"(B1: {b1_persons['person_source_value'].head(3).tolist()}, "
                 f"B0: {b0_persons['person_source_value'].head(3).tolist()}) "
                 "and pass --bridge-csv if they differ.")

    configs = to_date_keys(TABLE_CONFIGS) if args.key_granularity == "date" else TABLE_CONFIGS

    all_summaries = []
    detail_sections: list[str] = []
    for config in configs:
        config = {**config, "all_fields": not args.listed_fields_only}
        print(f"Comparing {config['table']} (key: {config['key']})...")
        lines, summary = compare_table(config, crosswalk, args.b1_schema, b0_session_scope, args.b0_schema)
        all_summaries.append(summary)
        detail_sections.extend(lines)
        detail_sections.extend(["---", ""])

    head = build_executive_summary(all_summaries)
    report = head + field_agreement_section(all_summaries) + diagnostics(b1_persons, b0_persons, crosswalk, mode) + \
        [f"Key granularity: {args.key_granularity}", ""] + ["## Per-Table Detail", ""] + detail_sections
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report), encoding="utf-8")
    fields_path = output_path.with_name(output_path.stem + "_fields.csv")
    n = write_field_details(all_summaries, fields_path)
    print(f"\nFull report written: {output_path}\nField detail ({n} rows): {fields_path}")


if __name__ == "__main__":
    main()
