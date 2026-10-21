"""
Explains, from the artefacts of ONE pipeline run, why an OMOP table has the
rows it has. Reads only the JSON files under runs/<execution_id>/ : it touches
neither the database nor the model, and it never changes anything.

For a table (visit_occurrence by default) it reports:
  - the rows loaded for every table of the run, and, for the table asked for,
    why rows were dropped;
  - how each of its fields was mapped: from which source column, how many
    values were resolved, by a curated file or by the automatic search;
  - the warnings that matter, which are the problems met so far:
      * several source columns for the same field (the Transformation Agent
        applies the groups in turn and the last one erases the others),
      * a field none of whose values was resolved,
      * rows dropped because of a missing concept or a missing date.

Usage (from the project root):
    python scripts/diagnose_run.py RUN-synthea_fhir-e22e9aae
    python scripts/diagnose_run.py RUN-xxxx --table person
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

LOADING_STAGES = ("loading_load_temp", "loading")
SAMPLE_SIZE = 5


def read_result(run_dir: Path, stages: tuple[str, ...]) -> dict | None:
    """The `output` of the first stage folder that holds a result.json."""
    for stage in stages:
        path = run_dir / stage / "result.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")).get("output") or {}
    return None


def mapping_groups(structural_targets: list[dict], table: str) -> dict[tuple, dict]:
    """The structural records of a table grouped by (target field, source table,
    source column), with what each group resolved and how."""
    groups: dict[tuple, dict] = defaultdict(lambda: {
        "records": 0, "resolved": 0, "curated": 0, "unresolved_values": [], "reasons": set(),
    })
    for record in structural_targets:
        if record.get("target_table") != table or not record.get("source_field"):
            continue
        key = (record["target_field"], record.get("source_table"), record["source_field"])
        group = groups[key]
        group["records"] += 1
        resolved = record.get("target_concept_id") is not None
        group["resolved"] += resolved
        if "human-curated" in (record.get("reason") or ""):
            group["curated"] += 1
        if record.get("source_value") is not None and not resolved:
            group["unresolved_values"].append(str(record["source_value"]))
        if record.get("reason"):
            group["reasons"].add(record["reason"][:60])
    return groups


def warnings_for(table: str, groups: dict[tuple, dict], loading_detail: dict | None) -> list[str]:
    """What looks wrong, in plain words."""
    warnings: list[str] = []

    sources_by_field: dict[str, set] = defaultdict(set)
    for (field, source_table, source_field), group in groups.items():
        if field.endswith("_concept_id") and group["records"] > 0:
            sources_by_field[field].add((source_table, source_field))
    for field, sources in sources_by_field.items():
        if len(sources) > 1:
            listed = ", ".join(f"{t}.{c}" for t, c in sorted(sources))
            warnings.append(
                f"{field} has records from {len(sources)} different source columns ({listed}). The "
                f"Transformation Agent applies these groups in turn to the same output column: the last "
                f"one erases the others. This is how every row of a table can lose its concept."
            )

    for (field, source_table, source_field), group in groups.items():
        if field.endswith("_concept_id") and group["records"] and group["resolved"] == 0:
            warnings.append(f"{field} <- {source_table}.{source_field}: none of its {group['records']} values was resolved.")

    if loading_detail:
        for key, value in loading_detail.items():
            if key.startswith("dropped_") and isinstance(value, dict) and value.get("dropped_rows"):
                warnings.append(f"{value['dropped_rows']} rows of {table} were dropped ({key}): {str(value.get('reason', ''))[:110]}")
    return warnings


def build_report(run_dir: Path, table: str) -> list[str]:
    lines = [f"# {run_dir.name} - table {table}", "", "## Loading", ""]
    loading = read_result(run_dir, LOADING_STAGES)
    loading_detail = None
    if loading is None:
        lines.append(f"No loading result found under {run_dir} (looked for: {', '.join(LOADING_STAGES)}).")
    else:
        per_table = loading.get("per_table_result", {})
        for name, info in per_table.items():
            lines.append(f"- {name}: {info.get('rows_loaded')} rows" + (f" - {info['reason']}" if info.get("reason") else ""))
        loading_detail = per_table.get(table)
        if loading_detail is None:
            lines.append(f"\nNo result for '{table}' in this run.")

    lines += ["", f"## Mapping of {table}", ""]
    mapping = read_result(run_dir, ("mapping",))
    groups: dict[tuple, dict] = {}
    if mapping is None:
        lines.append(f"No mapping result found under {run_dir}.")
    else:
        groups = mapping_groups(mapping.get("structural_target_mappings", []), table)
        if not groups:
            lines.append(f"No field of {table} was mapped from a source column.")
        else:
            lines += ["| Field | Source column | Records | Resolved | By curated file | Unresolved values (sample) |",
                      "|---|---|---|---|---|---|"]
            for (field, source_table, source_field), g in sorted(groups.items()):
                sample = ", ".join(g["unresolved_values"][:SAMPLE_SIZE]) or "-"
                lines.append(f"| {field} | {source_table}.{source_field} | {g['records']} | {g['resolved']} | {g['curated']} | {sample} |")

        for label, key in (("Curated mappings derived for this FHIR batch", "fhir_derived_fixed_mappings"),
                           ("Coded fields derived for this FHIR batch", "fhir_derived_declarations")):
            entries = mapping.get(key, [])
            if entries:
                lines += ["", f"### {label}", ""]
                for e in entries:
                    name = f"{e.get('target_table', e.get('table'))}.{e.get('target_field', e.get('field'))}"
                    extra = f" - not covered: {e['values_not_covered']}" if e.get("values_not_covered") else ""
                    lines.append(f"- {name}: {e.get('status')}{extra}")
        retry = (mapping.get("vocab_field_retry_log") or {}).get(table)
        if retry:
            lines += ["", f"### Retry log for {table}", "", json.dumps(retry, ensure_ascii=False)[:600]]

    found = warnings_for(table, groups, loading_detail)
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in found] if found else ["- None of the known problems was detected."]
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("execution_id", help="Folder name under runs/, for example RUN-synthea_fhir-e22e9aae")
    parser.add_argument("--table", default="visit_occurrence", help="OMOP table to explain")
    parser.add_argument("--runs-dir", default="runs", type=Path)
    args = parser.parse_args()

    run_dir = args.runs_dir / args.execution_id
    if not run_dir.exists():
        print(f"No run folder: {run_dir}")
        return 1
    print("\n".join(build_report(run_dir, args.table)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
