"""
Introspects the REAL, already-instantiated OMOP DDL (installed in step 1
via CommonDataModel's buildRelease()) to get the authoritative field list
and SQL type for any target table - never guessed, never hand-curated.
This is what makes the target-first resolution complete: the Mapping
Agent asks about every field a table actually has, not a hand-picked
subset.
"""
from __future__ import annotations

from sqlalchemy import text

from app.tools.database.db import OMOP_TEMP_SCHEMA, session_scope


def get_table_columns(table_name: str, schema: str = OMOP_TEMP_SCHEMA) -> list[dict]:
    """Returns [{"column_name":, "data_type":, "is_nullable":,
    "character_maximum_length":}, ...] for a table, ordered as declared
    in the DDL. Requires the OMOP DDL to already be instantiated (step 1)
    - raises if the table doesn't exist, rather than silently returning
    an empty list, since a typo'd table name should fail loudly."""
    with session_scope() as session:
        rows = session.execute(
            text(
                """
                SELECT column_name, data_type, is_nullable, character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = :schema AND table_name = :table_name
                ORDER BY ordinal_position
                """
            ),
            {"schema": schema, "table_name": table_name},
        ).mappings().all()

    if not rows:
        raise ValueError(
            f"Table '{schema}.{table_name}' has no columns (or doesn't exist). "
            f"Has the OMOP DDL been instantiated? See database/scripts/install_cdm.R."
        )
    return [dict(r) for r in rows]
