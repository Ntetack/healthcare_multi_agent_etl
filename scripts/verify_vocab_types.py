"""
Verifies that EVERY column across all 9 cdm_vocab vocabulary tables has
its correct real type (INTEGER/DATE/NUMERIC where expected) - not just
the ones a crash happened to reveal. Run this once after any
load_vocabulary.py run to confirm, rather than assume, that nothing is
silently stored as TEXT.

Usage:
    python scripts/verify_vocab_types.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.database.db import session_scope
from sqlalchemy import text

# The full, official expected type for every non-text column across all
# 9 vocabulary tables (per OMOP CDM v5.4 spec) - anything NOT listed
# here is expected to be text/varchar, which is correct as-is.
EXPECTED_TYPES = {
    "concept": {"concept_id": "integer", "valid_start_date": "date", "valid_end_date": "date"},
    "vocabulary": {"vocabulary_concept_id": "integer"},
    "domain": {"domain_concept_id": "integer"},
    "concept_class": {"concept_class_concept_id": "integer"},
    "relationship": {"relationship_concept_id": "integer"},
    "concept_relationship": {
        "concept_id_1": "integer", "concept_id_2": "integer",
        "valid_start_date": "date", "valid_end_date": "date",
    },
    "concept_synonym": {"concept_id": "integer", "language_concept_id": "integer"},
    "concept_ancestor": {
        "ancestor_concept_id": "integer", "descendant_concept_id": "integer",
        "min_levels_of_separation": "integer", "max_levels_of_separation": "integer",
    },
    "drug_strength": {
        "drug_concept_id": "integer", "ingredient_concept_id": "integer",
        "amount_value": "numeric", "amount_unit_concept_id": "integer",
        "numerator_value": "numeric", "numerator_unit_concept_id": "integer",
        "denominator_value": "numeric", "denominator_unit_concept_id": "integer",
        "box_size": "integer", "valid_start_date": "date", "valid_end_date": "date",
    },
}

# PostgreSQL reports several equivalent spellings for what we call
# "integer"/"numeric" above - normalize before comparing.
TYPE_ALIASES = {
    "integer": {"integer", "bigint", "smallint"},
    "numeric": {"numeric", "double precision", "real"},
    "date": {"date", "timestamp without time zone", "timestamp with time zone"},
}


def main():
    problems = []
    with session_scope() as session:
        for table, expected_columns in EXPECTED_TYPES.items():
            rows = session.execute(
                text(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'cdm_vocab' AND table_name = :table
                    """
                ),
                {"table": table},
            ).mappings().all()
            actual = {r["column_name"]: r["data_type"] for r in rows}

            if not actual:
                problems.append(f"{table}: table not found in cdm_vocab - was it loaded?")
                continue

            for column, expected in expected_columns.items():
                real_type = actual.get(column)
                if real_type is None:
                    problems.append(f"{table}.{column}: column not found at all")
                elif real_type not in TYPE_ALIASES[expected]:
                    problems.append(
                        f"{table}.{column}: expected {expected}, got '{real_type}' - "
                        f"still stored incorrectly, will cause the same class of crash"
                    )

    print(f"Vérifié : {sum(len(v) for v in EXPECTED_TYPES.values())} colonnes sur {len(EXPECTED_TYPES)} tables.\n")
    if not problems:
        print("✅ Tout est correctement typé - plus aucune colonne texte cachée.")
    else:
        print(f"❌ {len(problems)} problème(s) trouvé(s) :\n")
        for p in problems:
            print(f"  - {p}")


if __name__ == "__main__":
    main()
