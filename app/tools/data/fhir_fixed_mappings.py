"""
Shared curated mappings for the value sets that FHIR itself defines (the
race and ethnicity categories of US Core, the class of an encounter...).

A FHIR source does not need a file of its own for these: the categories are
the same everywhere. app/config/reference/fhir_fixed_mappings.yaml lists, for
each target field, where the value is found in a FHIR batch and which CSV of
app/config/reference/fhir_mappings/ turns it into an OMOP concept. This module
adds to a batch's `fixed_value_mappings` the entries whose source column
exists in the batch, so the rest of the pipeline treats them exactly like a
curated mapping declared by hand.

The `mapping_file` of a derived entry is an ABSOLUTE path. The function that
loads a curated file joins `mapping_file` to the folder of the source, and an
absolute path wins over that folder, so nothing else has to change.

A declaration written by hand in the batch metadata for the same target field
always takes precedence, which lets a source use its own file.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

_REFERENCE_DIR = Path(__file__).resolve().parents[2] / "config" / "reference"
DEFAULT_REFERENCE_PATH = _REFERENCE_DIR / "fhir_fixed_mappings.yaml"
MAPPING_FOLDER = _REFERENCE_DIR / "fhir_mappings"


def load_fhir_fixed_mapping_reference(path: str | Path = DEFAULT_REFERENCE_PATH) -> dict[str, dict[str, dict]]:
    """Reads the reference file: {target_table: {target_field: spec}}.
    Raises if it is missing, because a FHIR batch cannot be mapped without it."""
    reference_path = Path(path)
    if not reference_path.exists():
        raise FileNotFoundError(f"FHIR fixed mapping reference not found: '{reference_path}'")
    with open(reference_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("fixed_value_mappings") or {}


def _distinct_values(series: pd.Series) -> list[str]:
    return sorted({v for v in series.astype(str) if v.strip()})


def _covered_values(mapping_file: Path, key_column: str) -> set[str]:
    table = pd.read_csv(mapping_file, dtype=str)
    columns = {c.lower(): c for c in table.columns}
    column = columns.get(key_column.lower())
    if column is None:
        return set()
    return {v.strip().upper() for v in table[column].dropna()}


def derive_fhir_fixed_mappings(
    tables: dict[str, pd.DataFrame],
    batch_cfg: dict,
    reference: dict[str, dict[str, dict]] | None = None,
    mapping_folder: str | Path = MAPPING_FOLDER,
) -> tuple[dict, list[dict]]:
    """Returns a copy of `batch_cfg` whose `fixed_value_mappings` is
    completed with the shared FHIR mappings that apply to this batch, and a
    log of what was derived or skipped. `batch_cfg` itself is not modified.

    An entry is derived when its source table and column exist in the batch,
    the column holds at least one value, its CSV exists, and no declaration
    was written by hand for the same target field. The log lists, for each
    entry, the values found in the data and those the CSV does not cover, so
    that a value left unresolved is visible instead of silent."""
    reference = reference if reference is not None else load_fhir_fixed_mapping_reference()
    folder = Path(mapping_folder)

    result = copy.deepcopy(batch_cfg)
    declared = result.setdefault("fixed_value_mappings", {})
    actual_table_names = {name.lower(): name for name in tables}
    log: list[dict] = []

    for target_table, fields in reference.items():
        for target_field, spec in fields.items():
            entry: dict[str, Any] = {
                "target_table": target_table, "target_field": target_field,
                "source_table": spec["source_table"], "source_field": spec["source_field"],
            }
            log.append(entry)

            if declared.get(target_table, {}).get(target_field) is not None:
                entry["status"] = "kept the declaration written by hand"
                continue

            actual_name = actual_table_names.get(spec["source_table"].lower())
            df = tables.get(actual_name) if actual_name else None
            if df is None or spec["source_field"] not in df.columns:
                entry["status"] = "skipped: source column not present in this batch"
                continue

            values = _distinct_values(df[spec["source_field"]])
            if not values:
                entry["status"] = "skipped: the source column holds no value"
                continue

            mapping_file = folder / spec["mapping_file"]
            if not mapping_file.exists():
                entry["status"] = f"skipped: reference file '{spec['mapping_file']}' is missing"
                continue

            key_column = spec.get("source_field_column", spec["source_field"])
            covered = _covered_values(mapping_file, key_column)
            entry["values_found"] = values
            entry["values_not_covered"] = [v for v in values if v.strip().upper() not in covered]

            declared.setdefault(target_table, {})[target_field] = {
                **spec,
                "source_table": actual_name,
                "mapping_file": str(mapping_file),
            }
            entry["status"] = "derived"

    return result, log
