"""
Read-only diagnostic for procedure_occurrence: explains WHY our table and the
reference table (e.g. mimic-omop) barely overlap. It changes nothing.

It answers five questions, one report section each:
  1. What is each table made of? (rows per source vocabulary, share of concept 0)
  2. Where do procedure dates come from? (the admission start, its end, or neither)
  3. How much of the reference is found if the date is allowed to differ by k days?
  4. Which reference rows have no counterpart at all (same patient + same concept,
     any date), and what are they?
  5. Same question the other way round, for our rows.

Usage (same connection arguments as scripts/run_full_comparison.py):
    python scripts/investigate_procedures.py \
        --patients-csv data/raw/hospital_a/mimic/patients.csv \
        --our-source-column SUBJECT_ID --their-source-column SUBJECT_ID \
        --their-db-host localhost --their-db-name omop_cdm --their-schema cdm_mimic \
        --their-db-user synthea_user --their-db-password changeme \
        --our-vocab-schema cdm_vocab --their-vocab-schema cdm_mimic \
        --output reports/mimic/procedure_investigation.md

--*-vocab-schema is the schema holding the CONCEPT table used to name concepts and
to classify procedure_source_concept_id by vocabulary (ICD9Proc, CPT4, local...).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

TOLERANCES_DAYS = [0, 1, 3, 7]


# ----------------------------------------------------------------- analysis --

def classify_source(frame: pd.DataFrame, concept: pd.DataFrame) -> pd.DataFrame:
    """Adds `source_vocab`: the vocabulary of procedure_source_concept_id."""
    vocab = concept.set_index("concept_id")["vocabulary_id"]
    sid = frame["procedure_source_concept_id"].fillna(0).astype("int64")
    out = frame.copy()
    out["source_vocab"] = sid.map(vocab).fillna("unknown id")
    out.loc[sid == 0, "source_vocab"] = "no source concept"
    return out


def composition(frame: pd.DataFrame, concept: pd.DataFrame) -> dict:
    names = concept.set_index("concept_id")["concept_name"]
    std = frame["procedure_concept_id"].fillna(0).astype("int64")
    top = (frame.assign(_c=std).groupby("_c").size().sort_values(ascending=False).head(10))
    return {
        "rows": len(frame),
        "concept_zero": int((std == 0).sum()),
        "by_vocab": frame["source_vocab"].value_counts().to_dict(),
        "top_concepts": [(int(c), str(names.get(c, "?")), int(n)) for c, n in top.items()],
    }


def date_origin(frame: pd.DataFrame, visits: pd.DataFrame) -> pd.DataFrame:
    """Per source vocabulary: is procedure_date equal to the visit start, the
    visit end, strictly inside the stay, outside it, or missing?"""
    v = visits.rename(columns={"visit_start_date": "_vs", "visit_end_date": "_ve"})
    merged = frame.merge(v[["visit_occurrence_id", "_vs", "_ve"]], on="visit_occurrence_id", how="left")
    d = pd.to_datetime(merged["procedure_date"], errors="coerce").dt.normalize()
    vs = pd.to_datetime(merged["_vs"], errors="coerce").dt.normalize()
    ve = pd.to_datetime(merged["_ve"], errors="coerce").dt.normalize()
    cat = np.select(
        [d.isna(), vs.isna(), d == vs, d == ve, (d > vs) & (d < ve)],
        ["no date", "no visit", "= visit start", "= visit end", "inside the stay"],
        default="outside the stay",
    )
    return pd.crosstab(merged["source_vocab"], pd.Series(cat, name="date is"))


def nearest_day_gap(theirs: pd.DataFrame, ours: pd.DataFrame) -> pd.Series:
    """For each reference row (by position): smallest |date difference| in days to
    one of OUR rows with the same patient and concept; NaN if there is none."""
    t = theirs.reset_index(drop=True)
    t["_i"] = t.index
    o = ours[["person_id", "procedure_concept_id", "procedure_date"]].rename(
        columns={"procedure_date": "_od"})
    m = t[["_i", "person_id", "procedure_concept_id", "procedure_date"]].merge(
        o, on=["person_id", "procedure_concept_id"], how="left")
    m["_gap"] = (pd.to_datetime(m["procedure_date"]).dt.normalize()
                 - pd.to_datetime(m["_od"]).dt.normalize()).abs().dt.days
    return m.groupby("_i")["_gap"].min().reindex(range(len(t)))


def coverage_by_tolerance(theirs: pd.DataFrame, ours: pd.DataFrame) -> pd.DataFrame:
    gaps = nearest_day_gap(theirs, ours)
    t = theirs.reset_index(drop=True)
    rows = []
    for group_name, mask in [("all reference rows", pd.Series(True, index=t.index)),
                             ("reference rows with a concept (not 0)", t["procedure_concept_id"].fillna(0) != 0)]:
        n = int(mask.sum())
        row = {"subset": group_name, "rows": n}
        for k in TOLERANCES_DAYS:
            row[f"date within {k} d"] = f"{int(((gaps <= k) & mask).sum())} ({100 * ((gaps <= k) & mask).sum() / n:.1f}%)" if n else "n/a"
        row["same patient+concept, any date"] = (
            f"{int((gaps.notna() & mask).sum())} ({100 * (gaps.notna() & mask).sum() / n:.1f}%)" if n else "n/a")
        rows.append(row)
    return pd.DataFrame(rows)


def unmatched(frame: pd.DataFrame, other: pd.DataFrame, concept: pd.DataFrame, top: int = 15) -> dict:
    """Rows whose (patient, concept) never appears on the other side."""
    names = concept.set_index("concept_id")["concept_name"]
    pairs = set(zip(other["person_id"], other["procedure_concept_id"].fillna(0).astype("int64")))
    cid = frame["procedure_concept_id"].fillna(0).astype("int64")
    mask = np.array([(p, c) not in pairs for p, c in zip(frame["person_id"], cid)])
    lost = frame[mask].assign(_c=cid[mask])
    top_concepts = (lost.groupby("_c").size().sort_values(ascending=False).head(top))
    return {
        "rows": int(mask.sum()),
        "share": float(mask.mean()) if len(frame) else 0.0,
        "by_vocab": lost["source_vocab"].value_counts().to_dict(),
        "concept_zero": int((lost["_c"] == 0).sum()),
        "top": [(int(c), str(names.get(c, "?")), int(n)) for c, n in top_concepts.items()],
    }


# ------------------------------------------------------------------ report ---

def md_table(df: pd.DataFrame) -> list[str]:
    cols = [df.index.name or ""] + [str(c) for c in df.columns] if df.index.name else [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for idx, r in df.iterrows():
        cells = ([str(idx)] if df.index.name else []) + [str(v) for v in r.values]
        out.append("| " + " | ".join(cells) + " |")
    return out


def render(ours_c, theirs_c, ours_dates, theirs_dates, cov, un_theirs, un_ours) -> list[str]:
    L = ["# procedure_occurrence : investigation", ""]
    L += ["## 1. Composition", "",
          "| | Ours | Reference |", "|---|---|---|",
          f"| rows | {ours_c['rows']} | {theirs_c['rows']} |",
          f"| procedure_concept_id = 0 | {ours_c['concept_zero']} | {theirs_c['concept_zero']} |", ""]
    vocabs = sorted(set(ours_c["by_vocab"]) | set(theirs_c["by_vocab"]))
    L += ["Rows per vocabulary of procedure_source_concept_id (this identifies the source table: "
          "ICD9Proc = PROCEDURES_ICD, CPT4 = CPTEVENTS, local/unknown ids = item based).", "",
          "| Source vocabulary | Ours | Reference |", "|---|---|---|"]
    L += [f"| {v} | {ours_c['by_vocab'].get(v, 0)} | {theirs_c['by_vocab'].get(v, 0)} |" for v in vocabs]
    L += ["", "Most frequent standard concepts.", "",
          "| Ours | n | Reference | n |", "|---|---|---|---|"]
    for i in range(max(len(ours_c["top_concepts"]), len(theirs_c["top_concepts"]))):
        a = ours_c["top_concepts"][i] if i < len(ours_c["top_concepts"]) else ("", "", "")
        b = theirs_c["top_concepts"][i] if i < len(theirs_c["top_concepts"]) else ("", "", "")
        L.append(f"| {a[0]} {a[1]} | {a[2]} | {b[0]} {b[1]} | {b[2]} |")
    L += ["", "## 2. Origin of procedure_date, by source vocabulary", "", "### Ours", ""]
    L += md_table(ours_dates) + ["", "### Reference", ""] + md_table(theirs_dates)
    L += ["", "MIMIC-III PROCEDURES_ICD has no date column. A date on those rows is therefore "
          "derived (most plausibly from the admission); the two tables above show which "
          "convention each side used.", ""]
    L += ["## 3. Coverage of the reference if the date may differ", ""] + md_table(cov.set_index("subset")) + [""]
    for title, u, side in [("4. Reference rows with no counterpart (same patient + concept, any date)", un_theirs, "reference"),
                           ("5. Our rows with no counterpart (same patient + concept, any date)", un_ours, "ours")]:
        L += [f"## {title}", "",
              f"{u['rows']} rows ({100 * u['share']:.1f}% of {side}); concept 0 among them: {u['concept_zero']}.", "",
              "By source vocabulary: " + ", ".join(f"{k}: {v}" for k, v in u["by_vocab"].items()), "",
              "| concept | n |", "|---|---|"]
        L += [f"| {c} {name} | {n} |" for c, name, n in u["top"]]
        L.append("")
    return L


# --------------------------------------------------------------------- I/O ---

def main():
    from sqlalchemy import text
    from compare_content import _remote_session_scope, build_crosswalk
    from app.tools.database.db import session_scope as our_session_scope

    p = argparse.ArgumentParser()
    p.add_argument("--our-schema", default="omop_temp")
    p.add_argument("--our-vocab-schema", default="cdm_vocab")
    p.add_argument("--their-db-host", required=True)
    p.add_argument("--their-db-port", default="5432")
    p.add_argument("--their-db-name", required=True)
    p.add_argument("--their-db-user", required=True)
    p.add_argument("--their-db-password", default=None)
    p.add_argument("--their-schema", default="public")
    p.add_argument("--their-vocab-schema", default=None)
    p.add_argument("--patients-csv", required=True)
    p.add_argument("--our-source-column", default="Id")
    p.add_argument("--their-source-column", default="Id")
    p.add_argument("--output", required=True)
    a = p.parse_args()

    password = a.their_db_password or os.environ.get("DB_PASSWORD", "")
    url = f"postgresql://{a.their_db_user}:{password}@{a.their_db_host}:{a.their_db_port}/{a.their_db_name}"
    their_scope = lambda: _remote_session_scope(url)
    their_vocab = a.their_vocab_schema or a.their_schema

    crosswalk = build_crosswalk(a.patients_csv, a.our_source_column, a.their_source_column,
                                a.our_schema, their_scope, a.their_schema)
    print(f"{len(crosswalk)} patients matched")

    proc_cols = ("person_id, procedure_concept_id, procedure_date, procedure_source_value, "
                 "procedure_source_concept_id, visit_occurrence_id")
    concept_sql = "SELECT concept_id, concept_name, vocabulary_id FROM {s}.concept"

    with our_session_scope() as s:
        ours = pd.read_sql(text(f"SELECT {proc_cols} FROM {a.our_schema}.procedure_occurrence"), s.connection())
        ovisits = pd.read_sql(text(f"SELECT visit_occurrence_id, visit_start_date, visit_end_date "
                                   f"FROM {a.our_schema}.visit_occurrence"), s.connection())
        oconcept = pd.read_sql(text(concept_sql.format(s=a.our_vocab_schema)), s.connection())
    with their_scope() as s:
        theirs = pd.read_sql(text(f"SELECT {proc_cols} FROM {a.their_schema}.procedure_occurrence"), s.connection())
        tvisits = pd.read_sql(text(f"SELECT visit_occurrence_id, visit_start_date, visit_end_date "
                                   f"FROM {a.their_schema}.visit_occurrence"), s.connection())
        tconcept = pd.read_sql(text(concept_sql.format(s=their_vocab)), s.connection())

    # one patient identifier for both sides: the reference's
    ours = ours.merge(crosswalk, left_on="person_id", right_on="our_person_id", how="inner")
    ours["person_id"] = ours["their_person_id"]
    ours = ours.drop(columns=["our_person_id", "their_person_id"])
    theirs = theirs[theirs["person_id"].isin(crosswalk["their_person_id"])]

    ours = classify_source(ours, oconcept)
    theirs = classify_source(theirs, tconcept)
    concept = pd.concat([tconcept, oconcept]).drop_duplicates("concept_id")

    report = render(
        composition(ours, concept), composition(theirs, concept),
        date_origin(ours, ovisits), date_origin(theirs, tvisits),
        coverage_by_tolerance(theirs, ours),
        unmatched(theirs, ours, concept), unmatched(ours, theirs, concept),
    )
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
