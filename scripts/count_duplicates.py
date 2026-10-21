"""
Compte les lignes uniques et dupliquées dans un ensemble de fichiers CSV.

Usage :
    python count_duplicates.py fichier1.csv fichier2.csv ...
    python count_duplicates.py dossier/*.csv
    python count_duplicates.py --dir data/raw/hospital_a/batch007/
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def analyze_csv(path: Path, subset: list[str] | None = None,
                ignore_cols: list[str] | None = None) -> dict:
    """Analyse un CSV et retourne les stats de duplication."""
    df = pd.read_csv(path, dtype=str)

    # Colonnes à ignorer (ex: un id interne qui rend chaque ligne unique)
    if ignore_cols:
        df = df.drop(columns=[c for c in ignore_cols if c in df.columns])

    cols = subset if subset else list(df.columns)
    cols = [c for c in cols if c in df.columns]

    total = len(df)
    uniques = df.drop_duplicates(subset=cols).shape[0]
    dupliquees = total - uniques

    # Nombre de lignes "en trop" (les occurrences au-delà de la 1ère)
    extra = df.duplicated(subset=cols, keep="first").sum()

    # Nombre de groupes de clés en doublon
    groupes = df[df.duplicated(subset=cols, keep=False)] \
        .groupby(cols, dropna=False).ngroups

    return {
        "fichier": path.name,
        "lignes_total": total,
        "lignes_uniques": uniques,
        "lignes_dupliquees": dupliquees,
        "lignes_en_trop": int(extra),
        "groupes_doublons": groupes,
        "colonnes_cles": cols,
        "dataframe": df,
    }


def find_csv_files(paths: list[str], directory: str | None) -> list[Path]:
    files: list[Path] = []
    if directory:
        files += sorted(Path(directory).glob("*.csv"))
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            files += sorted(pp.glob("*.csv"))
        elif pp.suffix.lower() == ".csv":
            files.append(pp)
    # dédoublonne en gardant l'ordre
    seen = set()
    out = []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def main():
    parser = argparse.ArgumentParser(description="Compte lignes uniques/dupliquées dans des CSV")
    parser.add_argument("files", nargs="*", help="Fichiers CSV ou dossiers")
    parser.add_argument("--dir", default=None, help="Dossier contenant les CSV")
    parser.add_argument("--subset", default=None,
                        help="Colonnes formant la clé de duplication (séparées par virgule)")
    parser.add_argument("--ignore-cols", default="",
                        help="Colonnes à ignorer (ex: un id qui rend tout unique)")
    parser.add_argument("--show-examples", type=int, default=3,
                        help="Nombre d'exemples de doublons à afficher par fichier")
    args = parser.parse_args()

    files = find_csv_files(args.files, args.dir)
    if not files:
        print("Aucun fichier CSV trouvé.", file=sys.stderr)
        sys.exit(1)

    subset = [c.strip() for c in args.subset.split(",")] if args.subset else None
    ignore = [c.strip() for c in args.ignore_cols.split(",") if c.strip()]

    print(f"{len(files)} fichier(s) à analyser\n")

    results = []
    for f in files:
        try:
            r = analyze_csv(f, subset=subset, ignore_cols=ignore)
            results.append(r)
        except Exception as e:
            print(f"❌ {f.name} : {e}")
            continue

    # ── Résumé global ──
    print("=" * 78)
    print(f"{'Fichier':<40} {'Total':>8} {'Uniques':>9} {'Dupliquées':>11} {'En trop':>8}")
    print("=" * 78)
    for r in results:
        print(f"{r['fichier']:<40} {r['lignes_total']:>8} "
              f"{r['lignes_uniques']:>9} {r['lignes_dupliquees']:>11} "
              f"{r['lignes_en_trop']:>8}")
    print("=" * 78)

    tot = sum(r["lignes_total"] for r in results)
    uniq = sum(r["lignes_uniques"] for r in results)
    dup = sum(r["lignes_dupliquees"] for r in results)
    extra = sum(r["lignes_en_trop"] for r in results)
    print(f"{'TOTAL':<40} {tot:>8} {uniq:>9} {dup:>11} {extra:>8}")

    # ── Exemples de doublons ──
    if args.show_examples > 0:
        print("\n" + "─" * 78)
        print("Exemples de lignes en doublon :\n")
        for r in results:
            if r["lignes_en_trop"] == 0:
                continue
            df = r["dataframe"]
            cols = r["colonnes_cles"]
            dupes = df[df.duplicated(subset=cols, keep=False)] \
                .sort_values(by=cols)
            print(f"### {r['fichier']} — clé : {cols}")
            print(dupes.head(args.show_examples).to_string(index=False))
            print()


if __name__ == "__main__":
    main()