"""
Verifies every concept_id declared in a batch's metadata.yaml
`type_concepts:` section against the REAL loaded vocabulary - confirms
each one (a) exists, and (b) is a STANDARD concept (required for any
*_concept_id field per OMOP convention). If a declared value fails
either check, suggests real, valid alternatives from the SAME
vocabulary domain instead of leaving you to guess.

Usage:
    python scripts/verify_type_concepts.py --metadata path/to/metadata.yaml
    python scripts/verify_type_concepts.py --concept-ids 32020 38000177 32817 32856
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml
from sqlalchemy import text

from app.tools.database.db import session_scope


def collect_declared_concept_ids(metadata_path: Path) -> dict[str, int]:
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    declared = {}
    for table, fields in (data.get("type_concepts") or {}).items():
        for field, concept_id in fields.items():
            declared[f"{table}.{field}"] = concept_id
    return declared


def verify_concept(session, concept_id: int) -> dict | None:
    row = session.execute(
        text(
            """
            SELECT concept_id, concept_name, vocabulary_id, domain_id,
                   standard_concept, invalid_reason
            FROM cdm_vocab.concept
            WHERE concept_id = :concept_id
            """
        ),
        {"concept_id": concept_id},
    ).mappings().first()
    return dict(row) if row else None


def suggest_alternatives(session, vocabulary_id: str, limit: int = 5) -> list[dict]:
    rows = session.execute(
        text(
            """
            SELECT concept_id, concept_name
            FROM cdm_vocab.concept
            WHERE vocabulary_id = :vocabulary_id
              AND standard_concept = 'S'
              AND (invalid_reason IS NULL OR invalid_reason = '')
            ORDER BY concept_id
            LIMIT :limit
            """
        ),
        {"vocabulary_id": vocabulary_id, "limit": limit},
    ).mappings().all()
    return [dict(r) for r in rows]


def check_vocabulary_loaded(session, vocabulary_id: str) -> int:
    return session.execute(
        text("SELECT COUNT(*) FROM cdm_vocab.concept WHERE vocabulary_id = :v"),
        {"v": vocabulary_id},
    ).scalar_one()


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--metadata", type=Path, help="Path to a batch's metadata.yaml")
    group.add_argument("--concept-ids", nargs="+", type=int, help="Concept IDs to check directly")
    args = parser.parse_args()

    if args.metadata:
        declared = collect_declared_concept_ids(args.metadata)
    else:
        declared = {f"concept_id_{i}": cid for i, cid in enumerate(args.concept_ids)}

    with session_scope() as session:
        # Sanity check first: is the "Type Concept" vocabulary even loaded?
        type_concept_count = check_vocabulary_loaded(session, "Type Concept")
        print(f"Concepts chargés pour vocabulary_id='Type Concept' : {type_concept_count}")
        if type_concept_count == 0:
            print("  /!\\ Le vocabulaire 'Type Concept' semble absent de votre chargement - "
                  "vérifiez qu'il était bien inclus dans votre export Athena.")
        print()

        for label, concept_id in declared.items():
            print(f"=== {label} = {concept_id} ===")
            concept = verify_concept(session, concept_id)
            if concept is None:
                print(f"  ❌ N'existe PAS dans cdm_vocab.concept.")
            elif concept["standard_concept"] != "S":
                print(f"  ❌ Existe mais N'EST PAS standard "
                      f"(standard_concept={concept['standard_concept']!r}, "
                      f"invalid_reason={concept['invalid_reason']!r})")
                print(f"     Nom : {concept['concept_name']} | Vocabulaire : {concept['vocabulary_id']}")
            else:
                print(f"  ✅ Valide et standard : {concept['concept_name']} "
                      f"(vocabulaire={concept['vocabulary_id']}, domaine={concept['domain_id']})")
                continue  # no need to suggest alternatives if already valid

            # Suggest real alternatives from the same vocabulary if we
            # know it (either from the failing row, or default to
            # "Type Concept" since that's what all our declared fields use).
            vocab_for_suggestions = concept["vocabulary_id"] if concept else "Type Concept"
            alternatives = suggest_alternatives(session, vocab_for_suggestions)
            if alternatives:
                print(f"  Alternatives valides dans '{vocab_for_suggestions}' :")
                for alt in alternatives:
                    print(f"    - {alt['concept_id']}: {alt['concept_name']}")
            print()


if __name__ == "__main__":
    main()
