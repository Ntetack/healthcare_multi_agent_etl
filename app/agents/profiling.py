"""
Profiling Agent (architecture doc v6, section 9 + new-data-detection +
per-batch-metadata requirement). Responsibilities, in order:

  0. Detect which batch folder to process, from the source's root folder
     (data/raw/<source_name>/). Detection itself needs no metadata - it's
     pure filesystem/DB bookkeeping. If nothing new is found, the agent
     stops the run cleanly rather than failing.
  1. Read THIS BATCH's own metadata.yaml (format + declared coded
     fields) - never a source-level file, since schema can drift between
     batches of the same source. A batch without metadata.yaml fails
     loudly rather than silently reusing a stale schema.
  2. AUTO-DISCOVER every distinct table in the batch folder - a real
     hospital export is never one flat file, it's several (MIMIC-style:
     PATIENTS, ADMISSIONS, DIAGNOSES, LABEVENTS, ...; OMOP-native:
     person, visit_occurrence, condition_occurrence, ...; FHIR: one
     resource type per file).
  3. For each discovered table: compute deterministic profiling facts via
     tools, and ask the LLM to interpret them, using whatever coding
     standard THIS BATCH declared for that (table, field) pair.

The Profiling Agent marks the folder IN_PROGRESS but never SUCCESS/FAILED
itself - see app/tools/data/folder_watcher.py docstring for why.
"""
from __future__ import annotations

import csv
import io
import json
from typing import Any

from app.agents.base import BaseAgent
from app.prompts.profiling_prompt import PROFILING_INTERPRETATION_PROMPT
from app.schemas.agent_result import AgentResult, AgentStatus
from app.tools.common.io_utils import run_dir
from app.tools.common.llm_utils import parse_json_response
from app.tools.data.folder_watcher import find_next_folder, mark_in_progress
from app.tools.data.metadata_loader import get_declared_fields_for_table, read_batch_metadata, source_root_path
from app.tools.data.schema_inspector import (
    detect_patterns,
    detect_possible_codings,
    inspect_schema,
    profile_dataset,
)
from app.tools.data.source_loader import load_source_tables


class ProfilingAgent(BaseAgent):
    name = "profiling_agent"
    stage = "profiling"

    def run(self, state: dict[str, Any]) -> AgentResult:
        source_name = state["source_name"]
        execution_id = state["execution_id"]
        source_root = source_root_path(source_name)

        # --- Step 0: detect new data (no metadata needed yet) -----------
        next_folder = find_next_folder(source_name, source_root)
        if next_folder is None:
            print(f"[Profiling] Aucun nouveau batch trouvé pour '{source_name}' sous '{source_root}'.")
            result = AgentResult(
                execution_id=execution_id,
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                output={"status": "NOTHING_TO_PROCESS", "source_root": str(source_root)},
                tools_used=["find_next_folder"],
                reasoning_summary=f"No new batch folder found under '{source_root}'. Nothing to process.",
            )
            return self.persist(result)

        print(f"[Profiling] Nouveau batch détecté pour '{source_name}' : {next_folder}")
        mark_in_progress(source_name, next_folder, execution_id)
        state["source_path"] = str(next_folder)

        # --- Step 1: read THIS BATCH's own metadata ----------------------
        batch_cfg = read_batch_metadata(next_folder)
        state["batch_metadata"] = batch_cfg  # handed off to the Mapping Agent

        # --- Step 2: auto-discover every table in the batch -------------
        tables = load_source_tables(batch_cfg["format"], next_folder)
        state["_raw_tables"] = tables  # handed off to the Mapping Agent, keyed by table name
        print(f"[Profiling] {len(tables)} table(s) découverte(s) : {', '.join(tables.keys())}")

        # --- Step 3: profile + interpret each table separately ----------
        per_table_output: dict[str, Any] = {}
        for table_name, df in tables.items():
            schema = inspect_schema(df)
            profile = profile_dataset(df)
            patterns = detect_patterns(df)
            codings = detect_possible_codings(df)
            interpretation = self._interpret_with_llm(table_name, profile, batch_cfg)
            # profile_dataset reports per-column missing/distinct counts,
            # but never a full-row duplicate count - computed here since
            # it's a table-level fact, not a per-column one.
            duplicate_rows = int(df.duplicated().sum())

            per_table_output[table_name] = {
                "schema": schema,
                "profile": profile,
                "patterns": patterns,
                "detected_codings": codings,
                "llm_interpretation": interpretation,
                "duplicate_rows": duplicate_rows,
            }

        report_md = self._build_readable_report(per_table_output)
        report_csv = self._build_report_csv(per_table_output)
        csv_path = run_dir(execution_id, self.stage) / "report.csv"
        csv_path.write_text(report_csv, encoding="utf-8")

        result = AgentResult(
            execution_id=execution_id,
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            input_summary={"source_name": source_name, "format": batch_cfg["format"], "folder": str(next_folder)},
            output={
                "status": "FOUND",
                "folder_processed": str(next_folder),
                "tables_discovered": list(tables.keys()),
                "per_table": per_table_output,
            },
            tools_used=[
                "find_next_folder", "mark_in_progress", "read_batch_metadata", "load_source_tables",
                "inspect_schema", "profile_dataset", "detect_patterns", "detect_possible_codings",
            ],
            reasoning_summary=(
                f"Detected new batch '{next_folder.name}' for '{source_name}': "
                f"{len(tables)} table(s) discovered ({', '.join(tables.keys())})."
            ),
        )
        return self.persist(result, report_markdown=report_md)

    @staticmethod
    def _build_readable_report(per_table_output: dict[str, Any]) -> str:
        """A clear, human-readable summary - not just the raw JSON -
        showing, for every discovered table: total rows, full-row
        duplicates, and per-column missing/distinct counts. Meant to be
        read at a glance before diving into the JSON for details."""
        lines = ["# Profiling Agent Report", ""]
        for table_name, info in sorted(per_table_output.items()):
            schema = info["schema"]
            n_rows = schema.get("n_rows", 0)
            duplicate_rows = info.get("duplicate_rows", 0)
            dup_pct = round(100 * duplicate_rows / n_rows, 1) if n_rows else 0

            lines.append(f"## {table_name}")
            lines.append(f"- Rows: {n_rows}")
            lines.append(f"- Columns: {schema.get('n_columns', 0)}")
            lines.append(f"- Full-row duplicates: {duplicate_rows} ({dup_pct}%)")
            lines.append("")
            lines.append("| Column | Missing | % Missing | Distinct |")
            lines.append("|---|---|---|---|")
            for col, stats in info["profile"].items():
                missing = stats.get("missing_count", 0)
                distinct = stats.get("distinct_count", 0)
                missing_pct = round(100 * missing / n_rows, 1) if n_rows else 0
                lines.append(f"| {col} | {missing} | {missing_pct}% | {distinct} |")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _build_report_csv(per_table_output: dict[str, Any]) -> str:
        """The same facts as _build_readable_report, as CSV - easier to
        load into pandas/Excel for systematic analysis across many
        tables or many runs than parsing a markdown table."""
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["table", "n_rows", "n_columns", "duplicate_rows", "duplicate_rows_pct",
                          "column", "missing_count", "missing_pct", "distinct_count"])
        for table_name, info in sorted(per_table_output.items()):
            schema = info["schema"]
            n_rows = schema.get("n_rows", 0)
            n_columns = schema.get("n_columns", 0)
            duplicate_rows = info.get("duplicate_rows", 0)
            dup_pct = round(100 * duplicate_rows / n_rows, 1) if n_rows else 0
            for col, stats in info["profile"].items():
                missing = stats.get("missing_count", 0)
                distinct = stats.get("distinct_count", 0)
                missing_pct = round(100 * missing / n_rows, 1) if n_rows else 0
                writer.writerow([table_name, n_rows, n_columns, duplicate_rows, dup_pct,
                                  col, missing, missing_pct, distinct])
        return buffer.getvalue()

    def _interpret_with_llm(self, table_name: str, profile: dict, batch_cfg: dict) -> dict:
        # Only the fields declared for THIS table, in THIS batch's own
        # metadata - a field named e.g. "code" in Condition and "code" in
        # Observation must not be conflated, and a previous batch's
        # standards must never leak into this one.
        field_standards = {
            f["name"]: f.get("standard") or "none"
            for f in get_declared_fields_for_table(batch_cfg, table_name)
        }
        prompt = PROFILING_INTERPRETATION_PROMPT.format(
            table_name=table_name,
            profiling_facts=json.dumps(profile, indent=2, default=str),
            field_standards=json.dumps(field_standards, indent=2),
        )
        response = self.llm.invoke(prompt)
        try:
            return parse_json_response(response.content)
        except ValueError:
            # Non-fatal: profiling can proceed without the LLM interpretation
            # for this table, the deterministic facts above remain available.
            return {"fields": [], "overall_notes": "LLM interpretation unavailable (parse error)."}
