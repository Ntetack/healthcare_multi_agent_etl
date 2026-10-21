"""
Checks, BEFORE any pipeline run, that a CSV export and a FHIR export of the
same Synthea run describe the same population.

A comparison of the OMOP data built from the two formats only means something
if both formats came from the same simulated patients. This script compares
the two exports at the source level:

  1. The patients: the ids of patients.csv against the ids of the Patient
     resources. A difference stops the comparison: the two exports do not
     come from the same run (different seed or different run).
  2. The number of records of each entity (conditions, encounters,
     medications...) against the number of the matching FHIR resources. A
     difference here is not an error, it is something to explain before the
     OMOP data is compared. Observations are counted twice, with and without
     the components of panels, because Synthea writes each component of a
     blood pressure panel as its own row in the CSV export.

Usage (from the project root):
    python scripts/check_dual_export.py --csv-dir <synthea output>/csv \\
                                        --fhir-dir <synthea output>/fhir

With --observations-detail the observations are also compared code by code, to
show which codes carry a difference that replacing panels by their components
does not explain. With --ignore-codes the rows of the CSV export that have one
of the given codes are left out of the observation counts, which is how a known,
explained difference is set aside to check that nothing else differs.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.data.source_loader import load_source_tables  # noqa: E402

# CSV file -> FHIR tables whose rows it should match. Observations are
# handled separately because of the panels.
ENTITY_PAIRS = [
    ("conditions.csv", "Condition"),
    ("encounters.csv", "Encounter"),
    ("medications.csv", "MedicationRequest"),
    ("immunizations.csv", "Immunization"),
    ("procedures.csv", "Procedure"),
    ("allergies.csv", "AllergyIntolerance"),
]
SAMPLE_SIZE = 5


def read_csv_rows(csv_dir: Path, file_name: str) -> pd.DataFrame | None:
    path = csv_dir / file_name
    if not path.exists():
        return None
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def read_observations(csv_dir: Path, ignore_codes: tuple[str, ...] = ()) -> tuple[pd.DataFrame | None, int]:
    """The rows of observations.csv without those whose CODE is in
    `ignore_codes`, and how many rows were left out."""
    observations = read_csv_rows(csv_dir, "observations.csv")
    if observations is None:
        return None, 0
    if ignore_codes and "CODE" in observations.columns:
        ignored = observations["CODE"].isin(ignore_codes)
        return observations[~ignored].reset_index(drop=True), int(ignored.sum())
    return observations, 0


def compare_patients(csv_ids: set[str], fhir_ids: set[str]) -> dict:
    """The patient ids found in only one of the two exports."""
    return {
        "csv": len(csv_ids),
        "fhir": len(fhir_ids),
        "only_in_csv": sorted(csv_ids - fhir_ids),
        "only_in_fhir": sorted(fhir_ids - csv_ids),
        "same": csv_ids == fhir_ids,
    }


def count_entities(
    csv_dir: Path, fhir_tables: dict[str, pd.DataFrame], ignore_codes: tuple[str, ...] = ()
) -> list[dict]:
    """One row per entity: the CSV count, the FHIR count and their difference.
    A side that does not exist (no such CSV file, no such resource type) is
    reported as None instead of 0, so a missing file is not mistaken for an
    empty one."""
    rows = []
    for file_name, table in ENTITY_PAIRS:
        csv = read_csv_rows(csv_dir, file_name)
        csv_count = None if csv is None else len(csv)
        fhir_count = len(fhir_tables[table]) if table in fhir_tables else None
        rows.append({"entity": f"{file_name} / {table}", "csv": csv_count, "fhir": fhir_count})

    observations, _ = read_observations(csv_dir, ignore_codes)
    csv_count = None if observations is None else len(observations)
    all_rows = len(fhir_tables["Observation"]) if "Observation" in fhir_tables else None
    rows.append({"entity": "observations.csv / Observation (all rows)", "csv": csv_count, "fhir": all_rows})
    if all_rows is not None:
        # A panel is an observation that has components. Synthea writes each
        # component as a row of the CSV export, and not the panel itself.
        components = fhir_tables.get("Observation_component")
        panels = components["parent.id"].nunique() if components is not None and len(components) else 0
        n_components = 0 if components is None else len(components)
        rows.append({
            "entity": "observations.csv / Observation without its panels, plus components",
            "csv": csv_count, "fhir": all_rows - panels + n_components,
        })
    for row in rows:
        row["difference"] = None if row["csv"] is None or row["fhir"] is None else row["csv"] - row["fhir"]
    return rows


def compare_observation_codes(csv_observations: pd.DataFrame, fhir_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """For each observation code: the rows of the CSV export, and the rows of
    the FHIR export split into standalone observations, components of panels
    and panels themselves. `unexplained` is what the CSV holds beyond the
    standalone observations and the components, which is the rule used for the
    comparison; `unexplained_if_panels_counted` shows what remains if the CSV
    export also holds one row for each panel."""
    observation = fhir_tables.get("Observation")
    components = fhir_tables.get("Observation_component")
    if observation is None or "CODE" not in csv_observations.columns:
        return pd.DataFrame()

    panel_ids = set(components["parent.id"]) if components is not None and len(components) else set()
    is_panel = observation["id"].isin(panel_ids)
    standalone = observation.loc[~is_panel, "code.code"].value_counts()
    panels = observation.loc[is_panel, "code.code"].value_counts()
    component_counts = components["code.code"].value_counts() if components is not None and len(components) else pd.Series(dtype=int)

    csv_counts = csv_observations["CODE"].value_counts()
    descriptions = {}
    if "DESCRIPTION" in csv_observations.columns:
        descriptions = csv_observations.drop_duplicates("CODE").set_index("CODE")["DESCRIPTION"].to_dict()

    table = pd.DataFrame({
        "csv": csv_counts, "fhir_standalone": standalone,
        "fhir_components": component_counts, "fhir_panels": panels,
    }).fillna(0).astype(int)
    table.index.name = "code"
    table["description"] = [descriptions.get(code, "") for code in table.index]
    table["unexplained"] = table["csv"] - table["fhir_standalone"] - table["fhir_components"]
    table["unexplained_if_panels_counted"] = table["unexplained"] - table["fhir_panels"]
    return table.reset_index()


def observation_detail_lines(detail: pd.DataFrame, top: int) -> list[str]:
    """Markdown for the code-by-code comparison: a summary, then the codes
    with the largest remaining difference."""
    lines = ["", "## Observations, code by code", ""]
    if detail.empty:
        return lines + ["Not available: observations.csv has no CODE column, or there is no Observation resource."]

    different = detail[detail["unexplained"] != 0]
    lines.append(f"- codes in either export: {len(detail)}; codes whose counts differ: {len(different)}")
    lines.append(f"- rows of the CSV beyond standalone observations and components: {int(detail['unexplained'].sum()):+d}")
    lines.append(
        f"- the same, if the CSV also held one row for each panel ({int(detail['fhir_panels'].sum())} panels): "
        f"{int(detail['unexplained_if_panels_counted'].sum()):+d}"
    )
    if different.empty:
        return lines + ["", "Every code has the same count in both exports."]

    ranked = different.reindex(different["unexplained"].abs().sort_values(ascending=False).index).head(top)
    lines += ["", f"Codes with the largest difference (top {len(ranked)}):", "",
              "| Code | Description | CSV | FHIR standalone | FHIR components | FHIR panels | Difference |",
              "|---|---|---|---|---|---|---|"]
    for row in ranked.itertuples():
        description = str(row.description).replace("|", "/")[:50]
        lines.append(
            f"| {row.code} | {description} | {row.csv} | {row.fhir_standalone} | "
            f"{row.fhir_components} | {row.fhir_panels} | {row.unexplained:+d} |"
        )
    return lines


def build_report(
    csv_dir: Path, fhir_dir: Path, observations_detail: bool = False, top: int = 15,
    ignore_codes: tuple[str, ...] = (),
) -> tuple[list[str], bool]:
    """The report as lines of Markdown, and whether the two exports describe
    the same patients."""
    patients_csv = read_csv_rows(csv_dir, "patients.csv")
    if patients_csv is None or "Id" not in patients_csv.columns:
        raise FileNotFoundError(f"'{csv_dir / 'patients.csv'}' with an 'Id' column is required")
    fhir_tables = load_source_tables("fhir", fhir_dir)
    if "Patient" not in fhir_tables:
        raise ValueError(f"No Patient resource found under '{fhir_dir}'")

    patients = compare_patients(set(patients_csv["Id"]), set(fhir_tables["Patient"]["id"]))
    lines = ["# CSV and FHIR exports: source-level comparison", "", "## Patients", ""]
    lines.append(f"- patients.csv: {patients['csv']} | Patient resources: {patients['fhir']}")
    if patients["same"]:
        lines.append("- The two exports describe the same patients.")
    else:
        lines.append("- **The two exports do NOT describe the same patients.**")
        if patients["only_in_csv"]:
            lines.append(f"  - only in the CSV export ({len(patients['only_in_csv'])}): {patients['only_in_csv'][:SAMPLE_SIZE]}")
        if patients["only_in_fhir"]:
            lines.append(f"  - only in the FHIR export ({len(patients['only_in_fhir'])}): {patients['only_in_fhir'][:SAMPLE_SIZE]}")

    lines += ["", "## Records per entity", "", "| Entity | CSV | FHIR | Difference |", "|---|---|---|---|"]
    for row in count_entities(csv_dir, fhir_tables, ignore_codes):
        csv = "missing" if row["csv"] is None else row["csv"]
        fhir = "missing" if row["fhir"] is None else row["fhir"]
        diff = "n/a" if row["difference"] is None else (f"{row['difference']:+d}" if row["difference"] else "0")
        lines.append(f"| {row['entity']} | {csv} | {fhir} | {diff} |")
    _, n_ignored = read_observations(csv_dir, ignore_codes)
    if ignore_codes:
        lines += ["", f"Rows of observations.csv left out of the observation counts because their code is in "
                      f"{list(ignore_codes)}: {n_ignored}."]
    lines += [
        "", "A non-zero difference is not an error: explain it before comparing the OMOP data.",
    ]
    if observations_detail:
        csv_observations, _ = read_observations(csv_dir, ignore_codes)
        if csv_observations is None:
            lines += ["", "## Observations, code by code", "", "Not available: observations.csv is missing."]
        else:
            lines += observation_detail_lines(compare_observation_codes(csv_observations, fhir_tables), top)
    return lines, patients["same"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv-dir", required=True, type=Path)
    parser.add_argument("--fhir-dir", required=True, type=Path)
    parser.add_argument("--observations-detail", action="store_true",
                        help="Also compare the observations code by code")
    parser.add_argument("--top", type=int, default=15, help="Number of codes shown by --observations-detail")
    parser.add_argument("--ignore-codes", default="",
                        help="Comma-separated observation codes of the CSV export to leave out, for example DALY,QALY,QOLS")
    args = parser.parse_args()
    ignore_codes = tuple(code.strip() for code in args.ignore_codes.split(",") if code.strip())
    lines, same_patients = build_report(args.csv_dir, args.fhir_dir, args.observations_detail, args.top, ignore_codes)
    print("\n".join(lines))
    return 0 if same_patients else 1


if __name__ == "__main__":
    raise SystemExit(main())
