"""Prompts for the Mapping Agent's structural resolution (mechanism 2):
for a given OMOP target table, which source table.field fills each
target field - both the initial attempt and the retry variants used
when a first attempt produces something that, in practice, doesn't
work (a 0% vocabulary match rate for a paired vocab-field, or simply no
source found at all for a plain field)."""

STRUCTURAL_TARGET_MAPPING_PROMPT = """You are the Mapping Agent of a healthcare ETL framework, resolving
structural (non-coded) fields for the OMOP CDM table '{target_table}'.

Tables discovered in this batch (columns + sample values):
{tables_summary}

Target fields to resolve (a plain list, not coded/vocabulary fields):
{target_fields}

For EACH target field, propose the single best (source_table,
source_field) pair that should fill it, based on column names and
sample values - never a hardcoded assumption about a specific source's
naming convention, since this must generalize to any future source.
If no plausible column exists for a field, return null rather than
guessing.

For a *_source_value field, the value to keep is the one the source
RECORDED, which is a code when the source has one. A column carrying a
"declared_standard" (NDC, ICD9CM, LOINC, ...) holds codes of that standard
vocabulary: choose it rather than a column of names or descriptions
(a drug name, a diagnosis label), even when the descriptive column looks
more readable. Choose a descriptive column only when no column of that
table holds a code. Do the same for a column whose sample values are
clearly codes of a recognised vocabulary even if none is declared.

Respond with STRICT JSON only, no markdown fences, no prose outside the
JSON, matching exactly this shape:
{{
  "mappings": [
    {{
      "target_field": "<one of the target OMOP fields above>",
      "source_table": "<table name, or null>",
      "source_field": "<field name, or null>",
      "confidence": <float between 0 and 1>,
      "reason": "<short reasoning>"
    }}
  ]
}}
"""

# Used when a previous resolution for this SAME field was found to be
# wrong AFTER the fact - not by a human, but by checking its actual
# result: every distinct value it produced failed to resolve against
# the vocabulary it was paired with (e.g. visit_source_value <-
# encounters.CODE led to a 0% match rate against the Visit vocabulary,
# revealing that CODE holds a clinical reason code, not a visit type,
# even though its name/samples looked plausible enough to pick at
# first). One retry only (see MAX_VOCAB_FIELD_RESOLUTION_ATTEMPTS) -
# this is a single, targeted correction, not a search loop.
STRUCTURAL_TARGET_MAPPING_RETRY_PROMPT = """You are the Mapping Agent of a healthcare ETL framework, resolving ONE
structural (non-coded) field for the OMOP CDM table '{target_table}'.

Your previous choice for this field was WRONG in practice: every
distinct value it produced failed to resolve against the vocabulary
this field feeds into ({vocabulary_domain}) - a 0% match rate. This
means the column you picked, while it looked plausible by name/sample
values, does not actually hold the kind of value this field needs.

Previous (rejected) choice: {rejected_table}.{rejected_field}

Tables discovered in this batch:
{tables_summary}

Target field to resolve: '{target_field}'

Task: propose a DIFFERENT (table, field) than the rejected one above -
look for a column whose actual VALUES (not just its name) plausibly
belong to a small, fixed category vocabulary, rather than a specific
clinical code. If no better alternative exists in this batch, return
null for source_table/source_field rather than repeating the same
rejected choice or guessing at random.

Respond with STRICT JSON only, no markdown fences, no prose outside the
JSON, matching exactly this shape:
{{
  "source_table": "<table name, or null>",
  "source_field": "<field name, or null>",
  "confidence": <float between 0 and 1>,
  "reason": "<short reasoning>"
}}
"""

# Used when the FIRST attempt at resolving one or more PLAIN structural
# fields (e.g. person_source_value) found NO source at all for them -
# a different failure mode than the vocab-field retry above (there is
# no "wrong column" to exclude here, just an absence of any answer).
# Generic by design: applies to ANY plain field that failed, not a
# hardcoded list - a critical field like person_source_value gets
# exactly the same second look as any other. One retry only, same
# principle as the vocab-field mechanism: a single targeted correction,
# never an open-ended search loop.
STRUCTURAL_PLAIN_FIELD_RETRY_PROMPT = """You are the Mapping Agent of a healthcare ETL framework, resolving
structural (non-coded) fields for the OMOP CDM table '{target_table}'.

Your FIRST attempt at resolving the fields below found NO plausible
source at all - neither a source_table nor a source_field. This can
happen when a genuinely fitting column was overlooked (an unusual but
correct name, or a column that plays this role in an unexpected
table), not necessarily because no such column exists.

Fields that could NOT be resolved on the first attempt:
{unresolved_fields}

Tables discovered in this batch (columns + sample values):
{tables_summary}

Look again, more carefully, at every discovered table - consider
columns whose name doesn't obviously match the target field's name but
whose VALUES (uniqueness, format, sample content) fit its role. For
example, a unique per-row identifier column in ANY table could serve
as a *_source_value field, even if its name doesn't contain the target
field's own name.

If, after this careful second look, you are still genuinely certain no
column exists for a field, return null for it again rather than
guessing at random - a second honest "no match" is a valid, expected
outcome for some fields.

Respond with STRICT JSON only, no markdown fences, no prose outside the
JSON, matching exactly this shape:
{{
  "mappings": [
    {{
      "target_field": "<one of the unresolved fields above>",
      "source_table": "<table name, or null>",
      "source_field": "<field name, or null>",
      "confidence": <float between 0 and 1>,
      "reason": "<short reasoning>"
    }}
  ]
}}
"""
