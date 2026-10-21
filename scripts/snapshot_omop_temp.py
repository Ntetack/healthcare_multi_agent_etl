"""
Copies the nine tables of omop_temp into another schema, to keep the result of
one pipeline run before the next run empties omop_temp.

omop_temp only ever holds the current batch: it is emptied at the start of every
load. To compare the OMOP data built from two runs (for example the same
Synthea population read from its CSV export and from its FHIR export), take a
snapshot after each run, then compare the two snapshot schemas.

Usage (from the project root, right after a run):
    python scripts/snapshot_omop_temp.py --target-schema omop_csv
    python scripts/snapshot_omop_temp.py --target-schema omop_fhir --replace

Without --replace the script refuses to touch a schema that already exists.
With --replace it drops and recreates the target schema, which is why the
schemas used by the pipeline itself can never be a target.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from app.tools.database import db as database  # noqa: E402
from app.tools.database.db import OMOP_TABLES, OMOP_TEMP_SCHEMA, session_scope  # noqa: E402

# The final schema is configurable (OMOP_FINAL_SCHEMA, `omop` by default).
OMOP_FINAL_SCHEMA = getattr(database, "OMOP_FINAL_SCHEMA", "omop")

_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
_PIPELINE_SCHEMAS = {"public", "cdm_vocab", "staging", "pipeline_meta"}


def validate_target_schema(target_schema: str, source_schema: str, final_schema: str) -> str:
    """A target schema must be a plain lower-case identifier and never one of
    the schemas the pipeline relies on: with --replace it is dropped."""
    if not _IDENTIFIER.match(target_schema):
        raise ValueError(
            f"'{target_schema}' is not a valid schema name: use lower-case letters, digits and "
            f"underscores, starting with a letter or an underscore, at most 63 characters."
        )
    protected = _PIPELINE_SCHEMAS | {source_schema, final_schema}
    if target_schema in protected:
        raise ValueError(f"'{target_schema}' is used by the pipeline and cannot be a snapshot target.")
    return target_schema


def build_snapshot_statements(source_schema: str, target_schema: str, tables: list[str], replace: bool) -> list[str]:
    """The SQL of a snapshot, in order. The schema names have been validated
    by validate_target_schema; the table names come from the project."""
    statements: list[str] = []
    if replace:
        statements.append(f'DROP SCHEMA IF EXISTS "{target_schema}" CASCADE')
    statements.append(f'CREATE SCHEMA "{target_schema}"')
    for table in tables:
        statements.append(f'CREATE TABLE "{target_schema}"."{table}" AS TABLE "{source_schema}"."{table}"')
    return statements


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target-schema", required=True, help="Schema that will hold the copy, for example omop_csv")
    parser.add_argument("--replace", action="store_true", help="Drop and recreate the target schema if it exists")
    args = parser.parse_args()

    target = validate_target_schema(args.target_schema, OMOP_TEMP_SCHEMA, OMOP_FINAL_SCHEMA)
    statements = build_snapshot_statements(OMOP_TEMP_SCHEMA, target, list(OMOP_TABLES), args.replace)

    with session_scope() as session:
        for statement in statements:
            session.execute(text(statement))
        print(f"Snapshot of '{OMOP_TEMP_SCHEMA}' written to '{target}':")
        for table in OMOP_TABLES:
            count = session.execute(text(f'SELECT COUNT(*) FROM "{target}"."{table}"')).scalar_one()
            print(f"  {table}: {count} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
