"""Prompt template for the Profiling Agent's LLM interpretation step
(the deterministic profiling facts are computed by tools; this prompt
asks the LLM to interpret them)."""

PROFILING_INTERPRETATION_PROMPT = """You are the Profiling Agent of a healthcare ETL framework.

You are interpreting ONE table out of a multi-table batch (a real hospital
export has several distinct tables, e.g. PATIENTS/ADMISSIONS/DIAGNOSES/
LABEVENTS, or person/visit_occurrence/condition_occurrence, or one FHIR
resource type per table). Do not assume other tables' fields apply here.

Table name: {table_name}

You are given deterministic profiling facts about this table, plus the
minimal metadata provided by the user for THIS table's fields
(Source + Table + Field + Standard).

Facts:
{profiling_facts}

Declared field standards for this table:
{field_standards}

Task: for each field, give a short interpretation of its likely clinical
meaning and flag any discrepancy between the declared standard and the
detected coding pattern. Be concise. Do not invent OMOP concept_ids here -
that is the Mapping Agent's job.

Respond with STRICT JSON only, no markdown fences, no prose outside the
JSON, matching exactly this shape:
{{
  "fields": [
    {{
      "field": "<field name>",
      "likely_meaning": "<short interpretation>",
      "standard_discrepancy": "<description, or null if none>",
      "confidence": <float between 0 and 1>
    }}
  ],
  "overall_notes": "<short free-text summary, 1-2 sentences>"
}}
"""
