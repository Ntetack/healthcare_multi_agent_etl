#!/usr/bin/env python3
"""
Evaluate agent structural mapping against scoped gold standard.

Gold statuses:
  MAP        -> expect (source_table, source_field); use Precision/Recall/F1
  FIXED      -> expect constant value (type_concept_id); no source
  NO_MAPPING -> expect no source proposal

Out of scope (ignored):
  *_concept_id / *_source_concept_id (semantic mapping)
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def norm(s: Optional[str]) -> str:
    if s is None:
        return ""
    return re.sub(r"[^a-z0-9]", "", str(s).strip().lower())


def norm_table(s: Optional[str]) -> str:
    t = norm(s)
    if t.endswith("csv"):
        t = t[:-3]
    return t


def is_semantic_field(field: str) -> bool:
    f = field.lower()
    if f.endswith("_type_concept_id"):
        return False  # FIXED, in scope
    if f.endswith("_source_concept_id") or f.endswith("_concept_id"):
        return True
    return False


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_gold(path: Path) -> List[dict]:
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "omop_table": r["omop_table"].strip(),
                "omop_field": r["omop_field"].strip(),
                "expected_source_table": r.get("expected_source_table", "").strip(),
                "expected_source_field": r.get("expected_source_field", "").strip(),
                "status": r["status"].strip().upper(),
                "expected_value": r.get("expected_value", "").strip(),
                "notes": r.get("notes", "").strip(),
            })
    return rows


def load_agent_report(path: Path) -> List[dict]:
    """Load agent report; keep structural_field rows with a target_table."""
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            section = (r.get("section") or "").strip().lower()
            if section and section != "structural_field":
                continue
            target_table = (r.get("target_table") or "").strip()
            target_field = (r.get("target_field") or "").strip()
            if not target_table or not target_field:
                continue
            rows.append({
                "status": (r.get("status") or "").strip().upper(),
                "target_table": target_table,
                "target_field": target_field,
                "source_table": (r.get("source_table") or "").strip(),
                "source_field": (r.get("source_field") or "").strip(),
                "confidence": (r.get("confidence") or "").strip(),
                "reason": (r.get("reason") or "").strip(),
            })
    return rows


# ---------------------------------------------------------------------------
# Index agent proposals
# ---------------------------------------------------------------------------

def build_agent_index(agent_rows: List[dict]):
    """
    Returns:
      proposals[(table, field)] = set of (norm_source_table, norm_source_field)
      has_any[(table, field)] = bool  (agent mentioned the field at all)
      raw_proposals[(table, field)] = list of original (source_table, source_field)
    """
    proposals = defaultdict(set)
    has_any = defaultdict(bool)
    raw_proposals = defaultdict(list)

    for r in agent_rows:
        key = (norm_table(r["target_table"]), norm(r["target_field"]))
        has_any[key] = True
        st = r["source_table"]
        sf = r["source_field"]
        if st and sf:
            proposals[key].add((norm_table(st), norm(sf)))
            raw_proposals[key].append((st, sf))

    return proposals, has_any, raw_proposals


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(gold_rows: List[dict], agent_rows: List[dict]) -> dict:
    proposals, has_any, raw_proposals = build_agent_index(agent_rows)

    # Aggregate gold MAP sources per (table, field)
    gold_map: Dict[Tuple[str, str], Set[Tuple[str, str]]] = defaultdict(set)
    gold_fixed: Dict[Tuple[str, str], str] = {}
    gold_no_mapping: Set[Tuple[str, str]] = set()
    gold_meta: Dict[Tuple[str, str], dict] = {}

    for g in gold_rows:
        key = (norm_table(g["omop_table"]), norm(g["omop_field"]))
        gold_meta[key] = g
        if g["status"] == "MAP":
            if g["expected_source_table"] and g["expected_source_field"]:
                gold_map[key].add((
                    norm_table(g["expected_source_table"]),
                    norm(g["expected_source_field"]),
                ))
        elif g["status"] == "FIXED":
            gold_fixed[key] = g["expected_value"]
        elif g["status"] == "NO_MAPPING":
            gold_no_mapping.add(key)

    # --- MAP metrics ---
    map_details = []
    tp = fp = fn = 0

    for key, gold_sources in gold_map.items():
        agent_sources = proposals.get(key, set())
        inter = gold_sources & agent_sources
        _tp = len(inter)
        _fp = len(agent_sources - gold_sources)
        _fn = len(gold_sources - agent_sources)
        tp += _tp
        fp += _fp
        fn += _fn

        prec = _tp / (_tp + _fp) if (_tp + _fp) else (1.0 if not gold_sources else 0.0)
        rec = _tp / (_tp + _fn) if (_tp + _fn) else (1.0 if not agent_sources else 0.0)
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0

        meta = gold_meta[key]
        map_details.append({
            "omop_table": meta["omop_table"],
            "omop_field": meta["omop_field"],
            "gold_sources": sorted(
                f"{a}.{b}" for a, b in (
                    (gold_meta[key]["expected_source_table"], gold_meta[key]["expected_source_field"])
                    for _ in [0]  # placeholder; rebuild from gold_rows below
                )
            ),
            "gold_sources_norm": sorted(f"{a}.{b}" for a, b in gold_sources),
            "agent_sources": sorted(f"{a}.{b}" for a, b in agent_sources),
            "agent_sources_raw": raw_proposals.get(key, []),
            "tp": _tp,
            "fp": _fp,
            "fn": _fn,
            "precision": prec,
            "recall": rec,
            "f1": f1,
        })

    # Rebuild readable gold sources list properly
    gold_readable: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for g in gold_rows:
        if g["status"] != "MAP":
            continue
        key = (norm_table(g["omop_table"]), norm(g["omop_field"]))
        if g["expected_source_table"] and g["expected_source_field"]:
            gold_readable[key].append(
                f"{g['expected_source_table']}.{g['expected_source_field']}"
            )
    for d in map_details:
        key = (norm_table(d["omop_table"]), norm(d["omop_field"]))
        d["gold_sources"] = sorted(set(gold_readable.get(key, [])))

    micro_p = tp / (tp + fp) if (tp + fp) else 0.0
    micro_r = tp / (tp + fn) if (tp + fn) else 0.0
    micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) else 0.0

    macro_p = sum(d["precision"] for d in map_details) / len(map_details) if map_details else 0.0
    macro_r = sum(d["recall"] for d in map_details) / len(map_details) if map_details else 0.0
    macro_f1 = sum(d["f1"] for d in map_details) / len(map_details) if map_details else 0.0

    over_mapping_rate = fp / (tp + fp) if (tp + fp) else 0.0
    under_mapping_rate = fn / (tp + fn) if (tp + fn) else 0.0

    # --- FIXED metrics ---
    fixed_details = []
    fixed_ok = fixed_total = 0
    for key, expected_val in gold_fixed.items():
        fixed_total += 1
        meta = gold_meta[key]
        agent_has_field = has_any.get(key, False)
        agent_has_source = len(proposals.get(key, set())) > 0
        # Success if agent mentioned the field and did NOT attach a source
        # (constant is applied downstream / conserved)
        ok = agent_has_field and not agent_has_source
        # Also accept: agent did not mention it but reason says fixed convention
        if not ok and agent_has_field and agent_has_source:
            ok = False
        if ok:
            fixed_ok += 1
        fixed_details.append({
            "omop_table": meta["omop_table"],
            "omop_field": meta["omop_field"],
            "expected_value": expected_val,
            "agent_mentioned": agent_has_field,
            "agent_proposed_source": agent_has_source,
            "ok": ok,
        })
    fixed_accuracy = fixed_ok / fixed_total if fixed_total else 1.0

    # --- NO_MAPPING metrics ---
    no_map_details = []
    no_map_ok = no_map_total = 0
    for key in gold_no_mapping:
        no_map_total += 1
        meta = gold_meta[key]
        agent_has_source = len(proposals.get(key, set())) > 0
        ok = not agent_has_source
        if ok:
            no_map_ok += 1
        no_map_details.append({
            "omop_table": meta["omop_table"],
            "omop_field": meta["omop_field"],
            "agent_proposed_source": agent_has_source,
            "agent_sources_raw": raw_proposals.get(key, []),
            "ok": ok,
        })
    no_mapping_agreement = no_map_ok / no_map_total if no_map_total else 1.0

    # Global scoped score
    global_score = (
        0.45 * micro_f1
        + 0.25 * (1.0 - over_mapping_rate)
        + 0.20 * micro_r
        + 0.10 * no_mapping_agreement
    )

    return {
        "map": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "micro_precision": micro_p,
            "micro_recall": micro_r,
            "micro_f1": micro_f1,
            "macro_precision": macro_p,
            "macro_recall": macro_r,
            "macro_f1": macro_f1,
            "over_mapping_rate": over_mapping_rate,
            "under_mapping_rate": under_mapping_rate,
            "details": map_details,
        },
        "fixed": {
            "ok": fixed_ok,
            "total": fixed_total,
            "accuracy": fixed_accuracy,
            "details": fixed_details,
        },
        "no_mapping": {
            "ok": no_map_ok,
            "total": no_map_total,
            "agreement": no_mapping_agreement,
            "details": no_map_details,
        },
        "global_score": global_score,
    }


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def write_markdown_report(result: dict, out_path: Path) -> None:
    m = result["map"]
    fx = result["fixed"]
    nm = result["no_mapping"]

    lines = []
    lines.append("# Mapping Evaluation Report")
    lines.append("")
    lines.append("## Global Score")
    lines.append("")
    lines.append(f"**Scoped Global Score: {result['global_score']:.4f}**")
    lines.append("")
    lines.append("Formula: `0.45 * Micro-F1 + 0.25 * (1 - OverMappingRate) + 0.20 * Micro-Recall + 0.10 * NO_MAPPING agreement`")
    lines.append("")
    lines.append("## MAP fields (Precision / Recall / F1)")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| TP | {m['tp']} |")
    lines.append(f"| FP (over-mapping) | {m['fp']} |")
    lines.append(f"| FN (under-mapping) | {m['fn']} |")
    lines.append(f"| Micro Precision | {m['micro_precision']:.4f} |")
    lines.append(f"| Micro Recall | {m['micro_recall']:.4f} |")
    lines.append(f"| Micro F1 | {m['micro_f1']:.4f} |")
    lines.append(f"| Macro Precision | {m['macro_precision']:.4f} |")
    lines.append(f"| Macro Recall | {m['macro_recall']:.4f} |")
    lines.append(f"| Macro F1 | {m['macro_f1']:.4f} |")
    lines.append(f"| Over-mapping rate | {m['over_mapping_rate']:.4f} |")
    lines.append(f"| Under-mapping rate | {m['under_mapping_rate']:.4f} |")
    lines.append("")
    lines.append("### Per-field MAP details")
    lines.append("")
    lines.append("| Table | Field | Gold sources | Agent sources | P | R | F1 | TP | FP | FN |")
    lines.append("|-------|-------|--------------|---------------|---|---|----|----|----|----|")
    for d in sorted(m["details"], key=lambda x: (x["omop_table"], x["omop_field"])):
        gold = ", ".join(d["gold_sources"]) if d["gold_sources"] else "—"
        agent = ", ".join(f"{a}.{b}" for a, b in d["agent_sources_raw"]) if d["agent_sources_raw"] else "—"
        lines.append(
            f"| {d['omop_table']} | {d['omop_field']} | {gold} | {agent} | "
            f"{d['precision']:.2f} | {d['recall']:.2f} | {d['f1']:.2f} | "
            f"{d['tp']} | {d['fp']} | {d['fn']} |"
        )
    lines.append("")
    lines.append("## FIXED fields (`*_type_concept_id`)")
    lines.append("")
    lines.append(f"**Accuracy: {fx['accuracy']:.4f}** ({fx['ok']}/{fx['total']})")
    lines.append("")
    lines.append("| Table | Field | Expected value | Mentioned | Proposed source? | OK |")
    lines.append("|-------|-------|----------------|-----------|------------------|----|")
    for d in sorted(fx["details"], key=lambda x: (x["omop_table"], x["omop_field"])):
        lines.append(
            f"| {d['omop_table']} | {d['omop_field']} | {d['expected_value']} | "
            f"{d['agent_mentioned']} | {d['agent_proposed_source']} | {d['ok']} |"
        )
    lines.append("")
    lines.append("## NO_MAPPING fields")
    lines.append("")
    lines.append(f"**Agreement: {nm['agreement']:.4f}** ({nm['ok']}/{nm['total']})")
    lines.append("")
    lines.append("| Table | Field | Agent proposed source? | Sources | OK |")
    lines.append("|-------|-------|------------------------|---------|----|")
    for d in sorted(nm["details"], key=lambda x: (x["omop_table"], x["omop_field"])):
        src = ", ".join(f"{a}.{b}" for a, b in d["agent_sources_raw"]) if d["agent_sources_raw"] else "—"
        lines.append(
            f"| {d['omop_table']} | {d['omop_field']} | {d['agent_proposed_source']} | {src} | {d['ok']} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Semantic fields (`*_concept_id`, `*_source_concept_id` except type) are **out of scope**.")
    lines.append("- FIXED fields are successful when the agent acknowledges the field without attaching a source column.")
    lines.append("- Over-mapping = agent sources not in gold; under-mapping = gold sources missing from agent.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_details_csv(result: dict, out_path: Path) -> None:
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "category", "omop_table", "omop_field", "gold_sources", "agent_sources",
            "precision", "recall", "f1", "tp", "fp", "fn", "ok", "notes"
        ])
        for d in result["map"]["details"]:
            writer.writerow([
                "MAP",
                d["omop_table"],
                d["omop_field"],
                ";".join(d["gold_sources"]),
                ";".join(f"{a}.{b}" for a, b in d["agent_sources_raw"]),
                f"{d['precision']:.4f}",
                f"{d['recall']:.4f}",
                f"{d['f1']:.4f}",
                d["tp"],
                d["fp"],
                d["fn"],
                "",
                "",
            ])
        for d in result["fixed"]["details"]:
            writer.writerow([
                "FIXED",
                d["omop_table"],
                d["omop_field"],
                d["expected_value"],
                "",
                "", "", "",
                "", "", "",
                d["ok"],
                f"mentioned={d['agent_mentioned']}; proposed_source={d['agent_proposed_source']}",
            ])
        for d in result["no_mapping"]["details"]:
            writer.writerow([
                "NO_MAPPING",
                d["omop_table"],
                d["omop_field"],
                "",
                ";".join(f"{a}.{b}" for a, b in d["agent_sources_raw"]),
                "", "", "",
                "", "", "",
                d["ok"],
                "",
            ])


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate agent mapping vs scoped gold standard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pass the CSV produced by your system
  python evaluate_mapping.py --agent /path/to/mon_rapport.csv

  # Full example
  python evaluate_mapping.py \\
      --gold  gold_standard_scoped.csv \\
      --agent mon_systeme_output.csv \\
      --out-md  evaluation_report.md \\
      --out-csv evaluation_details.csv
        """,
    )
    parser.add_argument(
        "--gold",
        type=Path,
        default=Path("/home/workdir/artifacts/gold_standard_scoped.csv"),
        help="Gold standard CSV (MAP / FIXED / NO_MAPPING)",
    )
    parser.add_argument(
        "--agent",
        "--report",
        dest="agent",
        type=Path,
        default=Path("/home/workdir/attachments/report.csv"),
        help="CSV generated by your system/agents (structural mapping report)",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("/home/workdir/artifacts/evaluation_report.md"),
        help="Output markdown report path",
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("/home/workdir/artifacts/evaluation_details.csv"),
        help="Output per-field details CSV path",
    )
    args = parser.parse_args()

    if not args.gold.exists():
        raise SystemExit(f"Gold file not found: {args.gold}")
    if not args.agent.exists():
        raise SystemExit(f"Agent report not found: {args.agent}")

    print(f"Gold standard : {args.gold}")
    print(f"Agent report  : {args.agent}")
    print()

    gold = load_gold(args.gold)
    agent = load_agent_report(args.agent)
    result = evaluate(gold, agent)

    write_markdown_report(result, args.out_md)
    write_details_csv(result, args.out_csv)

    m = result["map"]
    print("=" * 60)
    print("MAPPING EVALUATION SUMMARY")
    print("=" * 60)
    #print(f"Global Score     : {result['global_score']:.4f}")
    print(f"Precision  : {m['micro_precision']:.4f}")
    print(f"Recall     : {m['micro_recall']:.4f}")
    print(f"F1         : {m['micro_f1']:.4f}")
    #print(f"Macro F1         : {m['macro_f1']:.4f}")
    print(f"Over-mapping rate: {m['over_mapping_rate']:.4f}")
    print(f"Under-mapping    : {m['under_mapping_rate']:.4f}")
    print(f"FIXED accuracy   : {result['fixed']['accuracy']:.4f} ({result['fixed']['ok']}/{result['fixed']['total']})")
    print(f"NO_MAPPING agree : {result['no_mapping']['agreement']:.4f} ({result['no_mapping']['ok']}/{result['no_mapping']['total']})")
    print("=" * 60)
    print(f"Markdown report  : {args.out_md}")
    print(f"Details CSV      : {args.out_csv}")



if __name__ == "__main__":
    main()
