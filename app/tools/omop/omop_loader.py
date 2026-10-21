"""
Loading tools used by the Loading Agent. Two phases:
  1. load_to_omop(): writes the transformed batch into OMOP_TEMP.
  2. promote_to_final(): after DQD PASS, appends OMOP_TEMP rows into
     OMOP_FINAL.

MVP simplification: append-only, no upsert/crosswalk. Re-running the same
source will duplicate rows in OMOP_FINAL if the same patient appears in
two batches - acceptable for the MVP scope; revisit if/when
cross-batch deduplication becomes a real requirement.
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from app.tools.database.db import (
    OMOP_FINAL_SCHEMA,
    OMOP_TEMP_SCHEMA,
    ensure_cdm_source_populated,
    session_scope,
    truncate_omop_temp,
)


def load_to_omop(table: str, df: pd.DataFrame) -> int:
    """Loads a transformed DataFrame into OMOP_TEMP.<table>. Assumes
    truncate_omop_temp() has already been called for this run."""
    with session_scope() as session:
        df.to_sql(table, con=session.get_bind(), schema=OMOP_TEMP_SCHEMA,
                   if_exists="append", index=False)
    return len(df)


def verify_load(table: str, expected_rows: int) -> bool:
    with session_scope() as session:
        actual = session.execute(
            text(f'SELECT COUNT(*) FROM "{OMOP_TEMP_SCHEMA}"."{table}"')
        ).scalar_one()
    return actual == expected_rows


def promote_to_final(table: str) -> dict[str, int]:
    """Appends all OMOP_TEMP.<table> rows into OMOP_FINAL.<table>.
    Plain INSERT ... SELECT, no dedup/upsert. Called after the DQD
    validation on OMOP_TEMP has passed."""
    with session_scope() as session:
        result = session.execute(
            text(
                f"""
                INSERT INTO "{OMOP_FINAL_SCHEMA}"."{table}"
                SELECT * FROM "{OMOP_TEMP_SCHEMA}"."{table}"
                """
            )
        )
    return {"rows_inserted": result.rowcount}


def reset_temp_for_new_run() -> None:
    truncate_omop_temp()
    ensure_cdm_source_populated()
