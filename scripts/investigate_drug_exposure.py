"""
Read-only diagnostic for drug_exposure: explains why 27 306 of our rows and
56 715 reference rows share only 9 456 matches although 69 % of the distinct
(patient, drug, start date, end date) keys exist on both sides. Changes nothing.

Report sections:
  1. Composition (type concepts, shape of drug_source_value, concept 0, top drugs)
  2. How rows pile up on keys (the key has no time, so repeated administrations
     of one drug on one day collapse into one key)
  3. Coverage under five keys, from the current one to "patient + drug, any date",
     counted on distinct keys AND on rows
  4. Rows whose (patient, drug) never appears on the other side, by source shape
  5. Quantity on rows that pair unambiguously (one row per side for the same
     patient, drug, start and end time): the only clean test of quantity

Usage (same connection arguments as scripts/investigate_procedures.py):
    python scripts/investigate_drug_exposure.py \
        --patients-csv data/raw/hospital_b/batch39/PATIENTS.csv \
        --our-source-column ROW_ID --their-source-column SUBJECT_ID \
        --their-db-host localhost --their-db-name mimic --their-schema omop \
        --their-db-user postgres --their-db-password ... \
        --our-vocab-schema cdm_vocab --their-vocab-schema omop \
        --output reports/mimic/drug_investigation.md
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

KEYS = {
    "A. patient + drug + start date + end date (current key)": ["drug_concept_id", "start_d", "end_d"],
    "B. patient + drug + start date": ["drug_concept_id", "start_d"],
    "C. patient + drug + start date and time": ["drug_concept_id", "start_dt"],
    "D. patient + drug + start and end date and time": ["drug_concept_id", "start_dt", "end_dt"],
    "E. patient + drug, any date": ["drug_concept_id"],
}


# ----------------------------------------------------------------- helpers ---

def prepare(frame: pd.DataFrame) -> pd.DataFrame:
    f = frame.copy()
    f["drug_concept_id"] = f["drug_concept_id"].fillna(0).astype("int64")
    f["start_d"] = pd.to_datetime(f["drug_exposure_start_date"], errors="coerce").dt.normalize()
    f["end_d"] = pd.to_datetime(f["drug_exposure_end_date"], errors="coerce").dt.normalize()
    f["start_dt"] = pd.to_datetime(f.get("drug_exposure_start_datetime"), errors="coerce")
    f["end_dt"] = pd.to_datetime(f.get("drug_exposure_end_datetime"), errors="coerce")
    f["source_shape"] = f["drug_source_value"].map(source_shape)
    return f


def source_shape(value) -> str:
    """The shape of the raw code tells which MIMIC table a row came from:
    an 11-digit NDC is PRESCRIPTIONS, a short integer is an ITEMID of
    INPUTEVENTS or CHARTEVENTS, free text is a drug name."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "empty"
    s = str(value).strip()
    if re.fullmatch(r"\d{10,11}", s):
        return "NDC (10-11 digits)"
    if re.fullmatch(r"\d{4,7}", s):
        return "itemid-like (4-7 digits)"
    if re.fullmatch(r"\d+", s):
        return "other number"
    return "text (drug name)"


def composition(f: pd.DataFrame, names: pd.Series) -> dict:
    top = f.groupby("drug_concept_id").size().sort_values(ascending=False).head(10)
    key_sizes = f.groupby(["person_id", "drug_concept_id", "start_d", "end_d"], dropna=False).size()
    return {
        "rows": len(f),
        "concept_zero": int((f["drug_concept_id"] == 0).sum()),
        "types": f["drug_type_concept_id"].fillna(-1).astype("int64").value_counts().to_dict()
        if "drug_type_concept_id" in f.columns else {},
        "shapes": f["source_shape"].value_counts().to_dict(),
        "top": [(int(c), str(names.get(c, "?")), int(n)) for c, n in top.items()],
        "distinct_keys": int(len(key_sizes)),
        "rows_per_key": key_sizes.describe(percentiles=[.5, .9, .99]).round(1).to_dict(),
        "rows_in_keys_of_10_plus": int(key_sizes[key_sizes >= 10].sum()),
        "heaviest": key_sizes.sort_values(ascending=False).head(5),
    }


def coverage(ours: pd.DataFrame, theirs: pd.DataFrame, key: list[str]) -> dict:
    cols = ["person_id"] + key
    o = ours.groupby(cols, dropna=False).size().rename("n_o")
    t = theirs.groupby(cols, dropna=False).size().rename("n_r")
    both = pd.concat([o, t], axis=1)
    common = both.dropna()
    return {
        "keys_ref": int(t.shape[0]), "keys_ours": int(o.shape[0]), "keys_common": int(common.shape[0]),
        "rows_matched": int(np.minimum(common["n_o"], common["n_r"]).sum()),
        "rows_ref": len(theirs), "rows_ours": len(ours),
    }


def unmatched(f: pd.DataFrame, other: pd.DataFrame, names: pd.Series, top: int = 15) -> dict:
    pairs = set(zip(other["person_id"], other["drug_concept_id"]))
    mask = np.array([(p, c) not in pairs for p, c in zip(f["person_id"], f["drug_concept_id"])])
    lost = f[mask]
    t = lost.groupby("drug_concept_id").size().sort_values(ascending=False).head(top)
    return {
        "rows": int(mask.sum()), "share": float(mask.mean()) if len(f) else 0.0,
        "concept_zero": int((lost["drug_concept_id"] == 0).sum()),
        "by_shape": lost["source_shape"].value_counts().to_dict(),
        "top": [(int(c), str(names.get(c, "?")), int(n)) for c, n in t.items()],
    }


def quantity_on_unique_pairs(ours: pd.DataFrame, theirs: pd.DataFrame, names: pd.Series) -> dict:
    key = ["person_id", "drug_concept_id", "start_dt", "end_dt"]
    o = ours.dropna(subset=["start_dt"]).groupby(key).filter(lambda g: len(g) == 1)
    t = theirs.dropna(subset=["start_dt"]).groupby(key).filter(lambda g: len(g) == 1)
    m = o.merge(t, on=key, suffixes=("_o", "_r"))
    if m.empty:
        return {"pairs": 0}
    qo, qr = m["quantity_o"], m["quantity_r"]
    both = qo.notna() & qr.notna()
    agree = both & np.isclose(qo, qr, rtol=1e-4, atol=1e-6)
    ratio = (qo[both & (qr != 0)] / qr[both & (qr != 0)]).replace([np.inf, -np.inf], np.nan).dropna()
    bad = m[both & ~agree]
    top_bad = bad.groupby("drug_concept_id").size().sort_values(ascending=False).head(10)
    return {
        "pairs": len(m), "both_filled": int(both.sum()), "agree": int(agree.sum()),
        "ours_missing": int((qo.isna() & qr.notna()).sum()), "ref_missing": int((qo.notna() & qr.isna()).sum()),
        "ratio_quantiles": ratio.quantile([.05, .25, .5, .75, .95]).round(4).to_dict() if len(ratio) else {},
        "top_bad": [(int(c), str(names.get(c, "?")), int(n)) for c, n in top_bad.items()],
        "examples": bad[["drug_concept_id", "quantity_o", "quantity_r"]].head(8).values.tolist(),
    }


def end_date_on_pairs(ours: pd.DataFrame, theirs: pd.DataFrame) -> pd.DataFrame:
    """Pairs with one row per side for the same patient, drug and start time:
    do the end dates agree, and if not, which side ends later? Grouped by the
    shape of OUR source value (itemid-like rows are INPUTEVENTS or CHARTEVENTS,
    text rows are PRESCRIPTIONS), which shows where the end-date convention
    differs."""
    key = ["person_id", "drug_concept_id", "start_dt"]
    o = ours.dropna(subset=["start_dt"]).groupby(key).filter(lambda g: len(g) == 1)
    t = theirs.dropna(subset=["start_dt"]).groupby(key).filter(lambda g: len(g) == 1)
    m = o.merge(t, on=key, suffixes=("_o", "_r"))
    if m.empty:
        return pd.DataFrame()
    delta = (m["end_d_o"] - m["end_d_r"]).dt.days
    verdict = np.select(
        [delta.isna(), delta == 0, delta < 0, delta > 0],
        ["end date missing", "same end date", "ours ends earlier", "ours ends later"], default="?")
    return pd.crosstab(m["source_shape_o"], pd.Series(verdict, index=m.index, name="end date"))


# ------------------------------------------------------------------ report ---

def pct(a, b) -> str:
    return f"{a} ({100 * a / b:.1f}%)" if b else "n/a"


def render(co, ct, covs, un_t, un_o, qty, ends=None) -> list[str]:
    L = ["# drug_exposure : investigation", "", "## 1. Composition", "",
         "| | Ours | Reference |", "|---|---|---|",
         f"| rows | {co['rows']} | {ct['rows']} |",
         f"| drug_concept_id = 0 | {co['concept_zero']} | {ct['concept_zero']} |",
         f"| distinct keys (patient, drug, start date, end date) | {co['distinct_keys']} | {ct['distinct_keys']} |",
         f"| rows in keys holding 10+ rows | {co['rows_in_keys_of_10_plus']} | {ct['rows_in_keys_of_10_plus']} |", "",
         "Rows per key (describe): ours " + str(co["rows_per_key"]) + " ; reference " + str(ct["rows_per_key"]), "",
         "Shape of drug_source_value (NDC = PRESCRIPTIONS, itemid-like = INPUTEVENTS or CHARTEVENTS, text = name).", "",
         "| Shape | Ours | Reference |", "|---|---|---|"]
    for s in sorted(set(co["shapes"]) | set(ct["shapes"])):
        L.append(f"| {s} | {co['shapes'].get(s, 0)} | {ct['shapes'].get(s, 0)} |")
    L += ["", "drug_type_concept_id: ours " + str(co["types"]) + " ; reference " + str(ct["types"]), "",
          "Most frequent drugs.", "", "| Ours | n | Reference | n |", "|---|---|---|---|"]
    for i in range(max(len(co["top"]), len(ct["top"]))):
        a = co["top"][i] if i < len(co["top"]) else ("", "", "")
        b = ct["top"][i] if i < len(ct["top"]) else ("", "", "")
        L.append(f"| {a[0]} {a[1]} | {a[2]} | {b[0]} {b[1]} | {b[2]} |")
    L += ["", "Heaviest keys (rows sharing one patient + drug + start/end date).", "",
          "Ours:", "```", co["heaviest"].to_string(), "```", "Reference:", "```", ct["heaviest"].to_string(), "```", ""]

    L += ["## 2. Coverage of the reference under five keys", "",
          "Distinct keys: how many reference keys exist on our side. Rows: sum over common keys of "
          "min(rows ours, rows reference), the way the comparator pairs them.", "",
          "| Key | Reference keys found | Our keys found in reference | Reference rows paired | Our rows paired |",
          "|---|---|---|---|---|"]
    for name, c in covs.items():
        L.append(f"| {name} | {pct(c['keys_common'], c['keys_ref'])} | {pct(c['keys_common'], c['keys_ours'])} | "
                 f"{pct(c['rows_matched'], c['rows_ref'])} | {pct(c['rows_matched'], c['rows_ours'])} |")
    L.append("")

    for title, u, side in [("3. Reference rows whose patient + drug never appears on our side", un_t, "reference"),
                           ("4. Our rows whose patient + drug never appears in the reference", un_o, "ours")]:
        L += [f"## {title}", "", f"{u['rows']} rows ({100 * u['share']:.1f}% of {side}); drug 0 among them: {u['concept_zero']}.", "",
              "By source shape: " + ", ".join(f"{k}: {v}" for k, v in u["by_shape"].items()), "",
              "| drug | n |", "|---|---|"] + [f"| {c} {n} | {k} |" for c, n, k in u["top"]] + [""]

    L += ["## 5. Quantity on unambiguous pairs", ""]
    if not qty.get("pairs"):
        L += ["No pair with exactly one row per side for the same patient, drug, start and end time.", ""]
    else:
        L += [f"{qty['pairs']} pairs; both quantities filled: {qty['both_filled']}; they agree: {pct(qty['agree'], qty['both_filled'])}.",
              f"Quantity missing on our side only: {qty['ours_missing']}; on the reference side only: {qty['ref_missing']}.",
              f"Ratio ours/reference over pairs with both quantities (5/25/50/75/95 %): {qty['ratio_quantiles']}", "",
              "Drugs with the most disagreements.", "", "| drug | n |", "|---|---|"]
        L += [f"| {c} {n} | {k} |" for c, n, k in qty["top_bad"]]
        L += ["", "Examples (drug, ours, reference): " + str(qty["examples"]), ""]
    if ends is not None and not ends.empty:
        L += ["## 6. End date on pairs with the same patient, drug and start time", "",
              "| Our source shape | " + " | ".join(str(c) for c in ends.columns) + " |",
              "|---|" + "---|" * len(ends.columns)]
        for idx, r in ends.iterrows():
            L.append(f"| {idx} | " + " | ".join(str(v) for v in r.values) + " |")
        L.append("")
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

    wanted = ["person_id", "drug_concept_id", "drug_exposure_start_date", "drug_exposure_end_date",
              "drug_exposure_start_datetime", "drug_exposure_end_datetime", "quantity",
              "drug_source_value", "drug_type_concept_id"]

    def read(session, schema):
        have = _get_columns(session, schema, "drug_exposure")
        cols = [c for c in wanted if c in have]
        return pd.read_sql(text(f"SELECT {', '.join(cols)} FROM {schema}.drug_exposure"), session.connection())

    with our_session_scope() as s:
        ours = read(s, a.our_schema)
        oconcept = pd.read_sql(text(f"SELECT concept_id, concept_name FROM {a.our_vocab_schema}.concept"), s.connection())
    with their_scope() as s:
        theirs = read(s, a.their_schema)
        tconcept = pd.read_sql(text(f"SELECT concept_id, concept_name FROM {their_vocab}.concept"), s.connection())

    ours = ours.merge(crosswalk, left_on="person_id", right_on="our_person_id", how="inner")
    ours["person_id"] = ours["their_person_id"]
    ours = ours.drop(columns=["our_person_id", "their_person_id"])
    theirs = theirs[theirs["person_id"].isin(crosswalk["their_person_id"])]
    names = pd.concat([tconcept, oconcept]).drop_duplicates("concept_id").set_index("concept_id")["concept_name"]

    ours, theirs = prepare(ours), prepare(theirs)
    covs = {name: coverage(ours, theirs, key) for name, key in KEYS.items()}
    report = render(composition(ours, names), composition(theirs, names), covs,
                    unmatched(theirs, ours, names), unmatched(ours, theirs, names),
                    quantity_on_unique_pairs(ours, theirs, names), end_date_on_pairs(ours, theirs))
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
