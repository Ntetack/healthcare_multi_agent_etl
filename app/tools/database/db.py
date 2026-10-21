"""
Central SQLAlchemy engine/session + schema-lifecycle helpers for
OMOP_TEMP / OMOP_FINAL (architecture doc v6, decision "validation par DQD
uniquement"): OMOP_TEMP is a persistent structure, truncated at the start
of each run.

Assumption made explicit (per architecture review): runs are executed
sequentially. Concurrent runs would race on the truncate step; if that
changes, move to a per-execution_id schema/suffix instead.
"""
from __future__ import annotations

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# Loaded here (not only in app/models/config.py) so that .env is picked up
# even when a script imports this module directly without going through
# the LLM config path (e.g. database/scripts/load_vocabulary.py).
load_dotenv()

OMOP_TEMP_SCHEMA = os.getenv("OMOP_TEMP_SCHEMA", "omop_temp")
OMOP_FINAL_SCHEMA = os.getenv("OMOP_FINAL_SCHEMA", "omop")


def get_engine() -> Engine:
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'omopdb')}"
    )
    return create_engine(url, future=True)


_SessionLocal = None


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), future=True)
    return _SessionLocal()


@contextmanager
def session_scope():
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


OMOP_TABLES = [
    "person", "visit_occurrence", "condition_occurrence",
    "measurement", "observation", "drug_exposure", "procedure_occurrence",
    "death", "observation_period",
]


def truncate_omop_temp() -> None:
    """Vides OMOP_TEMP au début de chaque run (isolation du batch pour le DQD).
    Called by the Loading Agent before writing the current batch."""
    with session_scope() as session:
        for table in OMOP_TABLES:
            session.execute(text(f'TRUNCATE TABLE "{OMOP_TEMP_SCHEMA}"."{table}" CASCADE'))


def ensure_cdm_source_populated() -> None:
    """DQD refuses to run at all ('Please populate the cdm_source table')
    unless CDM_SOURCE has at least one row - it's metadata ABOUT the CDM
    instance itself, not per-batch data, so it's intentionally NOT in
    OMOP_TABLES/truncated every run. Previously this was populated once,
    manually, outside the pipeline - fragile, since any DB reset or fresh
    install silently loses it with no automated recovery. Self-heals
    here instead: checked (and inserted if missing) at the start of
    every load_temp run.

    The INSERT is built by INTROSPECTING the real DDL (never a
    hand-picked column list, which previously missed
    cdm_version_concept_id and crashed on NOT NULL) - every required
    column gets a value, known ones from KNOWN_CDM_SOURCE_VALUES below,
    anything else defaulting per its real type (0 for concept_id/integer
    fields, matching the same "0 = unmapped" convention used everywhere
    else in Loading; CURRENT_DATE for date fields; '' otherwise).

    NOTE: cdm_version_concept_id defaults to 0 here because the correct
    OMOP concept representing 'CDM v5.4' has not been confirmed against
    this database's own loaded vocabulary (never invent an unverified
    concept_id - see this project's established convention). To set the
    real value once confirmed:
        SELECT concept_id, concept_name FROM cdm_vocab.concept
        WHERE vocabulary_id = 'CDM' AND concept_name ILIKE '%5.4%';
    then: UPDATE omop_temp.cdm_source SET cdm_version_concept_id = <id>;
    """
    from app.tools.mapping.omop_schema_introspection import get_table_columns

    known_values = {
        "cdm_source_name": "'Healthcare Multi-Agent ETL Framework'",
        "cdm_source_abbreviation": "'HMAE-ETL'",
        "cdm_holder": "'MST'",
        "source_release_date": "CURRENT_DATE",
        "cdm_release_date": "CURRENT_DATE",
        "cdm_version": "'v5.4'",
        "vocabulary_version": "'Athena export'",
    }

    with session_scope() as session:
        count = session.execute(
            text(f'SELECT COUNT(*) FROM "{OMOP_TEMP_SCHEMA}"."cdm_source"')
        ).scalar_one()
        if count > 0:
            return

        columns_info = get_table_columns("cdm_source", schema=OMOP_TEMP_SCHEMA)
        columns, values = [], []
        for c in columns_info:
            name = c["column_name"]
            is_nullable = (c.get("is_nullable") or "YES").upper() == "YES"
            if name in known_values:
                columns.append(name)
                values.append(known_values[name])
            elif not is_nullable:
                data_type = (c.get("data_type") or "").lower()
                if "concept_id" in name or "int" in data_type:
                    default = "0"
                elif "date" in data_type or "timestamp" in data_type:
                    default = "CURRENT_DATE"
                else:
                    default = "''"
                columns.append(name)
                values.append(default)

        col_list = ", ".join(f'"{c}"' for c in columns)
        val_list = ", ".join(values)
        session.execute(text(
            f'INSERT INTO "{OMOP_TEMP_SCHEMA}"."cdm_source" ({col_list}) VALUES ({val_list})'
        ))
