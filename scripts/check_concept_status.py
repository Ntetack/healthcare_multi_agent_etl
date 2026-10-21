#!/usr/bin/env python3
"""Dit, pour chaque concept_id d'une colonne d'un CSV, s'il est standard ou non
dans le vocabulaire (cdm_vocab).

Exemple :
    python check_concept_status.py datetimeevents_to_concept.csv \
        --column observation_concept_id --dsn "postgresql://user:pass@localhost:5432/omopmimic"

Plusieurs colonnes a la fois : --column observation_concept_id --column observation_source_concept_id
Le DSN peut aussi venir de la variable d'environnement DATABASE_URL, ou de PGHOST/PGPORT/PGUSER/
PGPASSWORD/PGDATABASE.

Categories (une par concept_id) :
  zero                  concept_id = 0 (aucun concept)
  absent                le concept_id n'existe pas dans cdm_vocab.concept
  standard_valide       standard_concept = 'S' et invalid_reason vide
  classification        standard_concept = 'C' et invalid_reason vide (pas utilisable comme *_concept_id)
  non_standard_valide   standard_concept vide et invalid_reason vide (jamais standard, pas perime)
  deprecie_remplace     invalid_reason = 'D' ou 'U' (etait valide, ne l'est plus) ; le concept de
                        remplacement ("Maps to" vers un standard valide) est indique quand il existe

Sortie : un resume a l'ecran (concept_id distincts, et lignes du CSV) + un CSV de detail
(--out, par defaut <fichier>_statut_concepts.csv).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

CATEGORIES = [
    "standard_valide", "classification", "non_standard_valide", "deprecie_remplace", "absent", "zero",
]

CONCEPT_SQL = """
SELECT concept_id, concept_name, domain_id, vocabulary_id, concept_class_id,
       standard_concept, invalid_reason
FROM {schema}.concept
WHERE concept_id = ANY(%(ids)s)
"""

REPLACEMENT_SQL = """
SELECT r.concept_id_1 AS concept_id, t.concept_id AS remplacant_id, t.concept_name AS remplacant_nom
FROM {schema}.concept_relationship r
JOIN {schema}.concept t ON t.concept_id = r.concept_id_2
WHERE r.concept_id_1 = ANY(%(ids)s)
  AND r.relationship_id = 'Maps to'
  AND r.invalid_reason IS NULL
  AND t.standard_concept = 'S'
  AND t.invalid_reason IS NULL
  AND t.concept_id <> r.concept_id_1
"""


def classify(concept_id: int, row: dict | None) -> str:
    """Categorie d'un concept_id, a partir de sa ligne dans cdm_vocab.concept (None si absent)."""
    if concept_id == 0:
        return "zero"
    if row is None:
        return "absent"
    invalid = row.get("invalid_reason")
    if invalid in ("D", "U"):
        return "deprecie_remplace"
    standard = row.get("standard_concept")
    if standard == "S":
        return "standard_valide"
    if standard == "C":
        return "classification"
    return "non_standard_valide"


def read_ids(csv_path: Path, columns: list[str], sep: str | None) -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=sep, engine="python", dtype=str, keep_default_na=False)
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise SystemExit(f"Colonne(s) absente(s) de {csv_path.name} : {missing}. Colonnes disponibles : {list(df.columns)}")
    return df


def fetch_vocabulary(conn, ids: list[int], schema: str) -> tuple[dict[int, dict], dict[int, tuple[int, str]]]:
    concepts: dict[int, dict] = {}
    replacements: dict[int, tuple[int, str]] = {}
    with conn.cursor() as cur:
        cur.execute(CONCEPT_SQL.format(schema=schema), {"ids": ids})
        names = [d[0] for d in cur.description]
        for rec in cur.fetchall():
            row = dict(zip(names, rec))
            concepts[int(row["concept_id"])] = row
        cur.execute(REPLACEMENT_SQL.format(schema=schema), {"ids": ids})
        for concept_id, remplacant_id, remplacant_nom in cur.fetchall():
            replacements.setdefault(int(concept_id), (int(remplacant_id), remplacant_nom))
    return concepts, replacements


def analyse(df: pd.DataFrame, columns: list[str], concepts: dict[int, dict],
            replacements: dict[int, tuple[int, str]]) -> pd.DataFrame:
    """Un enregistrement par (colonne, concept_id) avec son nombre de lignes dans le CSV."""
    out = []
    for column in columns:
        values = df[column].str.strip()
        values = values[values != ""]
        counts = pd.to_numeric(values, errors="coerce").dropna().astype("int64").value_counts()
        for concept_id, n in counts.items():
            row = concepts.get(int(concept_id))
            repl = replacements.get(int(concept_id))
            out.append({
                "colonne": column,
                "concept_id": int(concept_id),
                "lignes_csv": int(n),
                "categorie": classify(int(concept_id), row),
                "concept_name": (row or {}).get("concept_name", ""),
                "domain_id": (row or {}).get("domain_id", ""),
                "vocabulary_id": (row or {}).get("vocabulary_id", ""),
                "concept_class_id": (row or {}).get("concept_class_id", ""),
                "standard_concept": (row or {}).get("standard_concept") or "",
                "invalid_reason": (row or {}).get("invalid_reason") or "",
                "remplacant_id": repl[0] if repl else "",
                "remplacant_nom": repl[1] if repl else "",
            })
    result = pd.DataFrame(out)
    if result.empty:
        return result
    order = {c: i for i, c in enumerate(CATEGORIES)}
    return result.sort_values(["colonne", "categorie", "lignes_csv"],
                              key=lambda s: s.map(order) if s.name == "categorie" else s,
                              ascending=[True, True, False]).reset_index(drop=True)


def summary(result: pd.DataFrame) -> str:
    lines = []
    for column, part in result.groupby("colonne"):
        total_ids, total_rows = len(part), int(part["lignes_csv"].sum())
        lines.append(f"\n== {column} : {total_ids} concept_id distincts, {total_rows} lignes du CSV")
        lines.append(f"{'categorie':<22}{'concepts':>10}{'lignes':>10}{'% lignes':>10}")
        for cat in CATEGORIES:
            sub = part[part["categorie"] == cat]
            if sub.empty:
                continue
            rows = int(sub["lignes_csv"].sum())
            lines.append(f"{cat:<22}{len(sub):>10}{rows:>10}{100 * rows / total_rows:>9.1f}%")
        dep = part[(part["categorie"] == "deprecie_remplace")]
        if not dep.empty:
            with_repl = int((dep["remplacant_id"] != "").sum())
            lines.append(f"  dont {with_repl}/{len(dep)} depreciés ont un remplacant standard valide (colonne remplacant_id)")
    return "\n".join(lines)


def connect(dsn: str | None):
    import psycopg2
    dsn = dsn or os.environ.get("DATABASE_URL")
    if dsn:
        return psycopg2.connect(dsn)
    return psycopg2.connect()  # lit PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path, help="CSV contenant les concept_id")
    ap.add_argument("--column", action="append", default=None,
                    help="colonne a analyser (repetable). Defaut : observation_concept_id")
    ap.add_argument("--sep", default=None, help="separateur du CSV (defaut : detecte)")
    ap.add_argument("--dsn", default=None, help="chaine de connexion PostgreSQL (sinon DATABASE_URL ou PG*)")
    ap.add_argument("--schema", default="cdm_vocab", help="schema du vocabulaire (defaut : cdm_vocab)")
    ap.add_argument("--out", type=Path, default=None, help="CSV de detail en sortie")
    args = ap.parse_args(argv)

    columns = args.column or ["observation_concept_id"]
    df = read_ids(args.csv, columns, args.sep)
    ids = sorted({int(v) for c in columns for v in pd.to_numeric(df[c].str.strip(), errors="coerce").dropna()})
    if not ids:
        raise SystemExit("Aucun concept_id numerique trouve dans les colonnes demandees.")

    conn = connect(args.dsn)
    try:
        concepts, replacements = fetch_vocabulary(conn, ids, args.schema)
    finally:
        conn.close()

    result = analyse(df, columns, concepts, replacements)
    out = args.out or args.csv.with_name(args.csv.stem + "_statut_concepts.csv")
    result.to_csv(out, index=False)
    print(summary(result))
    print(f"\nDetail ecrit dans : {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
