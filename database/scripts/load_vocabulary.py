"""
Loads an OHDSI Athena vocabulary export into the cdm_vocab schema.

The vocabulary itself has no API - download is manual:
  1. Create a free account at https://athena.ohdsi.org
  2. Select the vocabularies you need (at minimum: ICD10CM, LOINC, SNOMED, RxNorm)
  3. Request/download the export -> you get a zip with tab-separated .csv files:
     CONCEPT.csv, CONCEPT_RELATIONSHIP.csv, VOCABULARY.csv, DOMAIN.csv,
     CONCEPT_CLASS.csv, RELATIONSHIP.csv, CONCEPT_SYNONYM.csv,
     DRUG_STRENGTH.csv, CONCEPT_ANCESTOR.csv
  4. Unzip it, then run:
       python database/scripts/load_vocabulary.py --input-dir /path/to/unzipped

Requires the omop_temp/omop DDL to already exist (install_cdm.R) since
vocabulary tables are part of the standard CDM DDL - here we just load the
data into a dedicated cdm_vocab schema shared by search_concept()/map_concept().

IMPORTANT (2nd fix): column types are now forced EXPLICITLY via
SQLAlchemy's `dtype=` parameter on to_sql() - not left to pandas' type
inference. Two earlier versions of this script both failed silently:
  1. Reading everything as dtype=str, so pandas' to_sql() auto-created
     every column as TEXT.
  2. Casting to pandas' nullable "Int64" extension dtype before
     writing, assuming to_sql() would infer SQL INTEGER from it - this
     is a known compatibility gap: pandas' nullable Int64 does not
     always map cleanly to SQL INTEGER via automatic inference, and
     silently fell back to TEXT again.
Explicit SQLAlchemy types leave nothing to infer, regardless of the
pandas/SQLAlchemy version combination in your environment. Run
scripts/verify_vocab_types.py after loading to confirm this held.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
from sqlalchemy import BigInteger, Date, Numeric, SmallInteger, Text, text
from sqlalchemy.types import TypeEngine

from app.tools.database.db import get_engine

LOAD_ORDER = [
    "VOCABULARY", "DOMAIN", "CONCEPT_CLASS", "RELATIONSHIP",
    "CONCEPT", "CONCEPT_RELATIONSHIP", "CONCEPT_SYNONYM",
    "CONCEPT_ANCESTOR", "DRUG_STRENGTH",
]

# Explicit SQLAlchemy type for EVERY non-text column, per table - passed
# directly to to_sql(dtype=...), so the actual CREATE TABLE statement
# uses these types verbatim. Any column not listed here is left as TEXT
# (correct for every genuinely textual OMOP vocabulary field: names,
# codes, ids that are themselves strings like vocabulary_id).
COLUMN_TYPES: dict[str, dict[str, TypeEngine]] = {
    "CONCEPT": {
        "concept_id": BigInteger(), "valid_start_date": Date(), "valid_end_date": Date(),
    },
    "VOCABULARY": {"vocabulary_concept_id": BigInteger()},
    "DOMAIN": {"domain_concept_id": BigInteger()},
    "CONCEPT_CLASS": {"concept_class_concept_id": BigInteger()},
    "RELATIONSHIP": {"relationship_concept_id": BigInteger()},
    "CONCEPT_RELATIONSHIP": {
        "concept_id_1": BigInteger(), "concept_id_2": BigInteger(),
        "valid_start_date": Date(), "valid_end_date": Date(),
    },
    "CONCEPT_SYNONYM": {"concept_id": BigInteger(), "language_concept_id": BigInteger()},
    "CONCEPT_ANCESTOR": {
        "ancestor_concept_id": BigInteger(), "descendant_concept_id": BigInteger(),
        "min_levels_of_separation": SmallInteger(), "max_levels_of_separation": SmallInteger(),
    },
    "DRUG_STRENGTH": {
        "drug_concept_id": BigInteger(), "ingredient_concept_id": BigInteger(),
        "amount_value": Numeric(), "amount_unit_concept_id": BigInteger(),
        "numerator_value": Numeric(), "numerator_unit_concept_id": BigInteger(),
        "denominator_value": Numeric(), "denominator_unit_concept_id": BigInteger(),
        "box_size": SmallInteger(), "valid_start_date": Date(), "valid_end_date": Date(),
    },
}

# Athena's CSV exports use YYYYMMDD (e.g. "20230115") for date columns.
DATE_COLUMNS = {
    "CONCEPT": ["valid_start_date", "valid_end_date"],
    "CONCEPT_RELATIONSHIP": ["valid_start_date", "valid_end_date"],
    "DRUG_STRENGTH": ["valid_start_date", "valid_end_date"],
}
NUMERIC_LIKE_COLUMNS = {
    table: [c for c, t in cols.items() if not isinstance(t, Date)]
    for table, cols in COLUMN_TYPES.items()
}


def _prepare_values(chunk: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Only pre-parses DATE strings (YYYYMMDD -> a real date object) so
    pandas can hand them to the driver correctly. Numeric-like columns
    are left as their original string/blank form here - the explicit
    SQLAlchemy dtype on to_sql() handles the actual SQL-side conversion,
    so we don't need (and must not rely on) a pandas-side numeric dtype
    for those."""
    for col in DATE_COLUMNS.get(table_name, []):
        if col in chunk.columns:
            chunk[col] = pd.to_datetime(chunk[col], format="%Y%m%d", errors="coerce").dt.date
    for col in NUMERIC_LIKE_COLUMNS.get(table_name, []):
        if col in chunk.columns:
            # Blank string -> real None, so the driver sends SQL NULL
            # instead of trying to cast an empty string to a number.
            chunk[col] = chunk[col].replace("", None)
    return chunk


def load_file(engine, input_dir: Path, table_name: str) -> int:
    csv_path = input_dir / f"{table_name}.csv"
    if not csv_path.exists():
        print(f"  skip {table_name}: file not found")
        return 0

    dtype_map = COLUMN_TYPES.get(table_name, {})
    n = 0
    for i, chunk in enumerate(pd.read_csv(csv_path, sep="\t", dtype=str, keep_default_na=False, chunksize=100_000)):
        chunk = chunk.replace("", None)
        chunk = _prepare_values(chunk, table_name)
        chunk.to_sql(
            table_name.lower(), con=engine, schema="cdm_vocab",
            if_exists="replace" if i == 0 else "append", index=False,
            dtype=dtype_map,  # <- forces real SQL types explicitly, no inference
        )
        n += len(chunk)
    return n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, help="Directory with the unzipped Athena export")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS cdm_vocab"))

    for table in LOAD_ORDER:
        print(f"Loading {table}...")
        n = load_file(engine, input_dir, table)
        print(f"  {n} rows loaded into cdm_vocab.{table.lower()}")


if __name__ == "__main__":
    main()
