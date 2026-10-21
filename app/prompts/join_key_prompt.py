"""Prompt for the Loading Agent's single LLM task: identifying which
column in each of two source tables should be used to join them (e.g.
encounters.PATIENT <-> patients.Id). Asked ONCE per pair of tables, not
per row - the resulting join is then executed deterministically."""

JOIN_KEY_PROMPT = """You are the Loading Agent of a healthcare ETL framework.

Two tables from the same batch need to be joined to build a single OMOP
row. Identify which column in each table should be used as the join key
- the one that lets you match a row in table A to the row in table B
representing the SAME real-world entity (e.g. the same patient, or the
same visit).

Table A: {table_a}
Columns and sample values:
{columns_a}

Table B: {table_b}
Columns and sample values:
{columns_b}

Respond with STRICT JSON only, no markdown fences, no prose outside the
JSON:
{{
  "key_a": "<column name in table A, or null if no plausible join key exists>",
  "key_b": "<column name in table B, or null>",
  "confidence": <float between 0 and 1>,
  "reason": "<short reasoning>"
}}
"""
