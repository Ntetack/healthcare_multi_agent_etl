#!/usr/bin/env python3
"""Count the data rows of every CSV file in a folder.

Usage:
    python count_csv_rows.py FOLDER [--recursive] [--csv out.csv] [--latex out.tex]

Rows are counted with the csv module, so a line break inside a quoted value
is not counted as a new row. The header line is not counted.
Files ending in .csv or .csv.gz are read.
"""
import argparse
import csv
import gzip
import sys
from pathlib import Path

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def open_text(path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="")
    return open(path, "r", encoding="utf-8", errors="replace", newline="")


def count_rows(path):
    with open_text(path) as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return 0, 0
        n = sum(1 for _ in reader)
    return n, len(header)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--recursive", action="store_true", help="also read sub-folders")
    ap.add_argument("--csv", help="write the result to this CSV file")
    ap.add_argument("--latex", help="write the result as a LaTeX table to this file")
    a = ap.parse_args()

    root = Path(a.folder)
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")
    pattern = "**/*" if a.recursive else "*"
    files = sorted(p for p in root.glob(pattern)
                   if p.is_file() and (p.name.lower().endswith(".csv") or p.name.lower().endswith(".csv.gz")))
    if not files:
        sys.exit("No CSV file found.")

    rows = []
    for p in files:
        try:
            n, cols = count_rows(p)
        except Exception as e:  # keep going if one file is unreadable
            print(f"! {p}: {e}", file=sys.stderr)
            continue
        rows.append((str(p.relative_to(root)), n, cols, p.stat().st_size))

    width = max(len(r[0]) for r in rows)
    print(f"{'file':<{width}}  {'rows':>12}  {'columns':>7}  {'size (MB)':>10}")
    for name, n, cols, size in rows:
        print(f"{name:<{width}}  {n:>12,}  {cols:>7}  {size/1e6:>10.2f}")
    print(f"{'TOTAL':<{width}}  {sum(r[1] for r in rows):>12,}")

    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["file", "rows", "columns", "size_bytes"])
            w.writerows(rows)
    if a.latex:
        def esc(s):
            return s.replace("\\", "").replace("_", "\\_")
        with open(a.latex, "w", encoding="utf-8") as f:
            f.write("\\begin{tabular}{lr}\n\\toprule\nFile & Rows \\\\\n\\midrule\n")
            for name, n, _, _ in rows:
                f.write(f"\\texttt{{{esc(name)}}} & {n:,} \\\\\n".replace(",", "\\,"))
            f.write("\\bottomrule\n\\end{tabular}\n")


if __name__ == "__main__":
    main()
