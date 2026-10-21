#!/usr/bin/env python3
"""Diagnostic (lecture seule) du mapping 'local' : pourquoi les identifiants
locaux (ITEMID) d'une source n'aboutissent pas a un concept routé.

Pour chaque jointure locale en cache (pipeline_meta.mapping_cache, kind
'local_vocab_join'), le script :
  1. rejoue la jointure ITEMID -> libellé sur les CSV sources ;
  2. rejoue la résolution EXACTE du pipeline (resolve_concept_exact_by_name,
     même fonction, mêmes vocabulaires) ;
  3. classe chaque libellé distinct dans UNE catégorie, avec son poids en lignes.

Aucune écriture en base, aucune modification du pipeline.

Usage (depuis la racine du projet, .env chargé) :
  python scripts/diagnose_local_labels.py --source-name <nom> \
      --data-dir <dossier des CSV MIMIC> --out-dir <dossier de sortie> \
      [--whatif LOINC SNOMED RxNorm]

--whatif : vocabulaires essayés quand la jointure n'en a AUCUN (resolved_standards
vide). Dans ce cas le pipeline ne cherche rien ; le script le signale
(searched_in_pipeline = non) et teste quand même, pour savoir ce qu'une
recherche exacte donnerait.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from sqlalchemy import text

from app.tools.database.db import session_scope
from app.tools.mapping.local_vocab_resolver import CACHE_KIND, resolve_concept_exact_by_name
from app.tools.mapping.omop_target_schema import DOMAIN_TO_TABLE
from app.tools.mapping.semantic.semantic_mapper import STANDARD_TO_VOCABULARY, is_placeholder

# --- catégories (une par libellé distinct) ---------------------------------
RESOLVED_ROUTED = "1_resolu_et_route"
RESOLVED_NO_TABLE = "2_resolu_domaine_hors_5_tables"
SOURCE_ONLY = "3_nom_trouve_sans_Maps_to_standard"
NORM_PUNCT = "4_recuperable_casse_ponctuation"
NORM_BRACKETS = "5_recuperable_sans_crochets_a_verifier"
SYNONYM = "6_recuperable_par_synonyme"
OTHER_VOCAB = "7_nom_exact_dans_un_autre_vocabulaire"
NO_MATCH = "8_aucun_candidat"
NO_LABEL = "0_libelle_absent_ou_placeholder"


def loose_punct(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def loose_brackets(s: str) -> str:
    return loose_punct(re.sub(r"\[[^\]]*\]", " ", s))


def _find_csv(data_dir: Path, table: str) -> Path | None:
    for p in data_dir.rglob("*.csv"):
        if p.stem.lower() == table.lower():
            return p
    return None


def _col(df_cols, name: str):
    lookup = {c.lower(): c for c in df_cols}
    return lookup.get(name.lower())


def list_specs(source_name: str) -> list[tuple[str, str, dict]]:
    with session_scope() as session:
        rows = session.execute(
            text(
                "SELECT table_name, field_name, resolution FROM pipeline_meta.mapping_cache "
                "WHERE source_name = :s AND cache_kind = :k ORDER BY table_name, field_name"
            ),
            {"s": source_name, "k": CACHE_KIND},
        ).mappings().all()
    return [(r["table_name"], r["field_name"], dict(r["resolution"])) for r in rows]


def distinct_keys_with_counts(path: Path, key: str) -> Counter:
    counts: Counter = Counter()
    header = pd.read_csv(path, nrows=0)
    real = _col(header.columns, key)
    if real is None:
        raise SystemExit(f"Colonne {key!r} introuvable dans {path.name}")
    for chunk in pd.read_csv(path, usecols=[real], dtype=str, chunksize=500_000):
        counts.update(chunk[real].dropna().value_counts().to_dict())
    return counts


def load_dictionary(path: Path, key: str, value: str) -> dict[str, str]:
    df = pd.read_csv(path, dtype=str)
    kc, vc = _col(df.columns, key), _col(df.columns, value)
    if kc is None or vc is None:
        raise SystemExit(f"Colonnes {key!r}/{value!r} introuvables dans {path.name}")
    df = df.drop_duplicates(subset=[kc], keep="first")  # même règle que apply_local_vocab_join
    # Un libellé vide (NaN) équivaut à "pas de libellé" : None, jamais un float.
    return {k: (None if pd.isna(v) else str(v)) for k, v in zip(df[kc], df[vc])}


def standard_concepts_loose(vocab_ids: list[str]) -> dict[str, list[dict]]:
    """Index {nom normalisé: [concepts]} des concepts Standard valides."""
    index: dict[str, list[dict]] = defaultdict(list)
    with session_scope() as session:
        rows = session.execute(
            text(
                "SELECT concept_id, concept_name, vocabulary_id, domain_id FROM cdm_vocab.concept "
                "WHERE vocabulary_id = ANY(:v) AND standard_concept = 'S' AND invalid_reason IS NULL"
            ),
            {"v": vocab_ids},
        ).mappings().all()
    for r in rows:
        index[loose_punct(r["concept_name"])].append(dict(r))
        index[("B", loose_brackets(r["concept_name"]))].append(dict(r))
    return index


def batch_other_vocab(names: list[str]) -> dict[str, dict]:
    if not names:
        return {}
    with session_scope() as session:
        rows = session.execute(
            text(
                "SELECT lower(concept_name) AS n, concept_id, vocabulary_id, domain_id FROM cdm_vocab.concept "
                "WHERE lower(concept_name) = ANY(:n) AND standard_concept = 'S' AND invalid_reason IS NULL"
            ),
            {"n": names},
        ).mappings().all()
    return {r["n"]: dict(r) for r in rows}


def batch_synonyms(names: list[str], vocab_ids: list[str]) -> dict[str, dict]:
    if not names:
        return {}
    try:
        with session_scope() as session:
            rows = session.execute(
                text(
                    "SELECT lower(cs.concept_synonym_name) AS n, c.concept_id, c.vocabulary_id, c.domain_id "
                    "FROM cdm_vocab.concept_synonym cs JOIN cdm_vocab.concept c ON c.concept_id = cs.concept_id "
                    "WHERE lower(cs.concept_synonym_name) = ANY(:n) AND c.vocabulary_id = ANY(:v) "
                    "AND c.standard_concept = 'S' AND c.invalid_reason IS NULL"
                ),
                {"n": names, "v": vocab_ids},
            ).mappings().all()
    except Exception as exc:  # table concept_synonym absente ou non chargée
        print(f"  (synonymes ignorés : {exc.__class__.__name__})")
        return {}
    return {r["n"]: dict(r) for r in rows}


def classify(labels: list[str], standards: list[str]) -> dict[str, tuple[str, str]]:
    """{label: (catégorie, détail)}"""
    vocab_ids = sorted({v for s in standards for v in STANDARD_TO_VOCABULARY.get(s, [])})
    out: dict[str, tuple[str, str]] = {}
    pending: list[str] = []
    for label in labels:
        if is_placeholder(label):
            out[label] = (NO_LABEL, "")
            continue
        res = resolve_concept_exact_by_name(label, standards)
        std, src = res["standard_concept"], res["source_concept"]
        if std is not None:
            domain = std.get("domain_id")
            detail = f"{std['concept_id']} {std.get('concept_name', '')} [{std.get('vocabulary_id', '')}/{domain}]"
            out[label] = (RESOLVED_ROUTED if domain in DOMAIN_TO_TABLE else RESOLVED_NO_TABLE, detail)
        elif src is not None:
            out[label] = (SOURCE_ONLY, f"{src['concept_id']} {src.get('concept_name', '')} [{src.get('vocabulary_id', '')}]")
        else:
            pending.append(label)

    if pending:
        index = standard_concepts_loose(vocab_ids)
        still: list[str] = []
        for label in pending:
            hit = index.get(loose_punct(label)) or None
            if hit:
                out[label] = (NORM_PUNCT, f"{hit[0]['concept_id']} {hit[0]['concept_name']} ({len(hit)} candidat(s))")
                continue
            hit = index.get(("B", loose_brackets(label))) or None
            if hit and loose_brackets(label):
                out[label] = (NORM_BRACKETS, f"{hit[0]['concept_id']} {hit[0]['concept_name']} ({len(hit)} candidat(s))")
                continue
            still.append(label)
        syn = batch_synonyms([l.lower() for l in still], vocab_ids)
        other = batch_other_vocab([l.lower() for l in still])
        for label in still:
            key = label.lower()
            if key in syn:
                out[label] = (SYNONYM, f"{syn[key]['concept_id']} [{syn[key]['vocabulary_id']}/{syn[key]['domain_id']}]")
            elif key in other:
                out[label] = (OTHER_VOCAB, f"{other[key]['concept_id']} [{other[key]['vocabulary_id']}/{other[key]['domain_id']}]")
            else:
                out[label] = (NO_MATCH, "")
    return out


def probe_with_suffix(labels: list[str], suffix: str, standards: list[str]) -> dict[str, tuple[str, str, str]]:
    """Pour chaque libellé : cherche '<libellé><suffixe>' par nom exact (même fonction que le pipeline).
    Retourne {libellé: (statut, détail, concept_code)}, statut parmi
    trouve_standard / trouve_sans_standard / absent."""
    out: dict[str, tuple[str, str, str]] = {}
    for label in labels:
        res = resolve_concept_exact_by_name(f"{label}{suffix}", standards)
        std, src = res["standard_concept"], res["source_concept"]
        if std is not None:
            out[label] = ("trouve_standard", f"{std['concept_id']} {std.get('concept_name', '')} "
                                             f"[{std.get('vocabulary_id', '')}/{std.get('domain_id', '')}]",
                          str(std.get("concept_code", "") or ""))
        elif src is not None:
            out[label] = ("trouve_sans_standard", f"{src['concept_id']} {src.get('concept_name', '')}",
                          str(src.get("concept_code", "") or ""))
        else:
            out[label] = ("absent", "", "")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-name", required=True)
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--whatif", nargs="*", default=["LOINC", "SNOMED", "RxNorm"])
    ap.add_argument("--probe-table", help="Table à sonder avec un suffixe (ex. MICROBIOLOGYEVENTS)")
    ap.add_argument("--probe-suffix", default=" [Susceptibility]",
                    help="Suffixe ajouté au libellé avant la recherche exacte (défaut : ' [Susceptibility]')")
    ap.add_argument("--probe-reference", type=Path,
                    help="CSV de référence (colonnes: libellé, code) pour comparer le code trouvé, "
                         "ex. extras/concept/atb_to_concept.csv (ab_name,concept_code)")
    ap.add_argument("--probe-vocab", nargs="*", default=["LOINC"], help="Vocabulaire(s) du sondage (défaut : LOINC)")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    specs = list_specs(args.source_name)
    if not specs:
        raise SystemExit(f"Aucune jointure locale en cache pour la source {args.source_name!r}")

    print(f"Cache lu pour la source {args.source_name!r} ({len(specs)} jointure(s)) :")
    for t, f, sp in specs:
        print(f"  {t}.{f}: type={sp.get('resolved_kind')} vocabulaires={sp.get('resolved_standards')} "
              f"colonne={sp.get('join_table')}.{sp.get('resolved_column')}")
    detail_rows: list[dict] = []
    summary: list[str] = ["# Diagnostic du mapping local", ""]
    for table, field, spec in specs:
        head = f"{table}.{field}"
        if spec.get("resolved_kind") != "text":
            summary += [f"## {head}", f"Jointure de type `{spec.get('resolved_kind')}` (code réel) : hors périmètre de ce diagnostic.", ""]
            continue
        fact_path = _find_csv(args.data_dir, table)
        dict_path = _find_csv(args.data_dir, spec["join_table"])
        if fact_path is None or dict_path is None:
            summary += [f"## {head}", f"CSV introuvable (fait : {fact_path}, dictionnaire : {dict_path}).", ""]
            continue

        counts = distinct_keys_with_counts(fact_path, spec["join_key_source"])
        dictionary = load_dictionary(dict_path, spec["join_key_target"], spec["resolved_column"])
        labels_by_key = {k: dictionary.get(k) for k in counts}
        no_join_rows = sum(c for k, c in counts.items() if labels_by_key[k] is None)

        searched = bool(spec.get("resolved_standards"))
        standards = spec.get("resolved_standards") or args.whatif
        distinct_labels = sorted({l for l in labels_by_key.values() if l is not None})
        print(f"{head}: {len(counts)} identifiants, {len(distinct_labels)} libellés, vocabulaires {standards}")
        verdict = classify(distinct_labels, standards)

        per_cat_distinct: Counter = Counter()
        per_cat_rows: Counter = Counter()
        for key, n in counts.items():
            label = labels_by_key[key]
            if label is None:
                continue
            cat, detail = verdict[label]
            per_cat_distinct[cat] += 1
            per_cat_rows[cat] += n
            detail_rows.append({
                "table": table, "champ": field, "identifiant": key, "libelle": label, "lignes": n,
                "categorie": cat, "detail": detail, "cherche_par_le_pipeline": "oui" if searched else "non",
            })

        total_ids, total_rows = sum(per_cat_distinct.values()), sum(per_cat_rows.values())
        summary += [
            f"## {head}", "",
            f"Jointure : {spec['join_table']}.{spec['resolved_column']} · vocabulaires : {', '.join(standards)} · "
            f"**cherché par le pipeline : {'oui' if searched else 'NON (resolved_standards vide, essai de comparaison)'}**",
            f"Identifiants distincts : {len(counts)} ; sans libellé (absent du dictionnaire ou libellé vide) : "
            f"{sum(1 for v in labels_by_key.values() if v is None)} ({no_join_rows} lignes).", "",
            "| Catégorie | Identifiants | % | Lignes | % |", "|---|---|---|---|---|",
        ]
        for cat in sorted(per_cat_distinct):
            summary.append(
                f"| {cat} | {per_cat_distinct[cat]} | {100 * per_cat_distinct[cat] / max(total_ids, 1):.1f} "
                f"| {per_cat_rows[cat]} | {100 * per_cat_rows[cat] / max(total_rows, 1):.1f} |"
            )
        summary.append("")

        if args.probe_table and args.probe_table.lower() == table.lower():
            probe = probe_with_suffix(distinct_labels, args.probe_suffix, args.probe_vocab)
            counts_p = Counter(v[0] for v in probe.values())
            summary += [
                f"### Sondage {table} : '<libellé>{args.probe_suffix}' dans {', '.join(args.probe_vocab)}", "",
                "| Statut | Libellés |", "|---|---|",
                *[f"| {k} | {v} |" for k, v in sorted(counts_p.items())], "",
            ]
            ref: dict[str, str] = {}
            if args.probe_reference:
                rdf = pd.read_csv(args.probe_reference, dtype=str)
                ref = {str(a).strip().upper(): str(b).strip() for a, b in zip(rdf.iloc[:, 0], rdf.iloc[:, 1])}
            rows_p = []
            for l, v in probe.items():
                r = ref.get(l.strip().upper(), "")
                accord = ("" if not ref else "sans_reference" if not r
                          else "non_trouve" if not v[2] else "oui" if r == v[2] else "non")
                rows_p.append({"libelle": l, "requete": f"{l}{args.probe_suffix}", "statut": v[0],
                               "detail": v[1], "concept_code": v[2], "code_reference": r, "accord_reference": accord})
            pd.DataFrame(rows_p).to_csv(args.out_dir / f"probe_{table}.csv", index=False, encoding="utf-8")
            if ref:
                acc = Counter(r["accord_reference"] for r in rows_p)
                summary += ["", "Accord avec la référence : " + ", ".join(f"{k}={v}" for k, v in sorted(acc.items())), ""]
            print(f"  sondage {table}: {dict(counts_p)}")

    pd.DataFrame(detail_rows).to_csv(args.out_dir / "local_labels_detail.csv", index=False, encoding="utf-8")
    (args.out_dir / "local_labels_summary.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"Écrit : {args.out_dir / 'local_labels_summary.md'} et local_labels_detail.csv")


if __name__ == "__main__":
    main()
