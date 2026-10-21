"""
Transformation Agent. Casts raw string values into real types, driven
entirely by what the Mapping Agent already resolved - both WHICH source
field fills a target field, and the target field's REAL SQL type
(introspected from the already-instantiated OMOP DDL, never guessed).

Two kinds of structural_target_mappings records from Mapping, told apart
by `source_value` (see app/schemas/structural_target_mapping.py):

  1. Vocabulary fields (source_value set, e.g. gender_concept_id): one
     record per distinct source value, each already carrying its
     resolved target_concept_id. Grouped by (target_table, target_field,
     source_table, source_field) and combined into a single
     `source_value -> concept_id` mapping, applied to the whole column
     at once. No casting needed - concept_id is already an int.

  2. Plain fields (source_value is None, e.g. birth_datetime,
     condition_start_date): one record per field. Cast according to
     `data_type` (the real SQL type of that OMOP column) - date/
     timestamp -> parse_date, numeric types -> cast_decimal, integer ->
     cast_integer, boolean -> normalize_boolean, anything else
     (varchar, text) -> copied as-is.

Both are written into a new column named `__omop_{target_table}__
{target_field}` on the relevant SOURCE table's DataFrame - a uniform,
predictable location for the Loading Agent to read from regardless of
the source's own naming convention.

Row-level target-table routing for the 5 domain-driven event tables is
NOT this agent's job - that is the Loading Agent's known, separately-
tracked responsibility.
"""
from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Any, Callable

from app.agents.base import BaseAgent
from app.schemas.agent_result import AgentResult, AgentStatus
from app.tools.transformation.transform_tools import (
    cast_decimal,
    cast_integer,
    detect_day_first,
    normalize_boolean,
    parse_date,
)

# Real PostgreSQL data_type strings (as returned by information_schema)
# mapped to the transform to apply. Anything not listed here (varchar,
# text, character varying, ...) is copied as-is.
_DATA_TYPE_TRANSFORMS: dict[str, Callable] = {
    "date": parse_date,
    "timestamp without time zone": parse_date,
    "timestamp with time zone": parse_date,
    "integer": cast_integer,
    "bigint": cast_integer,
    "smallint": cast_integer,
    "numeric": cast_decimal,
    "double precision": cast_decimal,
    "real": cast_decimal,
    "boolean": normalize_boolean,
}


class TransformationAgent(BaseAgent):
    name = "transformation_agent"
    stage = "transformation"

    def run(self, state: dict[str, Any]) -> AgentResult:
        tables: dict[str, Any] = state.get("_enriched_tables") or state["_raw_tables"]
        structural_targets = state.get("mapping_output", {}).get("structural_target_mappings", [])

        transformed_tables = {name: df.copy() for name, df in tables.items()}
        applied: list[dict] = []
        skipped: list[dict] = []

        vocab_records = [m for m in structural_targets if m.get("source_value") is not None]
        plain_records = [
            m for m in structural_targets
            if m.get("source_value") is None and m.get("source_table") and m.get("source_field")
        ]

        self._apply_vocab_fields(vocab_records, transformed_tables, applied, skipped)
        self._apply_plain_fields(plain_records, transformed_tables, applied, skipped)

        state["_transformed_tables"] = transformed_tables

        result = AgentResult(
            execution_id=state["execution_id"],
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            output={"applied": applied, "skipped": skipped},
            tools_used=sorted({a["transform"] for a in applied}),
            reasoning_summary=(
                f"Applied {len(applied)} field transform(s) across "
                f"{len(transformed_tables)} table(s); {len(skipped)} skipped."
            ),
        )
        return self.persist(result)

    @staticmethod
    def _apply_vocab_fields(vocab_records: list[dict], transformed_tables: dict, applied: list, skipped: list) -> None:
        groups: dict[tuple, dict[str, int | None]] = {}
        for m in vocab_records:
            key = (m["target_table"], m["target_field"], m["source_table"], m["source_field"])
            groups.setdefault(key, {})[m["source_value"]] = m.get("target_concept_id")

        for (target_table, target_field, source_table, source_field), value_to_concept in groups.items():
            df = transformed_tables.get(source_table)
            if df is None or source_field not in df.columns:
                skipped.append({
                    "target_table": target_table, "target_field": target_field,
                    "source_table": source_table, "source_field": source_field,
                    "reason": "source table/field not present in this batch",
                })
                continue
            output_column = f"__omop_{target_table}__{target_field}"
            df[output_column] = df[source_field].astype(str).map(value_to_concept)
            applied.append({
                "target_table": target_table, "target_field": target_field,
                "source_table": source_table, "source_field": source_field,
                "transform": "vocabulary_lookup", "output_column": output_column,
            })

    @staticmethod
    def _apply_plain_fields(plain_records: list[dict], transformed_tables: dict, applied: list, skipped: list) -> None:
        for m in plain_records:
            source_table, source_field = m["source_table"], m["source_field"]
            target_table, target_field = m["target_table"], m["target_field"]
            df = transformed_tables.get(source_table)
            if df is None or source_field not in df.columns:
                skipped.append({**m, "reason": "source table/field not present in this batch"})
                continue

            data_type = (m.get("data_type") or "").lower()
            output_column = f"__omop_{target_table}__{target_field}"
            fn = _DATA_TYPE_TRANSFORMS.get(data_type)

            if fn is parse_date:
                # Day-first vs month-first ambiguity (e.g. "03/04/2024")
                # is resolved ONCE from this column's own real values -
                # never guessed per row, never left to flip
                # inconsistently within the same column.
                dayfirst = detect_day_first(df[source_field].dropna().unique().tolist())
                fn = partial(parse_date, dayfirst=dayfirst)

            if fn is None:
                df[output_column] = df[source_field]
                applied.append({**m, "transform": "copy_as_is", "output_column": output_column})
            elif data_type == "date":
                # parse_date() may return a full datetime if the source
                # value carried a time component - truncate to a plain
                # date here since the OMOP target column is DATE, not
                # TIMESTAMP (which is handled by the branch below).
                df[output_column] = df[source_field].map(fn).map(
                    lambda v: v.date() if isinstance(v, datetime) else v
                )
                applied.append({**m, "transform": "parse_date (truncated to date)", "output_column": output_column})
            else:
                df[output_column] = df[source_field].map(fn)
                applied.append({**m, "transform": getattr(fn, "func", fn).__name__, "output_column": output_column})
