"""
Per-BATCH metadata loading.

Metadata lives INSIDE each batch folder, not at the source level -
a source's schema can drift between batches (a hospital changing its
export format over time), so a source-level file would silently go
stale. Each new batch is fully self-describing:

    data/raw/<source_name>/<batch_folder>/metadata.yaml
    data/raw/<source_name>/<batch_folder>/<table files...>

Onboarding a new source is a filesystem operation only: create
data/raw/<source_name>/ and drop the first dated batch folder in it,
with its own metadata.yaml. No central file to edit, no code change.
The source_name folder itself carries no metadata - it's read only to
list/detect batch subfolders (see app/tools/data/folder_watcher.py).

EXACTLY TWO canonical YAML shapes - never a per-source/per-vendor
variant, to keep the framework itself unmodified regardless of how many
sources it onboards:

  CSV / Parquet sources - keyed by file:
    format: csv
    files:
      conditions.csv:
        CODE:
          standard: SNOMED

  FHIR sources - keyed by resource type:
    format: fhir
    resources:
      Condition:
        code:
          standard: SNOMED

Both are normalized here into the same internal `tables` structure -
{table_name: {field_name: standard}} - so every downstream consumer
(ProfilingAgent, MappingAgent) works off one shape and never needs to
know which YAML flavor was written.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

DATA_ROOT = Path(os.getenv("DATA_ROOT", "data/raw"))
BATCH_METADATA_FILENAME = "metadata.yaml"

# Accepted spellings that don't match the OMOP vocabulary_id used
# elsewhere (e.g. app/tools/mapping/semantic/semantic_mapper.py) are
# normalized here, once, so no other module needs to know about aliases.
STANDARD_ALIASES = {
    "SNOMED-CT": "SNOMED",
    "SNOMEDCT": "SNOMED",
    "ICD-10": "ICD10",
    "ICD-10-CM": "ICD10",
}


def _normalize_standard(standard: str | None) -> str | None:
    if not standard:
        return standard
    return STANDARD_ALIASES.get(standard.upper(), standard)


def _strip_extension(key: str) -> str:
    """No-op for FHIR resource-type keys (no extension); strips '.csv' /
    '.parquet' from file-based keys - one function handles both shapes."""
    return Path(key).stem


def source_root_path(source_name: str) -> Path:
    """The folder under which this source's batch subfolders live.
    Carries no metadata itself - purely a namespace/detection root."""
    return DATA_ROOT / source_name


def list_available_sources() -> list[str]:
    """Every source currently onboarded: any subfolder of DATA_ROOT.
    Enumerable without any source being registered anywhere else."""
    if not DATA_ROOT.exists():
        return []
    return sorted(p.name for p in DATA_ROOT.iterdir() if p.is_dir())


def read_batch_metadata(batch_folder: str | Path) -> dict:
    """Loads the metadata.yaml INSIDE a specific batch folder - the
    format and coded fields that apply to THIS batch. Required: a batch
    without a metadata.yaml cannot be profiled (fails loudly rather than
    silently reusing a possibly-stale schema from a previous batch).

    Reads either the `files:` (CSV/Parquet) or `resources:` (FHIR) top-
    level key - whichever is present - and normalizes it into
    { "format": ..., "tables": {table_name: {field: standard}} }."""
    path = Path(batch_folder) / BATCH_METADATA_FILENAME
    if not path.exists():
        raise FileNotFoundError(
            f"Batch folder '{batch_folder}' is missing the required "
            f"'{BATCH_METADATA_FILENAME}' - every batch must declare its "
            f"own format and coded fields, since schema can drift "
            f"between batches of the same source."
        )
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    raw_tables = data.get("files") or data.get("resources") or {}

    tables: dict[str, dict[str, str | None]] = {}
    for key, fields in raw_tables.items():
        table_name = _strip_extension(key).lower()
        table_fields = tables.setdefault(table_name, {})
        for field_name, field_cfg in (fields or {}).items():
            standard = _normalize_standard((field_cfg or {}).get("standard"))
            table_fields[field_name] = standard

    return {
        "format": data.get("format"),
        "tables": tables,
        "type_concepts": data.get("type_concepts", {}),
        "fixed_value_mappings": data.get("fixed_value_mappings", {}),
        "local_vocab_overrides": data.get("local_vocab_overrides", {}),
    }


def get_field_standard(batch_cfg: dict, table: str, field: str) -> str | None:
    """Returns the declared standard (ICD10, LOINC, ...) for a given
    (table, field) pair in THIS batch's metadata, or None if not
    declared - tables/fields not listed are still profiled/mapped
    structurally, just without a semantic-mapping hint. Table matching
    is case-insensitive (see read_batch_metadata)."""
    return batch_cfg.get("tables", {}).get(table.lower(), {}).get(field)


def get_declared_fields_for_table(batch_cfg: dict, table: str) -> list[dict]:
    """All declared (coded) fields for a given table in THIS batch, as a
    list of {"name": ..., "standard": ...} - kept in this shape so
    callers (ProfilingAgent, MappingAgent) don't need to change how they
    iterate declared fields. Matching is case-insensitive (see
    read_batch_metadata) - the real discovered table name's case
    (whatever the source's own file-naming convention is) must not
    determine whether its declared fields are found."""
    table_fields = batch_cfg.get("tables", {}).get(table.lower(), {})
    return [{"name": name, "standard": standard} for name, standard in table_fields.items()]
