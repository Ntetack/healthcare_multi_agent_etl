"""
Compares our drug_exposure with the reference, restricted to the reference rows
whose drug_concept_id is NOT 0. Read-only, changes nothing.

Why: more than half of the reference rows carry concept 0, so any coverage
computed on the whole table mostly measures the reference's own gaps. Here the
question is only: for each reference row that has a real drug, what do we hold
for the same patient?

Each reference row falls in exactly one category, tested in this order:
  0a. no start date on the reference row, same drug found for the patient
  0b. no start date on the reference row, drug not found for the patient
  1.  same drug, same start date                          (reproduced)
  2.  same drug, other date                               (right drug, wrong day)
  3.  another real drug on the same start date            (concept disagreement)
  4.  only unmapped rows (concept 0 or empty) that day    (we hold the event, no drug)
  5.  patient present on our side, nothing that day, drug absent
  6.  patient absent from our drug_exposure

Also reported: the same figures by shape of the reference drug_source_value,
the main drug confusions in category 3, the drugs most often missing, coverage
under the five keys of investigate_drug_exposure.py (rows paired with the
min(rows ours, rows reference) rule of the comparator), and how many of our
rows sit on events the reference leaves at concept 0 (not evaluable).

Options narrowing the reference further (default: only "concept is not 0"):
  --drug-domain-only   keep only concepts of the Drug domain
  --require-start-date drop reference rows without a start date

Usage (same connection arguments as investigate_drug_exposure.py):
    python scripts/compare_drug_nonzero.py \
        --patients-csv data/raw/hospital_b/batch39/PATIENTS.csv \
        --our-source-column ROW_ID --their-source-column SUBJECT_ID \
        --their-db-host localhost --their-db-name mimic --their-schema omop \
        --their-db-user postgres --their-db-password ... \
        --our-vocab-schema cdm_vocab --their-vocab-schema omop \
        --output reports/mimic/drug_nonzero.md
Put it next to investigate_drug_exposure.py: it reuses its helpers.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from investigate_drug_exposure import KEYS, coverage, pct, prepare

CATEGORIES = [
    "0a. no start date, drug found for the patient",
    "0b. no start date, drug not found for the patient",
    "1. same drug, same start date",
    "2. same drug, other date",
    "3. another real drug, same start date",
    "4. only unmapped rows (0 or empty) that day",
    "5. patient present, nothing that day, drug absent",
    "6. patient absent from our drug_exposure",
]


# ----------------------------------------------------------- classification ---

def _in(left: pd.DataFrame, right: pd.DataFrame, cols: list[str]) -> np.ndarray:
    """True where the combination of `cols` on a row of `left` exists in `right`."""
    r = right.dropna(subset=cols)[cols].drop_duplicates()
    if r.empty:
        return np.zeros(len(left), dtype=bool)
    lk = pd.MultiIndex.from_frame(left[cols])
    return lk.isin(pd.MultiIndex.from_frame(r))


def classify(ref: pd.DataFrame, ours: pd.DataFrame) -> pd.Series:
    """Category (one of CATEGORIES) of every row of `ref`. Both frames come out of prepare()."""
    ours_real = ours[ours["drug_concept_id"] != 0]
    ours_zero = ours[ours["drug_concept_id"] == 0]
    has_start = ref["start_d"].notna().to_numpy()
    same_drug_date = _in(ref, ours_real, ["person_id", "drug_concept_id", "start_d"])
    same_drug_any = _in(ref, ours_real, ["person_id", "drug_concept_id"])
    other_drug_date = _in(ref, ours_real, ["person_id", "start_d"])
    zero_date = _in(ref, ours_zero, ["person_id", "start_d"])
    patient_present = ref["person_id"].isin(ours["person_id"]).to_numpy()
    cat = np.select(
        [~has_start & same_drug_any,
         ~has_start,
         same_drug_date,
         same_drug_any,
         other_drug_date,
         zero_date,
         patient_present],
        CATEGORIES[:7],
        default=CATEGORIES[7])
    return pd.Series(cat, index=ref.index, name="category")


def confusions(ref: pd.DataFrame, ours: pd.DataFrame, cat: pd.Series, names: pd.Series,
               domains: pd.Series, top: int = 25) -> list[tuple]:
    """For category 3: which of our drugs sits where the reference has another one."""
    sub = ref[cat == CATEGORIES[4]][["person_id", "start_d", "drug_concept_id"]].copy()
    sub["ref_row"] = sub.index
    o = ours[ours["drug_concept_id"] != 0][["person_id", "start_d", "drug_concept_id"]]
    m = sub.merge(o, on=["person_id", "start_d"], suffixes=("_ref", "_ours"))
    m = m[m["drug_concept_id_ref"] != m["drug_concept_id_ours"]]
    g = (m.groupby(["drug_concept_id_ref", "drug_concept_id_ours"])["ref_row"].nunique()
         .sort_values(ascending=False).head(top))
    return [(int(a), str(names.get(a, "?")), int(b), str(names.get(b, "?")), str(domains.get(b, "?")), int(n))
            for (a, b), n in g.items()]


def missing_drugs(ref: pd.DataFrame, cat: pd.Series, names: pd.Series, top: int = 20) -> list[tuple]:
    lost = ref[cat.isin(CATEGORIES[5:8] + CATEGORIES[1:2])]
    g = lost.groupby("drug_concept_id").size().sort_values(ascending=False).head(top)
    return [(int(c), str(names.get(c, "?")), int(n)) for c, n in g.items()]


def timed_agreement(ref: pd.DataFrame, ours: pd.DataFrame, cat: pd.Series) -> dict:
    """Among reproduced rows (category 1) that carry a start time on both sides:
    does the time of day agree?"""
    r = ref[(cat == CATEGORIES[2]) & ref["start_dt"].notna()]
    o = ours[ours["start_dt"].notna()]
    if r.empty or o.empty:
        return {"rows": 0, "same_time": 0}
    same = _in(r, o, ["person_id", "drug_concept_id", "start_dt"])
    return {"rows": len(r), "same_time": int(same.sum())}


def not_evaluable_ours(ours: pd.DataFrame, ref_all: pd.DataFrame) -> dict:
    """Our rows whose patient + start date coincides with a reference row left at concept 0."""
    zero_ref = ref_all[ref_all["drug_concept_id"] == 0]
    on_zero = _in(ours, zero_ref, ["person_id", "start_d"])
    on_real = _in(ours, ref_all[ref_all["drug_concept_id"] != 0], ["person_id", "start_d"])
    return {"ours": len(ours), "on_zero_event": int(on_zero.sum()),
            "on_zero_event_only": int((on_zero & ~on_real).sum()),
            "on_real_event": int(on_real.sum()),
            "elsewhere": int((~on_zero & ~on_real).sum())}


# ------------------------------------------------------------------ report ---

def render(ref_all, ref, ours, cat, conf, miss, timed, lost_ours, covs, names, filters) -> list[str]:
    n = len(ref)
    counts = cat.value_counts()
    L = ["# drug_exposure : reference rows with a real drug", "",
         f"Reference rows (matched patients): {len(ref_all)}. Retained: {n} "
         f"({100 * n / len(ref_all):.1f}%). Filters: {filters}.",
         f"Our rows (matched patients): {len(ours)}.", "",
         "## 1. What we hold for each retained reference row", "",
         "| Category | Rows | Share |", "|---|---|---|"]
    for c in CATEGORIES:
        L.append(f"| {c} | {counts.get(c, 0)} | {100 * counts.get(c, 0) / n:.1f}% |")
    reproduced = counts.get(CATEGORIES[2], 0)
    drug_ok = reproduced + counts.get(CATEGORIES[3], 0) + counts.get(CATEGORIES[0], 0)
    L += ["", f"Right drug and right day: {pct(int(reproduced), n)}. Right drug, any day: {pct(int(drug_ok), n)}.", ""]
    if timed["rows"]:
        L += [f"Among category 1 rows with a start time on both sides, the time of day agrees on "
              f"{pct(timed['same_time'], timed['rows'])}.", ""]

    L += ["## 2. By shape of the reference drug_source_value", "",
          "| Shape | " + " | ".join(c.split(".")[0] for c in CATEGORIES) + " | Total |",
          "|---|" + "---|" * (len(CATEGORIES) + 1)]
    tab = pd.crosstab(ref["source_shape"], cat).reindex(columns=CATEGORIES, fill_value=0)
    for idx, r in tab.iterrows():
        L.append(f"| {idx} | " + " | ".join(str(v) for v in r.values) + f" | {int(r.sum())} |")
    L += ["", "Categories are numbered as in section 1.", ""]

    L += ["## 3. Disagreements: another real drug on the same patient and day", "",
          "Pairs counted once per reference row. Look first for pairs where the two drugs are clearly different "
          "substances (a wrong mapping) versus the same substance at another level (ingredient, clinical drug, brand).", "",
          "| Reference drug | Our drug | Domain of ours | Rows |", "|---|---|---|---|"]
    for a, an, b, bn, dom, k in conf:
        L.append(f"| {a} {an} | {b} {bn} | {dom} | {k} |")
    L += ["", "## 4. Reference drugs we most often lack altogether", "",
          "Categories 0b, 5 and 6 (and 4: only unmapped rows that day).", "",
          "| Drug | Rows |", "|---|---|"]
    L += [f"| {c} {nm} | {k} |" for c, nm, k in miss]

    L += ["", "## 5. Coverage under the five keys, retained reference only", "",
          "Rows paired with the comparator's rule, min(rows ours, rows reference) per common key.", "",
          "| Key | Reference rows paired | Our rows paired |", "|---|---|---|"]
    for name, c in covs.items():
        L.append(f"| {name} | {pct(c['rows_matched'], c['rows_ref'])} | {pct(c['rows_matched'], c['rows_ours'])} |")

    L += ["", "## 6. Our rows outside the evaluation", "",
          "| | Rows |", "|---|---|",
          f"| all our rows | {lost_ours['ours']} |",
          f"| on a patient + day where the reference holds a real drug | {lost_ours['on_real_event']} |",
          f"| on a patient + day where the reference holds only concept 0 | {lost_ours['on_zero_event_only']} |",
          f"| on a patient + day absent from the reference | {lost_ours['elsewhere']} |", "",
          "The second line is the part of our output that this comparison cannot judge, because the "
          "reference never named the drug there.", ""]
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
    p.add_argument("--drug-domain-only", action="store_true")
    p.add_argument("--require-start-date", action="store_true")
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
        oconcept = pd.read_sql(text(f"SELECT concept_id, concept_name, domain_id FROM {a.our_vocab_schema}.concept"), s.connection())
    with their_scope() as s:
        theirs = read(s, a.their_schema)
        tconcept = pd.read_sql(text(f"SELECT concept_id, concept_name, domain_id FROM {their_vocab}.concept"), s.connection())

    ours = ours.merge(crosswalk, left_on="person_id", right_on="our_person_id", how="inner")
    ours["person_id"] = ours["their_person_id"]
    ours = ours.drop(columns=["our_person_id", "their_person_id"])
    theirs = theirs[theirs["person_id"].isin(crosswalk["their_person_id"])]
    allc = pd.concat([tconcept, oconcept]).drop_duplicates("concept_id")
    names = allc.set_index("concept_id")["concept_name"]
    domains = allc.set_index("concept_id")["domain_id"]
    drug_ids = set(allc.loc[allc["domain_id"] == "Drug", "concept_id"])

    ours, theirs = prepare(ours), prepare(theirs)
    ref = theirs[theirs["drug_concept_id"] != 0]
    filters = ["drug_concept_id <> 0"]
    if a.drug_domain_only:
        ref = ref[ref["drug_concept_id"].isin(drug_ids)]
        filters.append("Drug domain")
    if a.require_start_date:
        ref = ref[ref["start_d"].notna()]
        filters.append("start date present")

    cat = classify(ref, ours)
    covs = {name: coverage(ours, ref, key) for name, key in KEYS.items()}
    report = render(theirs, ref, ours, cat, confusions(ref, ours, cat, names, domains),
                    missing_drugs(ref, cat, names), timed_agreement(ref, ours, cat),
                    not_evaluable_ours(ours, theirs), covs, names, ", ".join(filters))
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    detail = out.with_suffix(".rows.csv")
    ref.assign(category=cat, concept_name=ref["drug_concept_id"].map(names)).drop(
        columns=["start_dt", "end_dt"], errors="ignore").to_csv(detail, index=False)
    print(f"written: {out}\nwritten: {detail}")


if __name__ == "__main__":
    main()
