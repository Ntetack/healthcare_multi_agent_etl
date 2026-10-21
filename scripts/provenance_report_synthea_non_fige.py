"""
Reports the provenance of every field/row in a pipeline run's results -
formalizes the manual investigation method used throughout this
project's comparison work (checking which source table.field produced
which rows/values, and at what resolution rate).

Three levels of provenance, one section each:
  1. ROW-LEVEL: for each OMOP target table, how many actual rows came
     from each contributing source table (from Loading's
     person_id_resolution `<table>_FINAL_BY_SOURCE` diagnostics).
  2. STRUCTURAL FIELD-LEVEL: for each OMOP target field, which source
     table.field was used to resolve it (from Mapping's
     structural_target_mappings) - showing ALL contributing
     resolutions when more than one source table supplies the same
     field (see mapping.py's _build_report for why this matters).
  3. VALUE-LEVEL (domain-driven vocab fields): for each source
     table.field declared in metadata.yaml, how many distinct values
     resolved to which target domain, and the match rate (from
     Mapping's semantic_mapping).

Usage:
    python scripts/provenance_report.py RUN-xxxxxxxx
    python scripts/provenance_report.py RUN-xxxxxxxx --runs-dir runs --output provenance.md
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def row_level_provenance(loading_result: dict) -> list[str]:
    lines = ["## 1. Provenance au niveau des lignes (tables OMOP finales)", ""]
    person_res = loading_result.get("output", {}).get("person_id_resolution", {})

    by_table: dict[str, dict[str, int]] = defaultdict(dict)
    for key, val in person_res.items():
        if key.endswith("_FINAL_BY_SOURCE") or "<-FINAL_BY_SOURCE" in key:
            target_table = key.split("<-")[0].split("_FINAL_BY_SOURCE")[0]
            for source_table, counts in val.items():
                by_table[target_table][source_table] = counts.get("total", 0)

    if not by_table:
        lines.append("_Aucune donnée FINAL_BY_SOURCE trouvée dans ce résultat de Loading._")
        return lines

    for target_table in sorted(by_table):
        sources = by_table[target_table]
        total = sum(sources.values())
        lines.append(f"**{target_table}** — {total} lignes au total")
        for source_table, count in sorted(sources.items(), key=lambda x: -x[1]):
            pct = 100 * count / total if total else 0
            lines.append(f"  - {source_table}: {count} lignes ({pct:.0f}%)")
        lines.append("")
    return lines


def structural_field_level_provenance(mapping_result: dict) -> list[str]:
    lines = ["## 2. Provenance au niveau des champs structurels", ""]
    targets = mapping_result.get("output", {}).get("structural_target_mappings", [])

    by_table: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for t in targets:
        if t.get("source_value") is not None:
            continue  # handled in the value-level section instead
        by_table[t["target_table"]][t["target_field"]].append(t)

    for target_table in sorted(by_table):
        lines.append(f"**{target_table}**")
        for target_field in sorted(by_table[target_table]):
            records = by_table[target_table][target_field]
            if len(records) == 1 and not (records[0].get("source_table") and records[0].get("source_field")):
                lines.append(f"  - {target_field}: ❌ non résolu ({records[0].get('reason', '')[:80]})")
                continue
            for r in records:
                src = f"{r.get('source_table')}.{r.get('source_field')}"
                conf = r.get("confidence")
                conf_str = f"{conf:.2f}" if conf is not None else "—"
                lines.append(f"  - {target_field} ← {src} (confiance={conf_str})")
        lines.append("")
    return lines


def value_level_provenance(mapping_result: dict) -> list[str]:
    lines = ["## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)", ""]
    per_table = mapping_result.get("output", {}).get("per_table", {})

    for source_table in sorted(per_table):
        semantic = per_table[source_table].get("semantic_mapping", [])
        if not semantic:
            continue
        by_field: dict[str, Counter] = defaultdict(Counter)
        matched: dict[str, int] = defaultdict(int)
        total: dict[str, int] = defaultdict(int)
        for m in semantic:
            field = m.get("field", "?")
            target = m.get("target_table") or "AUCUN"
            by_field[field][target] += 1
            total[field] += 1
            if m.get("target_concept_id") is not None:
                matched[field] += 1

        lines.append(f"**{source_table}**")
        for field in sorted(by_field):
            match_rate = 100 * matched[field] / total[field] if total[field] else 0
            lines.append(f"  - {field}: {total[field]} valeurs distinctes, {match_rate:.0f}% résolues")
            for target, count in by_field[field].most_common():
                lines.append(f"      -> {target}: {count} valeurs")
        lines.append("")
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("execution_id")
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--output", default=None, help="Output path (default: print to stdout)")
    args = parser.parse_args()

    run_dir = Path(args.runs_dir) / args.execution_id
    mapping_result = load_json(run_dir / "mapping" / "result.json")
    loading_result = load_json(run_dir / "loading_load_temp" / "result.json")

    if mapping_result is None:
        print(f"Aucun résultat de Mapping trouvé dans {run_dir / 'mapping'}")
        return

    lines = [f"# Rapport de provenance — {args.execution_id}", ""]
    if loading_result:
        lines += row_level_provenance(loading_result)
    else:
        lines.append("_Aucun résultat de Loading trouvé - section 1 ignorée._\n")
    lines += structural_field_level_provenance(mapping_result)
    lines += value_level_provenance(mapping_result)

    report = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Rapport écrit : {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
