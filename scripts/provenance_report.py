"""
Reports the provenance of every field/row in a pipeline run's results -
formalizes the manual investigation method used throughout this
project's comparison and debugging work.

Five sections, each answering a different provenance question:
  1. ROW-LEVEL: for each OMOP target table, how many actual rows came
     from each contributing source table. Domain-driven event tables
     report this via Loading's `<table>_FINAL_BY_SOURCE` diagnostic;
     structural tables (visit_occurrence, death, person) fall back to
     the plain "<target_table><-<source_table>" entry, since they never
     produce a FINAL_BY_SOURCE breakdown at all (a single primary
     source table by design).
  2. STRUCTURAL FIELD-LEVEL: for each OMOP target field, which source
     table.field was used to resolve it - showing ALL contributing
     resolutions when more than one source table supplies the same
     field, and flagging which ones needed the plain-field retry.
  3. VALUE-LEVEL (domain-driven vocab fields): for each source
     table.field declared in metadata.yaml, how many distinct values
     resolved to which target domain, and the match rate. A table
     declared but producing zero distinct values is explicitly reported
     as such, never silently dropped.
  4. FIXED MAPPINGS: every value resolved via a human-curated CSV
     (fixed_value_mappings) rather than the automatic LLM/vocabulary
     search - the whole point of this mechanism is visibility into
     what it covered, not just that it exists.
  5. LOCAL VOCABULARY JOINS: every "local" field's join outcome -
     success (with its resolved vocabulary/vocabularies) or failure
     (with the specific reason), so a table that silently produced
     nothing is never confused with one that was never attempted.

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
    tables_with_final_by_source: set[str] = set()
    for key, val in person_res.items():
        if key.endswith("_FINAL_BY_SOURCE") or "<-FINAL_BY_SOURCE" in key:
            target_table = key.split("<-")[0].split("_FINAL_BY_SOURCE")[0]
            tables_with_final_by_source.add(target_table)
            for source_table, counts in val.items():
                by_table[target_table][source_table] = counts.get("total", 0)

    # Structural tables fallback - see module docstring.
    for key, val in person_res.items():
        if "<-" not in key or "FINAL_BY_SOURCE" in key or key.endswith("<-BEFORE_INSERT"):
            continue
        target_table, source_table = key.split("<-", 1)
        if target_table in tables_with_final_by_source:
            continue
        if isinstance(val, dict) and "total_rows" in val:
            by_table[target_table][source_table] = val["total_rows"]

    if not by_table:
        lines.append("_Aucune donnée de provenance trouvée dans ce résultat de Loading._")
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
    retry_log = mapping_result.get("output", {}).get("vocab_field_retry_log", {})
    plain_retries = retry_log.get("_plain_field_retries", {})

    by_table: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for t in targets:
        if t.get("source_value") is not None:
            continue  # handled in the value-level section instead
        by_table[t["target_table"]][t["target_field"]].append(t)

    for target_table in sorted(by_table):
        lines.append(f"**{target_table}**")
        retried_here = set(plain_retries.get(target_table, {}).get("resolved_by_retry", []))
        for target_field in sorted(by_table[target_table]):
            records = by_table[target_table][target_field]
            retried_marker = " 🔁 (résolu par reprise)" if target_field in retried_here else ""
            if len(records) == 1 and not (records[0].get("source_table") and records[0].get("source_field")):
                lines.append(f"  - {target_field}: ❌ non résolu ({records[0].get('reason', '')[:80]})")
                continue
            for r in records:
                src = f"{r.get('source_table')}.{r.get('source_field')}"
                conf = r.get("confidence")
                conf_str = f"{conf:.2f}" if conf is not None else "—"
                lines.append(f"  - {target_field} ← {src} (confiance={conf_str}){retried_marker}")
        lines.append("")
    return lines


def value_level_provenance(mapping_result: dict) -> list[str]:
    lines = ["## 3. Provenance au niveau des valeurs (champs codés, mécanisme 1)", ""]
    per_table = mapping_result.get("output", {}).get("per_table", {})

    for source_table in sorted(per_table):
        semantic = per_table[source_table].get("semantic_mapping", [])
        if not semantic:
            lines.append(f"**{source_table}**")
            lines.append("  - _Déclarée, mais aucune valeur distincte produite pour ce batch._")
            lines.append("")
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


def fixed_mapping_provenance(mapping_result: dict) -> list[str]:
    lines = ["## 4. Résolutions via mapping figé (fixed_value_mappings)", ""]
    targets = mapping_result.get("output", {}).get("structural_target_mappings", [])
    fixed = [t for t in targets if "human-curated" in (t.get("reason") or "")]

    if not fixed:
        lines.append("_Aucune résolution via mapping figé dans ce run._")
        lines.append("")
        return lines

    by_field: dict[tuple, list[dict]] = defaultdict(list)
    for t in fixed:
        by_field[(t["target_table"], t["target_field"])].append(t)

    for (target_table, target_field), records in sorted(by_field.items()):
        lines.append(f"**{target_table}.{target_field}** — {len(records)} valeur(s) couverte(s) par le CSV")
        for r in records:
            lines.append(f"  - {r['source_value']!r} -> concept_id={r['target_concept_id']}")
        lines.append("")
    return lines


def local_vocab_join_provenance(mapping_result: dict) -> list[str]:
    lines = ["## 5. Jointures de vocabulaire local", ""]
    output = mapping_result.get("output", {})
    successes = output.get("local_vocab_joins", {})
    failures = output.get("local_vocab_join_failures", {})

    if not successes and not failures:
        lines.append("_Aucun champ 'local' déclaré dans ce batch._")
        lines.append("")
        return lines

    if successes:
        lines.append("**Réussies :**")
        for key, spec in sorted(successes.items()):
            standards = spec.get("resolved_standards") or spec.get("resolved_standard") or "—"
            lines.append(
                f"  - {key} -> {spec.get('join_table')}.{spec.get('resolved_column')} "
                f"({spec.get('resolved_kind')}, vocabulaire(s)={standards})"
            )
        lines.append("")

    if failures:
        lines.append("**Échouées :**")
        for key, reason in sorted(failures.items()):
            lines.append(f"  - {key}")
            lines.append(f"      -> {reason}")
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
    lines += fixed_mapping_provenance(mapping_result)
    lines += local_vocab_join_provenance(mapping_result)

    report = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Rapport écrit : {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
