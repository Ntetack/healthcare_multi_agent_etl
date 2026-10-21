"""
Captures a snapshot of omop_temp's current content into a CSV, for
comparing across runs over time (e.g. against an external reference
like OHDSI/ETL-Synthea, or against a previous version of this
pipeline). One row per (table, metric) - a "long" format, so adding a
new metric or a new table later never breaks the ability to diff old
snapshots against new ones.

Usage:
    python scripts/omop_temp_snapshot.py --label "my_system_2026-09-13"
    python scripts/omop_temp_snapshot.py --label "etl_synthea_reference" --schema some_other_schema
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.tools.database.db import session_scope as default_session_scope

# The 9 in-scope OMOP tables this project builds - see
# app/tools/mapping/omop_target_schema.py's IN_SCOPE_TABLES.
TABLES = [
    "person", "visit_occurrence", "condition_occurrence", "drug_exposure",
    "measurement", "procedure_occurrence", "observation", "death", "observation_period",
]

# Per table, the concept_id fields worth tracking a resolution rate for
# (how many rows have a real value vs NULL vs the "unresolved" sentinel
# 0) - the same distinction this project has relied on throughout this
# whole comparison exercise (e.g. visit_concept_id, unit_concept_id,
# cause_concept_id).
CONCEPT_FIELDS = {
    "person": ["gender_concept_id", "race_concept_id", "ethnicity_concept_id"],
    "visit_occurrence": ["visit_concept_id", "visit_type_concept_id"],
    "condition_occurrence": ["condition_concept_id", "condition_type_concept_id"],
    "drug_exposure": ["drug_concept_id", "drug_type_concept_id", "route_concept_id"],
    "measurement": ["measurement_concept_id", "unit_concept_id", "value_as_concept_id"],
    "procedure_occurrence": ["procedure_concept_id", "procedure_type_concept_id"],
    "observation": ["observation_concept_id", "value_as_concept_id"],
    "death": ["death_type_concept_id", "cause_concept_id"],
    "observation_period": ["period_type_concept_id"],
}

# Per table, the primary date field to report a min/max range for.
DATE_FIELDS = {
    "person": None,  # no single event date - birth_datetime exists but isn't a per-row event
    "visit_occurrence": "visit_start_date",
    "condition_occurrence": "condition_start_date",
    "drug_exposure": "drug_exposure_start_date",
    "measurement": "measurement_date",
    "procedure_occurrence": "procedure_date",
    "observation": "observation_date",
    "death": "death_date",
    "observation_period": "observation_period_start_date",
}


import contextlib


@contextlib.contextmanager
def _custom_session_scope(db_url: str):
    """A standalone connection to ANY database, independent of this
    project's own .env-configured connection (app.tools.database.db) -
    needed when the reference/comparison data (e.g. ETL-Synthea's own
    output) lives in a genuinely separate database, not just a
    different schema in the same one."""
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def table_exists(session, schema: str, table: str) -> bool:
    return session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = :schema AND table_name = :table"
        ),
        {"schema": schema, "table": table},
    ).first() is not None


def column_exists(session, schema: str, table: str, column: str) -> bool:
    return session.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table AND column_name = :column"
        ),
        {"schema": schema, "table": table, "column": column},
    ).first() is not None


def snapshot(schema: str, label: str, session_scope_fn=None) -> list[dict]:
    session_scope_fn = session_scope_fn or default_session_scope
    rows = []
    timestamp = datetime.now(timezone.utc).isoformat()

    with session_scope_fn() as session:
        for table in TABLES:
            if not table_exists(session, schema, table):
                rows.append({"label": label, "timestamp": timestamp, "table": table,
                             "metric": "table_missing", "value": "1"})
                continue

            total = session.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}")).scalar_one()
            rows.append({"label": label, "timestamp": timestamp, "table": table,
                         "metric": "row_count", "value": str(total)})

            if column_exists(session, schema, table, "person_id"):
                distinct_persons = session.execute(
                    text(f"SELECT COUNT(DISTINCT person_id) FROM {schema}.{table}")
                ).scalar_one()
                rows.append({"label": label, "timestamp": timestamp, "table": table,
                             "metric": "distinct_person_count", "value": str(distinct_persons)})

            date_field = DATE_FIELDS.get(table)
            if date_field and total > 0 and column_exists(session, schema, table, date_field):
                min_max = session.execute(
                    text(f"SELECT MIN({date_field}), MAX({date_field}) FROM {schema}.{table}")
                ).first()
                rows.append({"label": label, "timestamp": timestamp, "table": table,
                             "metric": f"{date_field}_min", "value": str(min_max[0])})
                rows.append({"label": label, "timestamp": timestamp, "table": table,
                             "metric": f"{date_field}_max", "value": str(min_max[1])})

            for field in CONCEPT_FIELDS.get(table, []):
                if not column_exists(session, schema, table, field) or total == 0:
                    continue
                resolved = session.execute(
                    text(f"SELECT COUNT(*) FROM {schema}.{table} WHERE {field} IS NOT NULL AND {field} != 0")
                ).scalar_one()
                nulls = session.execute(
                    text(f"SELECT COUNT(*) FROM {schema}.{table} WHERE {field} IS NULL")
                ).scalar_one()
                zeros = total - resolved - nulls
                rows.append({"label": label, "timestamp": timestamp, "table": table,
                             "metric": f"{field}_resolved_count", "value": str(resolved)})
                rows.append({"label": label, "timestamp": timestamp, "table": table,
                             "metric": f"{field}_null_count", "value": str(nulls)})
                rows.append({"label": label, "timestamp": timestamp, "table": table,
                             "metric": f"{field}_zero_count", "value": str(zeros)})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="Identifies this snapshot (e.g. 'my_system', 'etl_synthea_reference')")
    parser.add_argument("--schema", default="omop_temp", help="Schema to snapshot (default: omop_temp)")
    parser.add_argument("--output", default=None, help="Output CSV path (default: runs/snapshots/<label>_<timestamp>.csv)")
    parser.add_argument("--db-host", default=None, help="Host of a SEPARATE database (e.g. where ETL-Synthea's own output lives) - omit to use this project's own configured connection")
    parser.add_argument("--db-port", default="5432")
    parser.add_argument("--db-name", default=None)
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--db-password", default=None, help="Omit to be prompted, or read from DB_PASSWORD env var")
    args = parser.parse_args()

    session_scope_fn = None
    if args.db_host:
        password = args.db_password or os.environ.get("DB_PASSWORD", "")
        db_url = f"postgresql://{args.db_user}:{password}@{args.db_host}:{args.db_port}/{args.db_name}"
        session_scope_fn = lambda: _custom_session_scope(db_url)

    rows = snapshot(args.schema, args.label, session_scope_fn)

    output_path = Path(args.output) if args.output else (
        Path("runs/snapshots") / f"{args.label}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "timestamp", "table", "metric", "value"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Bilan écrit : {output_path} ({len(rows)} lignes)")


if __name__ == "__main__":
    main()
