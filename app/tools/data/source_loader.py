"""
Source-agnostic loaders.

Goal: integrating a new source (MIMIC, Synthea, a new hospital extract)
must never require new ingestion code - only a new entry in
config/metadata/source_metadata.yaml. These readers make no assumption
about column names or clinical semantics; they only know how to turn a
given *format* into a flat pandas DataFrame. All values are kept as
strings on purpose (staging is STRING/TEXT - see architecture doc, 11.).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterator

import pandas as pd

from app.tools.data.fhir_code_systems import known_code_systems
from app.tools.data.fhir_flattener import build_fhir_tables


def load_csv(path: str | Path) -> pd.DataFrame:
    """Reads a single CSV/TSV file. Batch folders containing several
    distinct table files (e.g. PATIENTS.csv, DIAGNOSES.csv, LABEVENTS.csv)
    are handled one file at a time by load_source_tables() below - each
    file is a different clinical entity, never concatenated together."""
    return _read_csv_with_provenance(Path(path))


def _read_csv_with_provenance(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["_source_file"] = path.name
    return df


def load_parquet(path: str | Path) -> pd.DataFrame:
    return _read_parquet_with_provenance(Path(path))


def _read_parquet_with_provenance(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path).astype(str)
    df["_source_file"] = path.name
    return df


def load_ndjson_fhir(path: str | Path) -> pd.DataFrame:
    """LONG-FORMAT reader, kept for load_source('fhir', ...) only. Batch
    discovery (load_source_tables) does NOT use it: it builds WIDE tables,
    one per resource type, with FHIR paths as columns - see
    app/tools/data/fhir_flattener.py. This function flattens FHIR
    resources into a generic long-format table: one row
    per (resource_type, resource_id, field_path, value). Handles BOTH
    real layouts seen in the wild:
      - True bulk-data NDJSON: one compact JSON resource per line.
      - Synthea's DEFAULT FHIR export: one pretty-printed FHIR Bundle
        JSON document per file (per patient), wrapping many resources in
        an "entry" array - NOT one-resource-per-line.
    The Profiling/Mapping agents work off this shape rather than a
    resource-type-specific parser, so any FHIR resource type is supported
    without new code, regardless of which of the two layouts a given
    export uses."""
    p = Path(path)
    files = [p] if p.is_file() else sorted(p.glob("*.ndjson")) + sorted(p.glob("*.json"))

    rows: list[dict] = []
    for f in files:
        for resource in _read_fhir_resources(f):
            rows.extend(_flatten_fhir_resource(resource))
    return pd.DataFrame(rows, dtype=str)


def _read_fhir_resources(path: Path) -> Iterator[dict]:
    """Yields individual FHIR resources from a file, auto-detecting
    whether it's true NDJSON or a single pretty-printed Bundle/resource
    document."""
    content = path.read_text(encoding="utf-8")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        # Not a single valid JSON document -> assume true NDJSON,
        # one compact resource per line.
        for line in content.splitlines():
            line = line.strip()
            if line:
                yield json.loads(line)
        return

    # Whole file parsed as one JSON document.
    if isinstance(parsed, dict) and parsed.get("resourceType") == "Bundle":
        for entry in parsed.get("entry", []):
            if "resource" in entry:
                yield entry["resource"]
    elif isinstance(parsed, list):
        yield from parsed
    else:
        # A single standalone resource.
        yield parsed


def _flatten_fhir_resource(resource: dict) -> Iterator[dict]:
    resource_type = resource.get("resourceType", "Unknown")
    resource_id = resource.get("id", "")

    def walk(obj, prefix: str):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield from walk(v, f"{prefix}.{k}" if prefix else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from walk(v, f"{prefix}[{i}]")
        else:
            yield {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "field_path": prefix,
                "value": "" if obj is None else str(obj),
            }

    yield from walk(resource, "")


LOADERS = {
    "csv": load_csv,
    "parquet": load_parquet,
    "fhir": load_ndjson_fhir,
}

_EXTENSIONS = {
    "csv": (".csv", ".tsv"),
    "parquet": (".parquet",),
    "fhir": (".ndjson", ".json"),
}


def load_source(source_format: str, path: str | Path) -> pd.DataFrame:
    """Dispatches to the right generic single-file loader based on the
    `format` field declared in source_metadata.yaml. For a batch FOLDER
    containing multiple distinct tables (PATIENTS.csv, DIAGNOSES.csv, ...
    or person.csv, condition_occurrence.csv, ...), use
    load_source_tables() instead - this function reads exactly one file
    (or, for the 'fhir' format, one file/one folder of same-resource NDJSON or Bundle files)."""
    try:
        loader = LOADERS[source_format]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported source format '{source_format}'. "
            f"Supported: {list(LOADERS)}"
        ) from exc
    return loader(path)


def load_source_tables(source_format: str, folder_path: str | Path) -> dict[str, pd.DataFrame]:
    """Reads a batch folder as a set of DISTINCT tables - the real shape
    of a hospital export (MIMIC-style: PATIENTS, ADMISSIONS, DIAGNOSES,
    LABEVENTS, ...; or an OMOP-native export: person, visit_occurrence,
    condition_occurrence, ...; or a Synthea FHIR NDJSON dump: one
    resource type per file). Each file becomes its own table, keyed by a
    name derived from the file (or, for FHIR, the resource type found
    inside it) - tables representing different clinical entities are
    NEVER concatenated together, only files of the SAME table (rare, but
    handled) are merged.

    This is what the Profiling Agent calls for automatic, structure-
    agnostic discovery: it does not need to know in advance which tables
    a given source contains."""
    folder = Path(folder_path)
    if not folder.is_dir():
        raise NotADirectoryError(f"'{folder}' is not a batch folder")

    extensions = _EXTENSIONS.get(source_format, ())
    files = sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in extensions)
    if not files:
        raise FileNotFoundError(f"No '{source_format}' files found under '{folder}'")

    if source_format == "fhir":
        return _load_fhir_tables(files)

    # csv / parquet: one file = one table, keyed by its filename (without
    # extension). If the same table legitimately spans several files
    # (e.g. DIAGNOSES_part1.csv, DIAGNOSES_part2.csv), they share a table
    # name after stripping a trailing "_partN"/"_NN" suffix and get
    # concatenated; distinct table names are always kept separate.
    tables: dict[str, list[pd.DataFrame]] = {}
    loader = LOADERS[source_format]
    for f in files:
        table_name = _infer_table_name(f.stem)
        tables.setdefault(table_name, []).append(loader(f))

    return {name: pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]
            for name, dfs in tables.items()}


def _infer_table_name(file_stem: str) -> str:
    """Strips a trailing part/chunk suffix like '_part1' or '_00' so that
    a table deliberately split across multiple files is recognized as one
    table, without merging genuinely different tables (e.g. 'DIAGNOSES'
    and 'DIAGNOSES_ICD' stay distinct - only numeric/partN suffixes are
    stripped)."""
    return re.sub(r"_(part\d+|\d+)$", "", file_stem, flags=re.IGNORECASE)


def _load_fhir_tables(files: list[Path]) -> dict[str, pd.DataFrame]:
    """Builds one WIDE table per FHIR resource type, across all files in
    the batch. A Synthea export may put one resource type per file (e.g.
    Condition.ndjson), bundle several types together per file, or hold one
    Bundle per patient; all layouts are handled the same way because the
    grouping uses the resourceType found inside each resource.

    Columns are FHIR element paths (`code.code`, `subject.id`,
    `onsetDateTime`...), values are strings and a missing value is an empty
    string, exactly like a table read from CSV - so every downstream agent
    works on it unchanged. When a concept carries several codings, the one
    whose coding system the framework can search is kept (see
    app/tools/data/fhir_code_systems.py). The flattening rules are
    documented in app/tools/data/fhir_flattener.py."""
    return build_fhir_tables(
        ((f.name, _read_fhir_resources(f)) for f in files),
        known_systems=known_code_systems(),
    )
