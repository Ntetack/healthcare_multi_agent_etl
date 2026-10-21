"""
Writes the staging area. Staging is a single, progressively enriched
table per (source, discovered table), kept as TEXT throughout structural
and semantic mapping. Enrichment (e.g. resolved concept_id columns from
semantic mapping) happens IN MEMORY on the DataFrame before the single
write - not via per-row UPDATE statements after the fact - so each
batch's staging table is written exactly once per run, consistent with
its `if_exists="replace"` semantics.
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import Text

from app.tools.database.db import session_scope


def write_initial_staging(source_name: str, df: pd.DataFrame, execution_id: str) -> str:
    """Creates/replaces staging.<source_name> with all columns explicitly
    typed TEXT (not left to pandas dtype inference), tagged with the
    execution_id for traceability. Called with the FULLY enriched
    DataFrame (including any resolved *_concept_id columns added by the
    Mapping Agent) - not the raw one.

    Full-row duplicates (every column identical, including any resolved
    columns already attached) are dropped before insertion - a source
    export can legitimately contain the exact same row twice, and
    staging is meant to hold one enriched copy per real record, not an
    accidental repeat."""
    table_name = f"staging_{source_name}"
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    df["execution_id"] = execution_id
    with session_scope() as session:
        df.to_sql(
            table_name,
            con=session.get_bind(),
            schema="staging",
            if_exists="replace",
            index=False,
            dtype={col: Text() for col in df.columns},
        )
    if dropped > 0:
        print(f"staging.{table_name}: dropped {dropped} full-row duplicate(s) before insertion")
    return table_name
