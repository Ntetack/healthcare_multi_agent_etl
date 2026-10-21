"""
Read-only diagnostic for observation. Changes nothing.

Context: our observation table holds about 80 000 rows (79 228 of them from
CHARTEVENTS) while the reference holds about 22 500 for the same patients. The
direction is the opposite of measurement and drug_exposure: here WE hold far
more. This script answers, one report section each:

  1. Composition of each side: rows, concept 0, domain and status (standard,
     classification, non-standard, deleted, upgraded) of the concepts, rows per
     observation_type_concept_id, how many rows carry a number, a text or a
     concept as value.
  2. Item level: every source value is compared on its own (same concept,
     different concept, one side unmapped, only on our side, only on theirs).
  3. Row level, both directions: each row of one side falls in exactly one
     category with respect to the other side.
  4. Where the reference puts what we put in observation: for the source values
     we hold in observation and the reference does not, are they in the
     reference's measurement, drug_exposure, procedure_occurrence or
     condition_occurrence tables, or nowhere?
  5. Our rows that carry a numeric value: a number normally belongs to
     measurement, so these rows are candidates for a domain routing problem.

Usage (same connection arguments as investigate_measurement.py):
    python scripts/investigate_observation.py \
        --patients-csv data/raw/hospital_b/batch39/PATIENTS.csv \
        --our-source-column ROW_ID --their-source-column SUBJECT_ID \
        --their-db-host localhost --their-db-name mimic --their-schema omop \
        --their-db-user postgres --their-db-password ... \
        --our-vocab-schema cdm_vocab --their-vocab-schema omop \
        --output reports/mimic/observation_investigation.md

Both observation tables are read ONLY for the matched patients (a WHERE on
person_id). Put the file next to investigate_measurement.py (same helpers).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

WANTED = [
    "person_id", "observation_concept_id", "observation_date", "observation_datetime",
    "observation_type_concept_id", "value_as_number", "value_as_string", "value_as_concept_id",
    "qualifier_concept_id", "unit_concept_id", "observation_source_value",
]
NUMERIC = ["value_as_number", "value_as_concept_id", "unit_concept_id"]

CROSS_TABLES = {
    "measurement": "measurement_source_value",
    "drug_exposure": "drug_source_value",
    "procedure_occurrence": "procedure_source_value",
    "condition_occurrence": "condition_source_value",
}

ROW_CATEGORIES = [
    "A. same concept, same datetime",
    "B. same concept, same day, other time",
    "C. same concept, other day",
    "D. item mapped identically, this patient has no such row",
    "E. item mapped to another concept on the other side",
    "F. item present on the other side but unmapped (concept 0)",
    "G. item absent on the other side",
    "H. row without source value",
]


# ----------------------------------------------------------------- helpers ---

def prepare(frame: pd.DataFrame) -> pd.DataFrame:
    f = frame.copy()
    for col in WANTED:
        if col not in f.columns:
            f[col] = np.nan
    f["concept"] = pd.to_numeric(f["observation_concept_id"], errors="coerce").fillna(0).astype("int64")
    f["type_id"] = pd.to_numeric(f["observation_type_concept_id"], errors="coerce").fillna(0).astype("int64")
    f["date"] = pd.to_datetime(f["observation_date"], errors="coerce").dt.normalize()
    dt = pd.to_datetime(f["observation_datetime"], errors="coerce")
    f["dt"] = dt.fillna(f["date"])
    src = f["observation_source_value"].astype("object").where(f["observation_source_value"].notna(), "")
    f["src"] = src.astype(str).str.strip().replace({"nan": "", "None": ""})
    for col in NUMERIC:
        f[col] = pd.to_numeric(f[col], errors="coerce")
    f["has_number"] = f["value_as_number"].notna()
    f["has_text"] = f["value_as_string"].astype("object").where(f["value_as_string"].notna(), "").astype(str).str.strip().ne("")
    f["has_concept"] = f["value_as_concept_id"].fillna(0) != 0
    return f


def pct(a, b) -> str:
    return f"{a} ({100 * a / b:.1f}%)" if b else "n/a"


def _in(left: pd.DataFrame, right: pd.DataFrame, cols: list[str]) -> np.ndarray:
    """True where the combination of `cols` on a row of `left` exists in `right`."""
    r = right.dropna(subset=cols)[cols].drop_duplicates()
    valid = left[cols].notna().all(axis=1).to_numpy()
    if r.empty:
        return np.zeros(len(left), dtype=bool)
    hit = pd.MultiIndex.from_frame(left[cols]).isin(pd.MultiIndex.from_frame(r))
    return hit & valid


def concept_status(concepts: pd.DataFrame) -> pd.Series:
    """concept_id -> readable status from standard_concept and invalid_reason."""
    std = concepts["standard_concept"].astype("object").where(concepts["standard_concept"].notna(), "")
    inv = concepts["invalid_reason"].astype("object").where(concepts["invalid_reason"].notna(), "")
    base = np.select([std == "S", std == "C"], ["standard", "classification"], default="non-standard")
    tail = np.select([inv == "D", inv == "U"], [" / deleted", " / upgraded"], default="")
    return pd.Series([b + t for b, t in zip(base, tail)], index=concepts["concept_id"].to_numpy())


# ------------------------------------------------------------- 1. composition ---

def composition(f: pd.DataFrame, concepts: pd.DataFrame) -> dict:
    info = concepts.drop_duplicates("concept_id").set_index("concept_id")
    status = concept_status(concepts.drop_duplicates("concept_id"))
    names = info["concept_name"]
    nz = f[f["concept"] != 0]
    top = nz.groupby("concept").size().sort_values(ascending=False).head(10)
    types = f.groupby("type_id").agg(rows=("concept", "size"), zero=("concept", lambda s: int((s == 0).sum())))
    return {
        "rows": len(f),
        "concept_zero": int((f["concept"] == 0).sum()),
        "domains": nz["concept"].map(info["domain_id"]).fillna("unknown").value_counts().head(8).to_dict(),
        "vocabularies": nz["concept"].map(info["vocabulary_id"]).fillna("unknown").value_counts().head(6).to_dict(),
        "status": nz["concept"].map(status).fillna("unknown").value_counts().to_dict(),
        "src_empty": int((f["src"] == "").sum()),
        "distinct_src": int(f.loc[f["src"] != "", "src"].nunique()),
        "distinct_concepts": int(nz["concept"].nunique()),
        "with_number": int(f["has_number"].sum()),
        "with_text": int(f["has_text"].sum()),
        "with_concept": int(f["has_concept"].sum()),
        "types": [(int(t), str(names.get(t, "?")), int(r["rows"]), int(r["zero"])) for t, r in types.iterrows()],
        "top": [(int(c), str(names.get(c, "?")), int(n)) for c, n in top.items()],
    }


# ------------------------------------------------------------- 2. item level ---

def _mode(frame: pd.DataFrame) -> pd.Series:
    """Most frequent concept per source value."""
    g = frame.groupby(["src", "concept"]).size().rename("n").reset_index()
    g = g.sort_values(["src", "n"], ascending=[True, False])
    return g.drop_duplicates("src").set_index("src")["concept"]


def item_level(ours: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    o = ours[ours["src"] != ""]
    r = ref[ref["src"] != ""]
    srcs = sorted(set(o["src"]) | set(r["src"]))
    items = pd.DataFrame(index=pd.Index(srcs, name="src"))
    items["ours_rows"] = o.groupby("src").size().reindex(items.index).fillna(0).astype(int)
    items["ref_rows"] = r.groupby("src").size().reindex(items.index).fillna(0).astype(int)
    items["ours_nz_rows"] = o[o["concept"] != 0].groupby("src").size().reindex(items.index).fillna(0).astype(int)
    items["ref_nz_rows"] = r[r["concept"] != 0].groupby("src").size().reindex(items.index).fillna(0).astype(int)
    onz, rnz = o[o["concept"] != 0], r[r["concept"] != 0]
    items["ours_concept"] = _mode(onz).reindex(items.index) if len(onz) else np.nan
    items["ref_concept"] = _mode(rnz).reindex(items.index) if len(rnz) else np.nan
    items["category"] = np.select(
        [(items["ours_rows"] > 0) & (items["ref_rows"] == 0),
         (items["ours_rows"] == 0) & (items["ref_rows"] > 0),
         (items["ours_nz_rows"] == 0) | (items["ref_nz_rows"] == 0),
         items["ours_concept"] == items["ref_concept"]],
        ["only on our side", "only on the reference side", "one side unmapped", "same concept"],
        default="different concept")
    return items


def item_summary(items: pd.DataFrame) -> list[tuple[str, int, int, int]]:
    out = []
    for cat in ["same concept", "different concept", "one side unmapped", "only on our side", "only on the reference side"]:
        sub = items[items["category"] == cat]
        out.append((cat, len(sub), int(sub["ours_rows"].sum()), int(sub["ref_rows"].sum())))
    return out


def item_tops(items: pd.DataFrame, names: pd.Series, category: str, by: str, top: int = 15) -> list[tuple]:
    sub = items[items["category"] == category].sort_values(by, ascending=False).head(top)
    def nm(c):
        return f"{int(c)} {names.get(c, '?')}" if pd.notna(c) else "-"
    return [(src, int(r["ours_rows"]), nm(r["ours_concept"]), int(r["ref_rows"]), nm(r["ref_concept"]))
            for src, r in sub.iterrows()]


# ------------------------------------------------------------- 3. row level ---

def classify_rows(rows: pd.DataFrame, other: pd.DataFrame, items: pd.DataFrame, side: str) -> pd.Series:
    """Category of each row of `rows` (concept <> 0) with respect to `other`.
    `side` is "ours" or "ref"; `items` is the item_level table."""
    o = other[other["concept"] != 0]
    a = _in(rows, o, ["person_id", "concept", "dt"])
    b = _in(rows, o, ["person_id", "concept", "date"])
    c = _in(rows, o, ["person_id", "concept"])
    cat_of = items["category"]
    item_cat = rows["src"].map(cat_of).fillna("")
    absent = "only on our side" if side == "ours" else "only on the reference side"
    cat = np.select(
        [a, b, c, rows["src"] == "", item_cat == "same concept", item_cat == "different concept",
         item_cat == "one side unmapped", item_cat == absent],
        [ROW_CATEGORIES[0], ROW_CATEGORIES[1], ROW_CATEGORIES[2], ROW_CATEGORIES[7], ROW_CATEGORIES[3],
         ROW_CATEGORIES[4], ROW_CATEGORIES[5], ROW_CATEGORIES[6]],
        default=ROW_CATEGORIES[7])
    return pd.Series(cat, index=rows.index, name="category")


# ------------------------------------------------- 4. where the reference puts it ---

def cross_tables(ours: pd.DataFrame, items: pd.DataFrame, ref_counts: dict[str, pd.Series]) -> dict:
    """Our observation rows whose source value does not exist in the reference's
    observation: do they exist in another reference table?"""
    lost = ours[ours["src"].isin(items.index[items["category"] == "only on our side"]) & (ours["src"] != "")]
    keys = lost["src"].str.lower()
    found = pd.DataFrame(index=lost.index)
    for table, counts in ref_counts.items():
        found[table] = keys.isin(set(counts.index))
    found["nowhere"] = ~found.any(axis=1)
    first = np.select([found[t] for t in ref_counts] + [found["nowhere"]],
                      list(ref_counts) + ["nowhere"], default="nowhere")
    by_src = (lost.assign(first=first).groupby(["first", "src"]).size().rename("n").reset_index()
              .sort_values("n", ascending=False))
    summary = lost.assign(first=first).groupby("first").agg(rows=("src", "size"), items=("src", "nunique"))
    tops = {t: list(zip(g["src"], g["n"].astype(int)))[:10] for t, g in by_src.groupby("first")}
    return {"rows": len(lost), "summary": summary, "tops": tops, "tables": list(ref_counts)}


# --------------------------------------------------- 5. numeric values on ours ---

def numeric_on_ours(ours: pd.DataFrame, names: pd.Series, top: int = 10) -> dict:
    n = ours[ours["has_number"]]
    g = n.groupby("concept").size().sort_values(ascending=False).head(top)
    return {
        "rows": len(n), "share": (len(n) / len(ours)) if len(ours) else 0.0,
        "tops": [(int(c), str(names.get(c, "?")), int(k)) for c, k in g.items()],
    }


# ------------------------------------------------------------------ render ---

def _comp_lines(title: str, c: dict) -> list[str]:
    lines = [f"### {title}", "",
             f"Rows: {c['rows']}. Concept 0: {pct(c['concept_zero'], c['rows'])}. "
             f"Source value empty: {pct(c['src_empty'], c['rows'])}. "
             f"Distinct source values: {c['distinct_src']}. Distinct concepts (not 0): {c['distinct_concepts']}.",
             "",
             f"Rows with a number: {pct(c['with_number'], c['rows'])}; with text: {pct(c['with_text'], c['rows'])}; "
             f"with a concept as value: {pct(c['with_concept'], c['rows'])}.",
             "", f"Domains of the concepts (not 0): {c['domains']}",
             "", f"Vocabularies: {c['vocabularies']}",
             "", f"Status of the concepts (not 0): {c['status']}", "",
             "| Type concept | Name | Rows | Concept 0 |", "|---|---|---|---|"]
    lines += [f"| {t} | {n} | {r} | {z} |" for t, n, r, z in c["types"]]
    lines += ["", "| Most frequent concepts | n |", "|---|---|"]
    lines += [f"| {cid} {nm} | {k} |" for cid, nm, k in c["top"]]
    lines.append("")
    return lines


def render(co, cr, items, summary, tops_diff, tops_ours_only, tops_ref_only,
           cats_ours, cats_ref, cross, num, n_matched) -> list[str]:
    L = ["# observation : investigation", "", f"Matched patients: {n_matched}.", "", "## 1. Composition", ""]
    L += _comp_lines("Ours", co) + _comp_lines("Reference", cr)

    L += ["## 2. Item level: each source value on its own", "",
          "A source value is a string compared as is (an ITEMID on one side and a label on the other would "
          "show up as two different items: read 'only on one side' with that in mind).", "",
          "| Category | Items | Our rows | Reference rows |", "|---|---|---|---|"]
    L += [f"| {c} | {n} | {o} | {r} |" for c, n, o, r in summary]
    for title, rows in [("Items mapped to another concept (largest first)", tops_diff),
                        ("Items only on our side (largest first)", tops_ours_only),
                        ("Items only on the reference side (largest first)", tops_ref_only)]:
        L += ["", f"### {title}", "", "| item | our rows | our concept | reference rows | reference concept |",
              "|---|---|---|---|---|"]
        L += [f"| {s} | {o} | {oc} | {r} | {rc} |" for s, o, oc, r, rc in rows]

    for title, cats in [("Our rows with a real concept", cats_ours), ("Reference rows with a real concept", cats_ref)]:
        total = len(cats)
        L += ["", f"## 3. {title}, one category each", "", f"{total} rows.", "",
              "| Category | Rows | Share |", "|---|---|---|"]
        vc = cats.value_counts()
        L += [f"| {c} | {int(vc.get(c, 0))} | {100 * int(vc.get(c, 0)) / total:.1f}% |" if total else f"| {c} | 0 | n/a |"
              for c in ROW_CATEGORIES]

    L += ["", "## 4. Where the reference puts what we hold only in observation", "",
          f"{cross['rows']} of our rows have a source value absent from the reference's observation. "
          f"First reference table (in the order {', '.join(cross['tables'])}) in which that source value appears:", "",
          "| Reference table | Our rows | Items |", "|---|---|---|"]
    for table, r in cross["summary"].iterrows():
        L.append(f"| {table} | {int(r['rows'])} | {int(r['items'])} |")
    for table, rows in cross["tops"].items():
        L += ["", f"Largest source values ({table}).", "", "| item | our rows |", "|---|---|"]
        L += [f"| {s} | {n} |" for s, n in rows]

    L += ["", "## 5. Our rows that carry a numeric value", "",
          f"{num['rows']} rows ({100 * num['share']:.1f}% of ours). A number is normally a measurement.", "",
          "| Concept | Rows |", "|---|---|"]
    L += [f"| {c} {nm} | {k} |" for c, nm, k in num["tops"]]
    L.append("")
    return L


# -------------------------------------------------------------------- main ---

def main():
    from sqlalchemy import text
    from compare_content import _remote_session_scope, build_crosswalk, _get_columns
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
    our_ids = [int(x) for x in crosswalk["our_person_id"].unique()]
    their_ids = [int(x) for x in crosswalk["their_person_id"].unique()]

    def read(session, schema, ids):
        have = _get_columns(session, schema, "observation")
        cols = [c for c in WANTED if c in have]
        sql = text(f"SELECT {', '.join(cols)} FROM {schema}.observation WHERE person_id = ANY(:ids)")
        return pd.read_sql(sql, session.connection(), params={"ids": ids})

    def read_concepts(session, schema, ids):
        sql = text(f"SELECT concept_id, concept_name, domain_id, vocabulary_id, standard_concept, invalid_reason "
                   f"FROM {schema}.concept WHERE concept_id = ANY(:ids)")
        return pd.read_sql(sql, session.connection(), params={"ids": ids})

    def read_source_counts(session, schema, ids):
        out = {}
        for table, col in CROSS_TABLES.items():
            try:
                sql = text(f"SELECT lower(btrim({col}::text)) AS src, COUNT(*) AS n FROM {schema}.{table} "
                           f"WHERE person_id = ANY(:ids) AND {col} IS NOT NULL GROUP BY 1")
                df = pd.read_sql(sql, session.connection(), params={"ids": ids})
                out[table] = df.set_index("src")["n"]
            except Exception as exc:  # a missing table must not stop the report
                print(f"skipped {table}: {exc}")
                session.rollback()
        return out

    with our_session_scope() as s:
        ours = read(s, a.our_schema, our_ids)
    with their_scope() as s:
        theirs = read(s, a.their_schema, their_ids)
        ref_counts = read_source_counts(s, a.their_schema, their_ids)

    ours = ours.merge(crosswalk, left_on="person_id", right_on="our_person_id", how="inner")
    ours["person_id"] = ours["their_person_id"]
    ours = ours.drop(columns=["our_person_id", "their_person_id"])
    print(f"ours: {len(ours)} rows; reference: {len(theirs)} rows")

    ids = set()
    for frame in (ours, theirs):
        for col in ("observation_concept_id", "observation_type_concept_id", "value_as_concept_id"):
            if col in frame.columns:
                ids |= set(pd.to_numeric(frame[col], errors="coerce").dropna().astype(int))
    ids = sorted(int(i) for i in ids if i)
    with our_session_scope() as s:
        oc = read_concepts(s, a.our_vocab_schema, ids)
    with their_scope() as s:
        tc = read_concepts(s, their_vocab, ids)
    ours, theirs = prepare(ours), prepare(theirs)
    names = pd.concat([tc, oc]).drop_duplicates("concept_id").set_index("concept_id")["concept_name"]

    items = item_level(ours, theirs)
    ours_nz, ref_nz = ours[ours["concept"] != 0], theirs[theirs["concept"] != 0]
    cats_ours = classify_rows(ours_nz, theirs, items, "ours")
    cats_ref = classify_rows(ref_nz, ours, items, "ref")
    cross = cross_tables(ours, items, ref_counts)
    report = render(composition(ours, oc), composition(theirs, tc), items, item_summary(items),
                    item_tops(items, names, "different concept", "ref_rows"),
                    item_tops(items, names, "only on our side", "ours_rows"),
                    item_tops(items, names, "only on the reference side", "ref_rows"),
                    cats_ours, cats_ref, cross, numeric_on_ours(ours, names), len(crosswalk))
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    items.assign(ours_name=items["ours_concept"].map(names), ref_name=items["ref_concept"].map(names)).to_csv(
        out.with_suffix(".items.csv"))
    print(f"written: {out}\nwritten: {out.with_suffix('.items.csv')}")


if __name__ == "__main__":
    main()
