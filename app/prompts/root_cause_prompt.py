"""Prompt for the Root Cause Analyzer's real reasoning step. Given a
structured failure and the retry history for this stage, the LLM
assesses severity and recommends ONE action - it does not fix anything
itself, and it must not recommend retrying a stage whose failure looks
like a deterministic code/config defect (retrying won't change a
deterministic outcome) versus a genuinely tolerable data-quality issue
that the run could proceed past."""

ROOT_CAUSE_PROMPT = """You are the Root Cause Analyzer of a healthcare ETL framework.

A failure occurred. Analyze it and recommend exactly one action.

Failure details:
{failure_details}

Retry history for this stage: {retry_count} attempt(s) already made
(maximum allowed: {max_retries}).

Guidance:
- "retry": worth attempting again as-is (e.g. a transient/infrastructure
  issue like a timeout) - do NOT recommend this for something that looks
  like a deterministic data or logic problem, since retrying identical
  inputs against identical code will fail identically.
- "recompute_mapping": the failure traces to mapping quality (e.g. many
  unmapped concepts, wrong domain routing) - worth re-running mapping.
- "resume_stage": the failure is tolerable enough that the pipeline can
  continue from the SAME stage that failed (e.g. non-fatal data quality
  issues where proceeding is reasonable).
- "human_intervention": the failure needs a person to look at it (e.g.
  a configuration problem, a systematic data issue, retries exhausted).
- "stop_run": abandon this batch entirely (e.g. unrecoverable technical
  failure, or the batch's data is fundamentally unusable).

Respond with STRICT JSON only, no markdown fences, no prose outside the
JSON:
{{
  "probable_cause": "<short explanation of what likely went wrong>",
  "severity": "tolerable" | "serious" | "fatal",
  "recommended_action": "retry" | "recompute_mapping" | "resume_stage" | "human_intervention" | "stop_run",
  "resume_from_stage": "<one of: mapping, transformation, loading, validation - or null>"
}}
"""
