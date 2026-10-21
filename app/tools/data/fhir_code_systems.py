"""
FHIR code systems: what a FHIR source says about its own codes.

A FHIR code always travels with the URI of its coding system, so the
vocabulary of a coded field does not have to be declared by hand as it is
for a CSV export. This module reads a reference file written by a human
(app/config/reference/fhir_code_systems.yaml) that maps those URIs to the
`standard` tokens of the Mapping Agent, and derives from it the coded-field
declarations of a FHIR batch.

A derived declaration has the form

    standard: "from_system:<column holding the system URI>"

for example `from_system:code.system`. It means that the vocabulary is
decided for each value by the system found next to it, instead of being
fixed for the whole column: a single column can mix SNOMED and LOINC codes
and each one is searched in its own vocabulary.

Only the element that identifies the clinical event gets a derived
declaration (event_code_paths in the reference file). A declaration written
by hand in the batch metadata always takes precedence.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

DEFAULT_REFERENCE_PATH = Path(__file__).resolve().parents[2] / "config" / "reference" / "fhir_code_systems.yaml"

FROM_SYSTEM_PREFIX = "from_system:"

# The Mapping Agent adds up to 18 characters to the name of a coded field
# (`_source_concept_id`) and PostgreSQL identifiers stop at 63 characters.
MAX_CODED_FIELD_LENGTH = 45

# Separates the system from the code in the key of a (system, code) pair.
# A control character, so it can never occur in a system URI or a code.
SYSTEM_CODE_SEPARATOR = "\x1f"


def load_fhir_reference(path: str | Path = DEFAULT_REFERENCE_PATH) -> dict[str, Any]:
    """Reads the reference file. Raises if it is missing, because a FHIR
    batch cannot be mapped without it."""
    reference_path = Path(path)
    if not reference_path.exists():
        raise FileNotFoundError(f"FHIR reference file not found: '{reference_path}'")
    with open(reference_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {
        "code_systems": {str(k).strip(): v for k, v in (data.get("code_systems") or {}).items()},
        "event_code_paths": {str(k).lower(): list(v) for k, v in (data.get("event_code_paths") or {}).items()},
    }


def known_code_systems(path: str | Path = DEFAULT_REFERENCE_PATH) -> set[str]:
    """The coding systems the framework can search. An empty set when the
    reference file is missing, which only costs the preference given to a
    known system when a concept carries several codings."""
    try:
        return set(load_fhir_reference(path)["code_systems"])
    except FileNotFoundError:
        return set()


def parse_from_system(standard: str | None) -> str | None:
    """Returns the column holding the system URI when `standard` is a
    `from_system:<column>` declaration, and None for any other value."""
    if isinstance(standard, str) and standard.startswith(FROM_SYSTEM_PREFIX):
        column = standard[len(FROM_SYSTEM_PREFIX):].strip()
        return column or None
    return None


def standard_for_system(system: str | None, code_systems: dict[str, str]) -> str | None:
    """The `standard` token of a system URI, or None when the system is
    unknown, which leaves the value unresolved instead of guessing."""
    if not system:
        return None
    return code_systems.get(system.strip())


def build_system_code_keys(systems: pd.Series, codes: pd.Series) -> pd.Series:
    """One key `<system><separator><code>` per row, so that a coded column
    can be resolved value by value in the vocabulary of its own system.
    A row whose code is blank gets no key (NaN): there is nothing to look
    up, and it must not appear as a value to resolve."""
    codes = codes.astype(str)
    keys = systems.astype(str) + SYSTEM_CODE_SEPARATOR + codes
    return keys.where(codes.str.strip() != "")


def split_system_code_key(key: str) -> tuple[str, str]:
    """Inverse of build_system_code_keys: (system, code)."""
    system, _, code = key.partition(SYSTEM_CODE_SEPARATOR)
    return system, code


def derive_fhir_declarations(
    tables: dict[str, pd.DataFrame],
    batch_cfg: dict,
    reference: dict[str, Any] | None = None,
) -> tuple[dict, list[dict]]:
    """Returns a copy of `batch_cfg` completed with the coded-field
    declarations derived from the systems found in the data, together with
    a log of what was derived or skipped. `batch_cfg` itself is not
    modified.

    A field is derived when its table has an event code path, the columns
    `<path>.code` and `<path>.system` both exist, at least one system
    found in the data is known, no declaration was written by hand for it,
    and its name is short enough for the Mapping Agent to enrich."""
    reference = reference or load_fhir_reference()
    code_systems = reference["code_systems"]
    event_paths = reference["event_code_paths"]

    result = copy.deepcopy(batch_cfg)
    declared_tables = result.setdefault("tables", {})
    log: list[dict] = []

    for table_name, df in tables.items():
        for path in event_paths.get(table_name.lower(), []):
            code_column, system_column = f"{path}.code", f"{path}.system"
            if code_column not in df.columns or system_column not in df.columns:
                continue

            entry: dict[str, Any] = {"table": table_name, "field": code_column, "system_field": system_column}
            found = sorted({s for s in df[system_column].astype(str) if s})
            entry["systems_found"] = found
            entry["standards"] = sorted({code_systems[s] for s in found if s in code_systems})
            entry["unsupported_systems"] = [s for s in found if s not in code_systems]

            table_key = table_name.lower()
            if declared_tables.get(table_key, {}).get(code_column) is not None:
                entry["status"] = "kept the declaration written by hand"
            elif not entry["standards"]:
                entry["status"] = "skipped: no known coding system in the data"
            elif len(code_column) > MAX_CODED_FIELD_LENGTH:
                entry["status"] = f"skipped: field name longer than {MAX_CODED_FIELD_LENGTH} characters"
            else:
                declared_tables.setdefault(table_key, {})[code_column] = f"{FROM_SYSTEM_PREFIX}{system_column}"
                entry["status"] = "derived"
            log.append(entry)

    return result, log
