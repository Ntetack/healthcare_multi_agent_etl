"""
Systematically verifies EVERY entry in STANDARD_TO_VOCABULARY against
the real, loaded vocabulary - catching the exact class of bug found
twice already in this project (declaring an OMOP DOMAIN name where a
real vocabulary_id was needed, e.g. "Condition"/"Drug" for mechanism 1,
then "Unit" instead of "UCUM"). Never guesses: reports what's actually
in cdm_vocab.vocabulary and cdm_vocab.domain for each declared name.

Usage:
    python scripts/verify_standard_to_vocabulary.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.tools.database.db import session_scope
from app.tools.mapping.semantic.semantic_mapper import STANDARD_TO_VOCABULARY


def main():
    problems = []
    with session_scope() as session:
        for declared_name, vocab_ids in STANDARD_TO_VOCABULARY.items():
            if not vocab_ids:
                print(f"⚠️  {declared_name:20s} -> aucun vocabulaire associé (liste vide), ignoré volontairement")
                continue

            for vocab_id in vocab_ids:
                # 1. Does this actually exist as a real vocabulary_id?
                vocab_row = session.execute(
                    text("SELECT vocabulary_name FROM cdm_vocab.vocabulary WHERE vocabulary_id = :v"),
                    {"v": vocab_id},
                ).mappings().first()

                concept_count = session.execute(
                    text("SELECT COUNT(*) FROM cdm_vocab.concept WHERE vocabulary_id = :v"),
                    {"v": vocab_id},
                ).scalar_one()

                # 2. Is it ALSO (or instead) a domain name - the exact
                # confusion that caused real bugs twice already?
                domain_row = session.execute(
                    text("SELECT domain_name FROM cdm_vocab.domain WHERE domain_id = :v"),
                    {"v": vocab_id},
                ).mappings().first()

                if vocab_row is None and domain_row is not None:
                    problems.append(
                        f"❌ {declared_name!r} -> {vocab_id!r} n'existe PAS comme vocabulaire, "
                        f"mais EXISTE comme domaine ('{domain_row['domain_name']}') - probable confusion "
                        f"domaine/vocabulaire, comme pour 'Unit'/'Condition'/'Drug'."
                    )
                elif vocab_row is None:
                    problems.append(
                        f"❌ {declared_name!r} -> {vocab_id!r} n'existe ni comme vocabulaire ni comme "
                        f"domaine dans votre base chargée - vérifiez l'orthographe ou si ce vocabulaire "
                        f"a bien été inclus dans votre export Athena."
                    )
                elif concept_count == 0:
                    problems.append(
                        f"⚠️  {declared_name!r} -> {vocab_id!r} existe comme vocabulaire déclaré, mais "
                        f"0 concept chargé - probablement absent de votre export Athena."
                    )
                else:
                    print(f"✅ {declared_name:20s} -> {vocab_id:20s} ({concept_count} concepts, "
                          f"'{vocab_row['vocabulary_name']}')")

    print()
    if not problems:
        print("✅ Toutes les entrées de STANDARD_TO_VOCABULARY correspondent à de vrais vocabulaires chargés.")
    else:
        print(f"❌ {len(problems)} problème(s) trouvé(s) :\n")
        for p in problems:
            print(f"  {p}")


if __name__ == "__main__":
    main()
