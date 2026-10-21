"""
Reference schema for the OMOP CDM target tables in scope for this
prototype: PERSON, OBSERVATION_PERIOD, VISIT_OCCURRENCE,
CONDITION_OCCURRENCE, DRUG_EXPOSURE, MEASUREMENT, PROCEDURE_OCCURRENCE,
OBSERVATION, DEATH.

TWO SEPARATE static/known things, neither built by an agent at runtime:

1. app/config/reference/omop_vocabulary_fields.yaml (human-provided, not
   generated) - lists exactly which *_concept_id fields are backed by a
   fixed OMOP vocabulary, and which vocabulary_domain applies. Loaded
   once here.
2. The REAL field list of each table, via
   app/tools/mapping/omop_schema_introspection.py - introspected from the
   already-instantiated OMOP DDL, never hand-curated, so every field
   (including ones we previously missed, like year_of_birth) is known.

Two mapping mechanisms use this combination (see MappingAgent):

  a. ROW-LEVEL DOMAIN ROUTING (unchanged): for the 5 clinical event
     tables, a semantically mapped concept's domain_id tells us which
     OMOP table a given source row belongs in. See DOMAIN_TO_TABLE /
     resolve_target() below - this is about WHICH TABLE a row goes to,
     not which vocabulary fills a given table's own concept fields.

  b. TARGET-FIRST FIELD RESOLUTION (new): for every field of every one
     of the 9 tables (from the real introspected list), find the
     matching source field - via the LLM for plain fields (dates,
     source_value, ...), or automatically for vocabulary fields (b)
     once their paired *_source_value field has been resolved, using
     PAIRING_SUFFIXES below - a naming-convention rule, not a
     hand-curated per-field list.
"""
from __future__ import annotations

from pathlib import Path

import yaml

VOCABULARY_FIELDS_PATH = Path("app/config/reference/omop_vocabulary_fields.yaml")

# domain_id (from cdm_vocab.concept.domain_id) -> target OMOP table, for
# ROW-LEVEL ROUTING of the 5 domain-driven event tables (mechanism 'a').
DOMAIN_TO_TABLE = {
    "Condition": "condition_occurrence",
    "Drug": "drug_exposure",
    "Measurement": "measurement",
    "Procedure": "procedure_occurrence",
    "Observation": "observation",
}
TABLE_FIELD_TEMPLATES = {
    "condition_occurrence": {
        "concept_field": "condition_concept_id", "source_value_field": "condition_source_value",
        "source_concept_field": "condition_source_concept_id",
    },
    "drug_exposure": {
        "concept_field": "drug_concept_id", "source_value_field": "drug_source_value",
        "source_concept_field": "drug_source_concept_id",
    },
    "measurement": {
        "concept_field": "measurement_concept_id", "source_value_field": "measurement_source_value",
        "source_concept_field": "measurement_source_concept_id",
    },
    "procedure_occurrence": {
        "concept_field": "procedure_concept_id", "source_value_field": "procedure_source_value",
        "source_concept_field": "procedure_source_concept_id",
    },
    "observation": {
        "concept_field": "observation_concept_id", "source_value_field": "observation_source_value",
        "source_concept_field": "observation_source_concept_id",
    },
}

# All 9 in-scope tables, DB name (lowercase) <-> YAML key (uppercase, per
# omop_vocabulary_fields.yaml convention).
IN_SCOPE_TABLES = [
    "person", "observation_period", "visit_occurrence", "condition_occurrence",
    "drug_exposure", "measurement", "procedure_occurrence", "observation", "death",
]

# Suffixes tried, in order, to find a vocabulary field's paired plain
# field - e.g. "gender_concept_id" -> strip "_concept_id" -> "gender" ->
# try "gender_source_value". This is the OMOP naming CONVENTION, not a
# per-field hand-curated list: it generalizes to any table/field without
# maintenance as new fields are added.
PAIRING_SUFFIXES = ["_source_concept_id", "_concept_id"]


def resolve_target(domain_id: str | None) -> dict | None:
    """Row-level routing (mechanism 'a'): given a mapped concept's
    domain_id, returns {"table":, "concept_field":, "source_value_field":}
    for one of the 5 domain-driven event tables, or None otherwise."""
    table = DOMAIN_TO_TABLE.get(domain_id)
    if not table:
        return None
    return {"table": table, **TABLE_FIELD_TEMPLATES[table]}


_vocabulary_fields_cache: dict | None = None


def load_vocabulary_fields() -> dict[str, dict[str, str]]:
    """Loads omop_vocabulary_fields.yaml (human-provided) once:
    {TABLE_NAME_UPPER: {field_name: vocabulary_domain}}."""
    global _vocabulary_fields_cache
    if _vocabulary_fields_cache is None:
        with open(VOCABULARY_FIELDS_PATH, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        _vocabulary_fields_cache = {
            table: {field: cfg.get("vocabulary_domain") for field, cfg in fields.items()}
            for table, fields in raw.items()
        }
    return _vocabulary_fields_cache


def get_vocabulary_fields(table_name: str) -> dict[str, str]:
    """{field_name: vocabulary_domain} for one table (DB lowercase name),
    looked up against the YAML's uppercase keys."""
    return load_vocabulary_fields().get(table_name.upper(), {})


def find_paired_source_value_field(concept_field: str, available_fields: list[str]) -> str | None:
    """Applies the OMOP naming convention to find which plain field a
    vocabulary field should be resolved FROM. Returns None if no such
    field exists in this table (e.g. *_type_concept_id fields represent
    record provenance, not a value present in the source data - they
    have no natural pairing and need a fixed ETL convention instead,
    which this framework does not attempt to guess)."""
    for suffix in PAIRING_SUFFIXES:
        if concept_field.endswith(suffix):
            prefix = concept_field[: -len(suffix)]
            candidate = f"{prefix}_source_value"
            if candidate in available_fields:
                return candidate
    return None
