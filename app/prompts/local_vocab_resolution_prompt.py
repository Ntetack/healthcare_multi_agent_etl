"""Prompt for resolving a field explicitly declared as "local" in
metadata.yaml - meaning its raw values are an internal reference (not
a real external code), requiring a join to another table in the batch
to reach either a real external code, or a free-text description.

This is NEVER triggered for a normally-declared coded field (standard:
SNOMED, ICD9CM, etc.) - only for fields the batch's own metadata.yaml
explicitly flags as "local", so the join-resolution question is only
ever asked when genuinely needed, never wastefully for every declared
field."""

LOCAL_VOCAB_RESOLUTION_PROMPT = """You are the Mapping Agent of a healthcare ETL framework.

A field was declared as "local" - an internal reference whose raw
values are NOT a code by themselves:
  Table: {table}
  Field: {field}
  Sample raw values: {sample_values}

Other tables discovered in this batch (columns + sample values):
{tables_summary}

Determine which OTHER table in this batch is the dictionary/reference
table for this field, and what the resolved value actually represents
once joined.

Respond with STRICT JSON only, no markdown fences, no prose outside the
JSON:
{{
  "join_table": "<table name, or null if no plausible dictionary table exists>",
  "join_key_source": "<column in '{table}' used to join, or null>",
  "join_key_target": "<column in join_table used to join, or null>",
  "resolved_column": "<column in join_table holding the resolved value, or null>",
  "resolved_kind": "code" | "text",
  "resolved_standards": ["<vocabulary 1>", "<vocabulary 2>", ...],
  "confidence": <float between 0 and 1>,
  "reason": "<short reasoning>"
}}

Set "resolved_kind" to "code" ONLY if the resolved column holds a real,
externally-recognized code (e.g. a LOINC or SNOMED code). Set it to
"text" if the resolved column is a free-text description/label (e.g. a
name like "Heart Rate") with no external code - this is common and
expected, not a failure.

IMPORTANT PRIORITY RULE: if the SAME dictionary table offers BOTH a
real code column (e.g. a "loinc_code" column) AND a free-text label
column (e.g. "label") for the same reference, ALWAYS choose the real
code column and set "resolved_kind" to "code" - never the free-text
label in that case. A real, externally-recognized code is always more
precise and reliable than free-text matching, which only succeeds on
an exact string match and is far more prone to silent mismatches.
Free-text ("resolved_kind": "text") should be reserved for cases where
the dictionary table genuinely has NO real code column available at
all for this reference.

For "resolved_standards": list EVERY vocabulary this description could
plausibly belong to, MOST LIKELY FIRST - not just one. A single field
can genuinely mix different kinds of values (e.g. a drug/fluid
administration table's item names are usually drugs, but sometimes a
lab value or vital sign) - each vocabulary is tried in the order
listed, and the first one with a real match wins for that specific
value, so listing more than one costs nothing and only helps. Typical
examples: ["RxNorm"] for a drug/medication name, ["LOINC"] for a vital
sign or lab name, ["SNOMED"] for a diagnosis, a procedure/intervention
(e.g. "Colonoscopy", "Intubation"), a specimen type (e.g.
"Bronchoalveolar lavage"), or a microorganism (e.g. "Escherichia
coli"). For a table that plausibly mixes categories (e.g. a general
medication/fluid administration table), list several, such as
["RxNorm", "LOINC"]. Use an empty list only if you genuinely have no
idea. This guess only determines WHICH vocabularies get searched - a
wrong guess simply finds nothing, since only an EXACT text match will
ever be accepted downstream, never a fuzzy or partial one. A highly
source-specific compound description (e.g. combining an anatomical
site, a device, and a measurement type into one label) may genuinely
match nothing in any standard vocabulary - an empty list is the
correct, honest answer in that case, not a failure to guess harder.
"""