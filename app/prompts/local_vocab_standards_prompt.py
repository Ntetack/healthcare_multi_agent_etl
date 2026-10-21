"""Prompt that picks the vocabularies to search for a local field AFTER its
dictionary join has been applied, from a sample of the REAL labels and of the
rows they come from.

The first prompt (local_vocab_resolution_prompt.py) has to find the join
before any label exists, so it can only guess the vocabularies from a few
raw identifiers. Once the join has produced readable labels, this second,
better-informed question is asked instead. The rows matter: a label alone
can look like something it is not (a drug name in a table of laboratory
results is not necessarily a drug given to the patient)."""

LOCAL_VOCAB_STANDARDS_PROMPT = """You are the Mapping Agent of a healthcare ETL framework.

A field declared "local" was joined to its dictionary. Table: {table},
field: {field}. The dictionary resolves its raw identifiers to the
free-text labels below ({n_labels} distinct labels sampled from
{n_distinct} in total):
{labels}

A few rows of that table (identifiers and dates left out), to show what
each row actually records:
{rows}

Decide which standard vocabularies these labels should be searched in.
Each label is later looked up by EXACT concept name, one vocabulary after
the other in the order you give, and the first vocabulary with a match
wins for that label.

Choose by what the ROW records about the label, not by how the label looks
on its own: the same word can name something given to a patient, something
measured on a patient or a specimen, or something diagnosed or done.
  - given to the patient (a drug, a fluid): ["RxNorm"]
  - measured or tested (a vital sign, a lab test, the result of a test):
    ["LOINC"]
  - a diagnosis, a clinical finding, a procedure, a specimen or a
    microorganism: ["SNOMED"]
A table can mix categories: list several vocabularies, most likely first.
Use an empty list only when the labels are too source-specific to exist
in any standard vocabulary.

Respond with STRICT JSON only, no markdown fences:
{{
  "resolved_standards": ["<vocabulary 1>", "<vocabulary 2>"],
  "confidence": <float between 0 and 1>,
  "reason": "<short reasoning, citing what the rows record>"
}}
"""
