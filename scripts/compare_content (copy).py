"""
Compares ACTUAL CONTENT (not just row counts) between two OMOP
databases - typically this project's own restricted 9-table pipeline
vs a fuller reference like ETL-Synthea, which isn't restricted to a
9-table scope and therefore populates more tables/fields.

Two independent comparisons - use either or both:

  1. SCHEMA COVERAGE (--mode coverage): for each of our 9 tables, which
     fields does the reference populate that we don't (and vice
     versa), and for fields both populate, their respective null
     rates. No join needed - purely structural.

  2. ROW-LEVEL CONTENT (--mode content): for a given table, compares
     actual field values person-by-person. Since person_id is an
     independently auto-generated surrogate key in EACH system (never
     directly comparable), a CROSSWALK is built first from the
     ORIGINAL source file (e.g. patients.csv), which has every raw
     identifier BOTH systems might have chosen as person_source_value
     (Id, SSN, etc.) - this is the only reliable bridge, regardless of
     which convention either system happened to use.

Usage:
    # Schema coverage - no crosswalk needed
    python scripts/compare_content.py --mode coverage \\
        --their-db-host localhost --their-db-name etl_synthea_db --their-schema public

    # Content comparison - needs the original patients.csv as the bridge
    python scripts/compare_content.py --mode content --table condition_occurrence \\
        --patients-csv data/raw/hospital_a/batch054/patients.csv \\
        --our-source-column Id --their-source-column Id \\
        --their-db-host localhost --their-db-name etl_synthea_db --their-schema public
"""
from __future__ import annotations

import argparse
import contextlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.tools.database.db import session_scope as our_session_scope

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


def compare_coverage(our_schema: str, their_session_scope, their_schema: str) -> list[str]:
    lines = ["# Comparaison de portée (champs/tables)", ""]
    with our_session_scope() as our_session, their_session_scope() as their_session:
        for table in OUR_TABLES:
            our_cols = _get_columns(our_session, our_schema, table)
            their_cols = _get_columns(their_session, their_schema, table)

            if not their_cols:
                lines.append(f"## {table} — absente chez la référence (ou nom différent)\n")
                continue
            if not our_cols:
                lines.append(f"## {table} — absente chez nous\n")
                continue

            only_theirs = their_cols - our_cols
            only_ours = our_cols - their_cols
            common = our_cols & their_cols

            lines.append(f"## {table}")
            if only_theirs:
                lines.append(f"  Champs remplis par la référence, absents chez nous : {sorted(only_theirs)}")
            if only_ours:
                lines.append(f"  Champs présents chez nous, absents chez la référence : {sorted(only_ours)}")

            lines.append("  Taux de NULL sur les champs communs :")
            for col in sorted(common):
                our_rate = _null_rate(our_session, our_schema, table, col)
                their_rate = _null_rate(their_session, their_schema, table, col)
                if our_rate is None or their_rate is None:
                    continue
                marker = "  ⚠️" if abs(our_rate - their_rate) > 20 else "  "
                lines.append(f"{marker} {col}: nous={our_rate:.0f}% NULL, référence={their_rate:.0f}% NULL")
            lines.append("")
    return lines


def build_crosswalk(
    patients_csv: str, our_source_column: str, their_source_column: str,
    our_schema: str, their_session_scope, their_schema: str,
) -> pd.DataFrame:
    """Builds our_person_id <-> their_person_id via the ORIGINAL
    patients.csv - the only reliable bridge, since each system's
    person_source_value may follow a DIFFERENT convention (UUID, SSN,
    ...) that the other system never sees."""
    patients = pd.read_csv(patients_csv, dtype=str)

    with our_session_scope() as our_session:
        our_person = pd.read_sql(
            text(f"SELECT person_id, person_source_value FROM {our_schema}.person"), our_session.connection()
        )
    with their_session_scope() as their_session:
        their_person = pd.read_sql(
            text(f"SELECT person_id, person_source_value FROM {their_schema}.person"), their_session.connection()
        )

    # Built with explicitly distinct names, even when
    # our_source_column and their_source_column happen to be the SAME
    # real column (e.g. both "Id") - selecting the same column twice
    # via patients[[col, col]] produces a DataFrame with duplicate
    # column labels, which breaks pandas' merge() with a confusing
    # "column label is not unique" error.
    bridge = patients[[our_source_column, their_source_column]].copy()
    bridge.columns = ["_bridge_our", "_bridge_their"]
    bridge = bridge.drop_duplicates()
    crosswalk = bridge.merge(
        our_person, left_on="_bridge_our", right_on="person_source_value", how="inner"
    ).rename(columns={"person_id": "our_person_id"})
    crosswalk = crosswalk.merge(
        their_person, left_on="_bridge_their", right_on="person_source_value", how="inner",
        suffixes=("_our", "_their"),
    ).rename(columns={"person_id": "their_person_id"})

    return crosswalk[["our_person_id", "their_person_id"]]


def compare_content(
    table: str, fields: list[str], crosswalk: pd.DataFrame,
    our_schema: str, their_session_scope, their_schema: str,
) -> list[str]:
    lines = [f"# Comparaison de contenu — {table}", ""]
    lines.append(f"Correspondances patient trouvées : {len(crosswalk)}")
    lines.append("")

    field_list = ", ".join(fields)
    with our_session_scope() as our_session:
        our_rows = pd.read_sql(
            text(f"SELECT person_id, {field_list} FROM {our_schema}.{table}"), our_session.connection()
        )
    with their_session_scope() as their_session:
        their_rows = pd.read_sql(
            text(f"SELECT person_id, {field_list} FROM {their_schema}.{table}"), their_session.connection()
        )

    our_rows = our_rows.merge(crosswalk, left_on="person_id", right_on="our_person_id")
    their_rows = their_rows.merge(crosswalk, left_on="person_id", right_on="their_person_id")

    for field in fields:
        our_values = set(our_rows[field].dropna().astype(str))
        their_values = set(their_rows[field].dropna().astype(str))
        common = our_values & their_values
        only_ours = our_values - their_values
        only_theirs = their_values - our_values
        lines.append(f"## {field}")
        lines.append(f"  Valeurs communes : {len(common)}")
        lines.append(f"  Valeurs UNIQUEMENT chez nous : {len(only_ours)} (ex: {list(only_ours)[:5]})")
        lines.append(f"  Valeurs UNIQUEMENT chez la référence : {len(only_theirs)} (ex: {list(only_theirs)[:5]})")
        lines.append("")
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["coverage", "content"], required=True)
    parser.add_argument("--our-schema", default="omop_temp")
    parser.add_argument("--their-db-host", required=True)
    parser.add_argument("--their-db-port", default="5432")
    parser.add_argument("--their-db-name", required=True)
    parser.add_argument("--their-db-user", required=True)
    parser.add_argument("--their-db-password", default=None)
    parser.add_argument("--their-schema", default="public")
    parser.add_argument("--table", default=None, help="Required for --mode content")
    parser.add_argument("--fields", default=None, help="Comma-separated fields to compare, required for --mode content")
    parser.add_argument("--patients-csv", default=None, help="Required for --mode content")
    parser.add_argument("--our-source-column", default="Id", help="Column in patients.csv matching OUR person_source_value")
    parser.add_argument("--their-source-column", default="Id", help="Column in patients.csv matching THEIR person_source_value")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    password = args.their_db_password or os.environ.get("DB_PASSWORD", "")
    their_url = f"postgresql://{args.their_db_user}:{password}@{args.their_db_host}:{args.their_db_port}/{args.their_db_name}"
    their_session_scope = lambda: _remote_session_scope(their_url)

    if args.mode == "coverage":
        lines = compare_coverage(args.our_schema, their_session_scope, args.their_schema)
    else:
        if not (args.table and args.fields and args.patients_csv):
            parser.error("--mode content requires --table, --fields, and --patients-csv")
        crosswalk = build_crosswalk(
            args.patients_csv, args.our_source_column, args.their_source_column,
            args.our_schema, their_session_scope, args.their_schema,
        )
        lines = compare_content(
            args.table, args.fields.split(","), crosswalk,
            args.our_schema, their_session_scope, args.their_schema,
        )

    report = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Rapport écrit : {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()