"""
Structural mapping tools: deciding which staging column a source field
lands in. Deterministic helpers only - the *decision* of which OMOP
table/domain a field ultimately belongs to is made by the Mapping Agent
(LLM), informed by profiling output + source_metadata.yaml.
"""
from __future__ import annotations


def propose_staging_column_name(source_field: str) -> str:
    """Normalizes an arbitrary source field name (which may be a FHIR
    field_path like 'Condition.code' or a raw column like 'diagnosis_code')
    into a safe staging column name."""
    return (
        source_field.strip()
        .lower()
        .replace(".", "_")
        .replace("[", "_")
        .replace("]", "")
        .replace(" ", "_")
    )


def build_structural_mapping(source_fields: list[str]) -> dict[str, str]:
    """source_field -> staging.<column> for every declared field.
    This is the deterministic half of structural mapping; the Mapping
    Agent may still override individual entries based on profiling
    output (e.g. two source fields collapsing into one staging column)."""
    return {f: f"staging.{propose_staging_column_name(f)}" for f in source_fields}
