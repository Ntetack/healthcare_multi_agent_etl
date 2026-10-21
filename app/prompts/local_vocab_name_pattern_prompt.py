"""Prompt that chooses, for a local field, WHICH VARIANT of a concept the
source means, once the vocabulary is known.

Some vocabularies describe one thing in several concepts that differ by a
trailing qualifier, e.g. "Gentamicin [Susceptibility]" and "Gentamicin
[Susceptibility] by Minimum inhibitory concentration (MIC)". The label
(GENTAMICIN) does not say which. The qualifiers below were FOUND in the
vocabulary for the sampled labels - the model chooses among them, it never
invents one - and the choice is then applied to every label by exact name."""

LOCAL_VOCAB_NAME_PATTERN_PROMPT = """You are the Mapping Agent of a healthcare ETL framework.

Table: {table}, field: {field}. Its raw identifiers were resolved to
free-text labels (for example: {labels}).

For these labels, the vocabulary has concepts whose name is the label
followed by a qualifier. Each line is a qualifier, the number of sampled
labels ({n_labels} in total) that have a concept with it, and the domain
of those concepts:
{suffixes}

A few rows of that table (identifiers and dates left out), to show what the
data actually records:
{rows}

Choose the qualifier(s) that match WHAT THE DATA RECORDS - for instance the
method or the form that the other columns reveal - in order of preference:
the first one that has a concept for a given label is used, the next ones
are fallbacks. A fallback should be a less specific description of the same
thing, never a different thing. The empty qualifier "" means the label
itself, unchanged.

Rules:
  - choose only among the qualifiers listed above, copied exactly;
  - if the rows give no evidence for a more specific qualifier, prefer the
    least specific one that is listed;
  - if none of them describes what the rows record, answer an empty list.

Respond with STRICT JSON only, no markdown fences:
{{
  "suffixes": ["<qualifier 1>", "<qualifier 2>"],
  "confidence": <float between 0 and 1>,
  "reason": "<short reasoning, citing the columns that decided it>"
}}
"""
