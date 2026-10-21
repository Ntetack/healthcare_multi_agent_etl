"""
Resolves the join key between two source tables - the ONE task the
Loading Agent delegates to an LLM (see app/prompts/join_key_prompt.py).
Asked once per pair of tables in a batch, never per row: the LLM
proposes which columns identify the same real-world entity across two
tables (e.g. encounters.PATIENT <-> patients.Id); the actual join is
then executed deterministically with pandas.merge() - the LLM never
touches data, only proposes which columns to use.
"""
from __future__ import annotations

import json
from typing import Any

from app.prompts.join_key_prompt import JOIN_KEY_PROMPT
from app.tools.common.llm_utils import parse_json_response


def resolve_join_key(
    llm: Any, table_a: str, df_a_columns_sample: dict, table_b: str, df_b_columns_sample: dict
) -> tuple[str, str] | None:
    """Returns (key_a, key_b) - the column names in each table to join
    on - or None if the LLM found no plausible join key. Does not touch
    any data; purely a column-name-level decision."""
    prompt = JOIN_KEY_PROMPT.format(
        table_a=table_a,
        columns_a=json.dumps(df_a_columns_sample, indent=2, default=str),
        table_b=table_b,
        columns_b=json.dumps(df_b_columns_sample, indent=2, default=str),
    )
    response = llm.invoke(prompt)
    try:
        parsed = parse_json_response(response.content)
    except ValueError:
        return None

    key_a, key_b = parsed.get("key_a"), parsed.get("key_b")
    if not key_a or not key_b:
        return None
    return key_a, key_b
