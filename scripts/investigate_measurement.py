"""
Read-only diagnostic for measurement. Changes nothing.

Context: the comparator pairs rows on (patient, concept, date). For measurement
that key is far too coarse (a chart holds dozens of values per patient and day),
so 86 063 of the 823 220 reference rows pair up and the rest is hard to read.
This script separates the questions the single coverage figure mixes:

  1. Composition: share of concept 0, of concepts outside the Measurement
     domain, of empty values and units, on each side.
  2. Item level: every source value (an ITEMID) is compared ON ITS OWN, before
     any row is looked at. Does the reference give it a concept? Do we? The same?
     This isolates concept mapping from event existence.
  3. Row level: every reference row with a real concept falls in exactly one
     category (reproduced; time or day shifted; item mapped identically but
     the event is missing; item mapped to another concept; item unmapped on our
     side; item absent on our side).
  4. Volume per item: for items mapped identically, how many rows do we keep
     compared with the reference?
  5. Values on pairs that are unambiguous (one row per side for the same
     patient, concept, datetime and source value): value, unit.
  6. Time of day: offset between the two datetimes on unambiguous pairs.

Usage (same connection arguments as investigate_drug_exposure.py):
    python scripts/investigate_measurement.py \
        --patients-csv data/raw/hospital_b/batch39/PATIENTS.csv \
        --our-source-column ROW_ID --their-source-column SUBJECT_ID \
        --their-db-host localhost --their-db-name mimic --their-schema omop \
        --their-db-user postgres --their-db-password ... \
        --our-vocab-schema cdm_vocab --their-vocab-schema omop \
        --output reports/mimic/measurement_investigation.md

Both tables are read ONLY for the matched patients (a WHERE on person_id): the
baseline holds the whole of MIMIC and must not be read in full.
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
    "person_id", "measurement_concept_id", "measurement_date", "measurement_datetime",
    "value_as_number", "unit_concept_id", "unit_source_value", "value_source_value",
    "measurement_source_value", "measurement_type_concept_id", "range_low", "range_high",
]
NUMERIC = ["value_as_number", "unit_concept_id", "range_low", "range_high"]

ROW_CATEGORIES = [
    "A. same concept, same datetime",
    "B. same concept, same day, other time",
    "C. same concept, other day",
    "D. item mapped identically, this patient has no such row",
    "E. item mapped to another concept on our side",
    "F. item present on our side but unmapped (concept 0)",
    "G. item absent on our side",
    "H. reference row without source value",
]


# ----------------------------------------------------------------- helpers ---

def prepare(frame: pd.DataFrame) -> pd.DataFrame:
    f = frame.copy()
    for col in WANTED:
        if col not in f.columns:
            f[col] = np.nan
    f["concept"] = pd.to_numeric(f["measurement_concept_id"], errors="coerce").fillna(0).astype("int64")
    f["date"] = pd.to_datetime(f["measurement_date"], errors="coerce").dt.normalize()
    dt = pd.to_datetime(f["measurement_datetime"], errors="coerce")
    f["dt"] = dt.fillna(f["date"])
    f["src"] = f["measurement_source_value"].astype("object").where(f["measurement_source_value"].notna(), "")
    f["src"] = f["src"].astype(str).str.strip().replace({"nan": "", "None": ""})
    for col in NUMERIC:
        f[col] = pd.to_numeric(f[col], errors="coerce")
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


# ------------------------------------------------------------- 1. composition ---

def composition(f: pd.DataFrame, names: pd.Series, domains: pd.Series) -> dict:
    nz = f[f["concept"] != 0]
    dom = nz["concept"].map(domains).fillna("unknown")
    top = nz.groupby("concept").size().sort_values(ascending=False).head(10)
    return {
        "rows": len(f),
        "concept_zero": int((f["concept"] == 0).sum()),
        "domains": dom.value_counts().head(6).to_dict(),
        "value_empty": int(f["value_as_number"].isna().sum()),
        "unit_empty": int((f["unit_concept_id"].isna() | (f["unit_concept_id"] == 0)).sum()),
        "src_empty": int((f["src"] == "").sum()),
        "distinct_src": int(f.loc[f["src"] != "", "src"].nunique()),
        "distinct_concepts": int(nz["concept"].nunique()),
        "top": [(int(c), str(names.get(c, "?")), int(n)) for c, n in top.items()],
    }


# ------------------------------------------------------------- 2. item level ---

def _mode(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Most frequent concept per source value, and the number of distinct concepts."""
    g = frame.groupby(["src", "concept"]).size().rename("n").reset_index()
    g = g.sort_values(["src", "n"], ascending=[True, False])
    top = g.drop_duplicates("src").set_index("src")["concept"]
    return top, g.groupby("src")["concept"].nunique()


def item_level(ours: pd.DataFrame, ref: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    ref_nz = ref[(ref["concept"] != 0) & (ref["src"] != "")]
    ours_all = ours[ours["src"] != ""]
    ours_nz = ours_all[ours_all["concept"] != 0]

    rcon, rn = _mode(ref_nz)
    items = pd.DataFrame({"ref_concept": rcon, "ref_nconcepts": rn})
    items["ref_rows"] = ref_nz.groupby("src").size()
    items["ours_rows"] = ours_all.groupby("src").size().reindex(items.index).fillna(0).astype(int)
    items["ours_nz_rows"] = ours_nz.groupby("src").size().reindex(items.index).fillna(0).astype(int)
    if len(ours_nz):
        ocon, _ = _mode(ours_nz)
        items["ours_concept"] = ocon.reindex(items.index)
    else:
        items["ours_concept"] = np.nan
    items["category"] = np.select(
        [items["ours_rows"] == 0, items["ours_nz_rows"] == 0, items["ours_concept"] == items["ref_concept"]],
        ["ours absent", "ours unmapped", "same concept"], default="different concept")

    ref_zero_src = set(ref.loc[(ref["concept"] == 0) & (ref["src"] != ""), "src"])
    only = ours_all[~ours_all["src"].isin(items.index)]
    only_info = {
        "items": int(only["src"].nunique()), "rows": len(only),
        "ref_has_it_at_zero_items": int(only.loc[only["src"].isin(ref_zero_src), "src"].nunique()),
        "ref_has_it_at_zero_rows": int(only["src"].isin(ref_zero_src).sum()),
        "ours_unmapped_rows": int((only["concept"] == 0).sum()),
    }
    return items, only_info


def item_tops(items: pd.DataFrame, names: pd.Series, top: int = 15) -> dict:
    def rows(frame, with_ours):
        out = []
        for src, r in frame.head(top).iterrows():
            out.append((src, int(r["ref_concept"]), str(names.get(r["ref_concept"], "?")),
                        int(r["ref_rows"]), int(r["ours_rows"]),
                        (int(r["ours_concept"]), str(names.get(r["ours_concept"], "?"))) if with_ours and pd.notna(r["ours_concept"]) else None))
        return out
    diff = items[items["category"] == "different concept"].sort_values("ref_rows", ascending=False)
    unm = items[items["category"] == "ours unmapped"].sort_values("ref_rows", ascending=False)
    absn = items[items["category"] == "ours absent"].sort_values("ref_rows", ascending=False)
    return {"different": rows(diff, True), "unmapped": rows(unm, False), "absent": rows(absn, False)}


# -------------------------------------------------------------- 3. row level ---

def classify_rows(ref_nz: pd.DataFrame, ours: pd.DataFrame, items: pd.DataFrame) -> pd.Series:
    o = ours[ours["concept"] != 0]
    a = _in(ref_nz, o, ["person_id", "concept", "dt"])
    b = _in(ref_nz, o, ["person_id", "concept", "date"])
    c = _in(ref_nz, o, ["person_id", "concept"])
    item_cat = ref_nz["src"].map(items["category"]).fillna("")
    cat = np.select(
        [a, b, c, ref_nz["src"] == "", item_cat == "same concept", item_cat == "different concept",
         item_cat == "ours unmapped", item_cat == "ours absent"],
        [ROW_CATEGORIES[0], ROW_CATEGORIES[1], ROW_CATEGORIES[2], ROW_CATEGORIES[7], ROW_CATEGORIES[3],
         ROW_CATEGORIES[4], ROW_CATEGORIES[5], ROW_CATEGORIES[6]],
        default=ROW_CATEGORIES[7])
    return pd.Series(cat, index=ref_nz.index, name="category")


# --------------------------------------------------------------- 4. volumes ---

def volumes(items: pd.DataFrame, names: pd.Series, top: int = 15) -> dict:
    same = items[items["category"] == "same concept"].copy()
    if same.empty:
        return {"items": 0}
    same["ratio"] = same["ours_nz_rows"] / same["ref_rows"]
    same["lost"] = same["ref_rows"] - same["ours_nz_rows"]
    worst = same[same["lost"] > 0].sort_values("lost", ascending=False).head(top)
    return {
        "items": len(same),
        "ref_rows": int(same["ref_rows"].sum()), "ours_rows": int(same["ours_nz_rows"].sum()),
        "ratio_quantiles": same["ratio"].quantile([.05, .25, .5, .75, .95]).round(3).to_dict(),
        "items_ratio_ge_95": int((same["ratio"] >= 0.95).sum()),
        "items_ratio_lt_50": int((same["ratio"] < 0.5).sum()),
        "worst": [(src, str(names.get(r["ref_concept"], "?")), int(r["ref_rows"]), int(r["ours_nz_rows"]))
                  for src, r in worst.iterrows()],
    }


# ---------------------------------------------------- 5-6. unambiguous pairs ---

def _unique_pairs(ours: pd.DataFrame, ref: pd.DataFrame, key: list[str]) -> pd.DataFrame:
    o = ours[(ours["concept"] != 0) & (ours["src"] != "")]
    r = ref[(ref["concept"] != 0) & (ref["src"] != "")]
    o = o[~o.duplicated(key, keep=False)]
    r = r[~r.duplicated(key, keep=False)]
    return o.merge(r, on=key, suffixes=("_o", "_r"))


def values_on_pairs(ours: pd.DataFrame, ref: pd.DataFrame, names: pd.Series) -> dict:
    key = ["person_id", "concept", "dt", "src"]
    m = _unique_pairs(ours, ref, key)
    if m.empty:
        return {"pairs": 0}
    vo, vr = m["value_as_number_o"], m["value_as_number_r"]
    both = vo.notna() & vr.notna()
    agree = both & np.isclose(vo, vr, rtol=1e-4, atol=1e-6)
    ratio = (vo[both & (vr != 0) & ~agree] / vr[both & (vr != 0) & ~agree]).replace([np.inf, -np.inf], np.nan).dropna()

    uo = m["unit_concept_id_o"].where(m["unit_concept_id_o"] != 0)
    ur = m["unit_concept_id_r"].where(m["unit_concept_id_r"] != 0)
    ub = uo.notna() & ur.notna()

    def tops(mask, n=8):
        t = m[mask].groupby(["src", "concept"]).size().sort_values(ascending=False).head(n)
        return [(s, str(names.get(c, "?")), int(k)) for (s, c), k in t.items()]

    bad = m[both & ~agree].copy()
    bad["ratio"] = bad["value_as_number_o"] / bad["value_as_number_r"].replace(0, np.nan)
    per_item = (bad.groupby(["src", "concept"]).agg(n=("ratio", "size"), median_ratio=("ratio", "median"))
                .sort_values("n", ascending=False).head(8))
    return {
        "pairs": len(m), "both_filled": int(both.sum()), "agree": int(agree.sum()),
        "ours_missing": int((vo.isna() & vr.notna()).sum()), "ref_missing": int((vo.notna() & vr.isna()).sum()),
        "both_missing": int((vo.isna() & vr.isna()).sum()),
        "ratio_quantiles": ratio.quantile([.05, .25, .5, .75, .95]).round(4).to_dict() if len(ratio) else {},
        "unit_both": int(ub.sum()), "unit_agree": int((ub & (uo == ur)).sum()),
        "unit_ours_missing": int((uo.isna() & ur.notna()).sum()), "unit_ref_missing": int((uo.notna() & ur.isna()).sum()),
        "top_ours_missing": tops(vo.isna() & vr.notna()),
        "top_bad": [(s, str(names.get(c, "?")), int(r["n"]), float(r["median_ratio"]) if pd.notna(r["median_ratio"]) else None)
                    for (s, c), r in per_item.iterrows()],
    }


def time_offsets(ours: pd.DataFrame, ref: pd.DataFrame) -> dict:
    key = ["person_id", "concept", "date", "src"]
    m = _unique_pairs(ours, ref, key)
    if m.empty:
        return {"pairs": 0}
    hours = ((m["dt_o"] - m["dt_r"]).dt.total_seconds() / 3600).round(2)
    return {"pairs": len(m), "same": int((hours == 0).sum()),
            "counts": hours.value_counts().head(10).to_dict()}


# ------------------------------------------------------------------ report ---

def render(co, cr, items, only_info, tops, cats, vol, vals, offs, names) -> list[str]:
    n_ref_nz = int(cats.shape[0])
    L = ["# measurement : investigation", "", "## 1. Composition", "",
         "| | Ours | Reference |", "|---|---|---|",
         f"| rows | {co['rows']} | {cr['rows']} |",
         f"| concept 0 | {pct(co['concept_zero'], co['rows'])} | {pct(cr['concept_zero'], cr['rows'])} |",
         f"| value_as_number empty | {pct(co['value_empty'], co['rows'])} | {pct(cr['value_empty'], cr['rows'])} |",
         f"| unit empty or 0 | {pct(co['unit_empty'], co['rows'])} | {pct(cr['unit_empty'], cr['rows'])} |",
         f"| source value empty | {pct(co['src_empty'], co['rows'])} | {pct(cr['src_empty'], cr['rows'])} |",
         f"| distinct source values | {co['distinct_src']} | {cr['distinct_src']} |",
         f"| distinct concepts (not 0) | {co['distinct_concepts']} | {cr['distinct_concepts']} |", "",
         f"Domains of the concepts (not 0). Ours: {co['domains']}. Reference: {cr['domains']}.", "",
         "| Ours, most frequent | n | Reference, most frequent | n |", "|---|---|---|---|"]
    for i in range(max(len(co["top"]), len(cr["top"]))):
        a = co["top"][i] if i < len(co["top"]) else ("", "", "")
        b = cr["top"][i] if i < len(cr["top"]) else ("", "", "")
        L.append(f"| {a[0]} {a[1]} | {a[2]} | {b[0]} {b[1]} | {b[2]} |")

    ref_items = len(items)
    L += ["", "## 2. Item level: each source value on its own", "",
          f"{ref_items} source values carry a real concept on the reference side. Rows are reference rows.", "",
          "| Our side | Items | Reference rows |", "|---|---|---|"]
    tot_rows = int(items["ref_rows"].sum())
    for cat in ["same concept", "different concept", "ours unmapped", "ours absent"]:
        sub = items[items["category"] == cat]
        L.append(f"| {cat} | {pct(len(sub), ref_items)} | {pct(int(sub['ref_rows'].sum()), tot_rows)} |")
    multi = int((items["ref_nconcepts"] > 1).sum())
    L += ["", f"Items the reference maps to more than one concept: {multi}.",
          f"Source values present on our side only: {only_info['items']} items, {only_info['rows']} rows "
          f"(of which the reference has the item at concept 0: {only_info['ref_has_it_at_zero_items']} items, "
          f"{only_info['ref_has_it_at_zero_rows']} rows; unmapped on our side too: {only_info['ours_unmapped_rows']} rows).", ""]

    for title, key, with_ours in [("Items mapped to another concept (largest first)", "different", True),
                                  ("Items present on our side but unmapped", "unmapped", False),
                                  ("Items absent on our side", "absent", False)]:
        L += [f"### {title}", ""]
        if with_ours:
            L += ["| item | reference concept | ref rows | our rows | our concept |", "|---|---|---|---|---|"]
            for src, rc, rn, rr, orows, oc in tops[key]:
                L.append(f"| {src} | {rc} {rn} | {rr} | {orows} | {oc[0]} {oc[1] if oc else ''} |" if oc else
                         f"| {src} | {rc} {rn} | {rr} | {orows} | |")
        else:
            L += ["| item | reference concept | ref rows | our rows |", "|---|---|---|---|"]
            for src, rc, rn, rr, orows, _ in tops[key]:
                L.append(f"| {src} | {rc} {rn} | {rr} | {orows} |")
        L.append("")

    L += ["## 3. Reference rows with a real concept, one category each", "",
          f"{n_ref_nz} rows.", "", "| Category | Rows | Share |", "|---|---|---|"]
    counts = cats.value_counts()
    for c in ROW_CATEGORIES:
        L.append(f"| {c} | {counts.get(c, 0)} | {100 * counts.get(c, 0) / n_ref_nz:.1f}% |")
    reproduced = counts.get(ROW_CATEGORIES[0], 0)
    L += ["", f"Reproduced to the minute (A): {pct(int(reproduced), n_ref_nz)}.", ""]

    L += ["## 4. Volume per item, for items mapped identically", ""]
    if not vol.get("items"):
        L += ["No item is mapped identically.", ""]
    else:
        L += [f"{vol['items']} items; reference rows {vol['ref_rows']}, our rows {vol['ours_rows']}.",
              f"Ratio ours/reference per item (5/25/50/75/95 %): {vol['ratio_quantiles']}.",
              f"Items with ratio >= 0.95: {vol['items_ratio_ge_95']}; with ratio < 0.5: {vol['items_ratio_lt_50']}.", "",
              "Largest losses (items where we keep fewer rows than the reference).", ""]
        if vol["worst"]:
            L += ["| item | concept | ref rows | our rows |", "|---|---|---|---|"]
            L += [f"| {s} | {n} | {r} | {o} |" for s, n, r, o in vol["worst"]] + [""]
        else:
            L += ["None: for every item mapped identically we keep at least as many rows.", ""]

    L += ["## 5. Values on unambiguous pairs", ""]
    if not vals.get("pairs"):
        L += ["No pair with one row per side for the same patient, concept, datetime and source value.", ""]
    else:
        L += [f"{vals['pairs']} pairs. Both values filled: {vals['both_filled']}; they agree: {pct(vals['agree'], vals['both_filled'])}.",
              f"Value missing on our side only: {vals['ours_missing']}; on the reference side only: {vals['ref_missing']}; on both: {vals['both_missing']}.",
              f"Ratio ours/reference where both are filled and differ (5/25/50/75/95 %): {vals['ratio_quantiles']}.",
              f"Units (concept): both filled {vals['unit_both']}, agree {pct(vals['unit_agree'], vals['unit_both'])}; "
              f"missing on our side only {vals['unit_ours_missing']}; on the reference side only {vals['unit_ref_missing']}.", "",
              "Items where we lack the value and the reference has it.", "", "| item | concept | pairs |", "|---|---|---|"]
        L += [f"| {s} | {n} | {k} |" for s, n, k in vals["top_ours_missing"]]
        L += ["", "Items with differing values (median ours/reference).", "", "| item | concept | pairs | median ratio |", "|---|---|---|---|"]
        L += [f"| {s} | {n} | {k} | {r} |" for s, n, k, r in vals["top_bad"]] + [""]

    L += ["## 6. Time of day on unambiguous pairs (same patient, concept, day, item)", ""]
    if not offs.get("pairs"):
        L += ["No such pair.", ""]
    else:
        L += [f"{offs['pairs']} pairs; same datetime: {pct(offs['same'], offs['pairs'])}.",
              "Offset ours minus reference, in hours (most frequent): " + str(offs["counts"]), ""]
    return L


# --------------------------------------------------------------------- I/O ---

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
        have = _get_columns(session, schema, "measurement")
        cols = [c for c in WANTED if c in have]
        sql = text(f"SELECT {', '.join(cols)} FROM {schema}.measurement WHERE person_id = ANY(:ids)")
        return pd.read_sql(sql, session.connection(), params={"ids": ids})

    def read_concepts(session, schema, ids):
        sql = text(f"SELECT concept_id, concept_name, domain_id FROM {schema}.concept WHERE concept_id = ANY(:ids)")
        return pd.read_sql(sql, session.connection(), params={"ids": ids})

    with our_session_scope() as s:
        ours = read(s, a.our_schema, our_ids)
    with their_scope() as s:
        theirs = read(s, a.their_schema, their_ids)

    ours = ours.merge(crosswalk, left_on="person_id", right_on="our_person_id", how="inner")
    ours["person_id"] = ours["their_person_id"]
    ours = ours.drop(columns=["our_person_id", "their_person_id"])
    print(f"ours: {len(ours)} rows; reference: {len(theirs)} rows")

    all_ids = set(pd.to_numeric(ours["measurement_concept_id"], errors="coerce").dropna().astype(int)) | \
              set(pd.to_numeric(theirs["measurement_concept_id"], errors="coerce").dropna().astype(int))
    all_ids = sorted(int(i) for i in all_ids if i)
    with our_session_scope() as s:
        oc = read_concepts(s, a.our_vocab_schema, all_ids)
    with their_scope() as s:
        tc = read_concepts(s, their_vocab, all_ids)
    allc = pd.concat([tc, oc]).drop_duplicates("concept_id")
    names = allc.set_index("concept_id")["concept_name"]
    domains = allc.set_index("concept_id")["domain_id"]

    ours, theirs = prepare(ours), prepare(theirs)
    items, only_info = item_level(ours, theirs)
    ref_nz = theirs[theirs["concept"] != 0]
    cats = classify_rows(ref_nz, ours, items)
    report = render(composition(ours, names, domains), composition(theirs, names, domains), items, only_info,
                    item_tops(items, names), cats, volumes(items, names),
                    values_on_pairs(ours, theirs, names), time_offsets(ours, theirs), names)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    items.assign(ref_name=items["ref_concept"].map(names), ours_name=items["ours_concept"].map(names)).to_csv(
        out.with_suffix(".items.csv"))
    print(f"written: {out}\nwritten: {out.with_suffix('.items.csv')}")


if __name__ == "__main__":
    main()
