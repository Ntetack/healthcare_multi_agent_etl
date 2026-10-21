#!/usr/bin/env python3
"""
Evaluate agent structural mapping against gold standard (MAP only).

Gold CSV columns (scoped format):
  omop_table, omop_field, expected_source_table, expected_source_field,
  status, expected_value, notes

status should be MAP for structural rows. FIXED / NO_MAPPING rows are ignored
for scoring (structural focus only).

Also accepts report-like gold:
  section, status, target_table, target_field, source_table, source_field, ...
  (OK rows with source become MAP; FAIL rows skipped)

Agent report:
  structural_field rows with target_table, target_field, source_table, source_field

Usage:
  python evaluate_mapping.py \\
    --gold gold_standard_scoped.csv \\
    --agent path/to/report.csv \\
    --out-md evaluation_report.md \\
    --out-csv evaluation_details.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Normalization
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
    """Exclude pure semantic concept fields from structural eval.
    Keep *_type_concept_id out of MAP scoring too (fixed conventions).
    """
    f = field.lower()
    if f.endswith("_type_concept_id"):
        return True
    if f.endswith("_source_concept_id") or f.endswith("_concept_id"):
        return True
    return False


# ---------------------------------------------------------------------------
# Resolve agent path (file or directory)
# ---------------------------------------------------------------------------

def resolve_agent_csv(path: Path) -> Path:
    if path.is_file():
        return path
    if path.is_dir():
        candidates = [
            path / "report.csv",
            path / "structural_mapping.csv",
            path / "mapping.csv",
            path / "agent_report.csv",
        ]
        # any csv in dir
        csvs = sorted(path.glob("*.csv"))
        for c in candidates:
            if c.exists():
                return c
        if len(csvs) == 1:
            return csvs[0]
        if csvs:
            # prefer name containing report or structural or mapping
            for c in csvs:
                n = c.name.lower()
                if any(k in n for k in ("report", "structural", "mapping")):
                    return c
            return csvs[0]
        raise SystemExit(f"No CSV found in agent directory: {path}")
    raise SystemExit(f"Agent path not found: {path}")


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_gold(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = [c.strip() for c in (reader.fieldnames or [])]

        if "omop_table" in fieldnames:
            for r in reader:
                status = (r.get("status") or "MAP").strip().upper() or "MAP"
                if status != "MAP":
                    continue
                omop_table = (r.get("omop_table") or "").strip()
                omop_field = (r.get("omop_field") or "").strip()
                src_t = (r.get("expected_source_table") or "").strip()
                src_f = (r.get("expected_source_field") or "").strip()
                if not omop_table or not omop_field:
                    continue
                if not src_t or not src_f:
                    continue
                if is_semantic_field(omop_field):
                    continue
                rows.append({
                    "omop_table": omop_table,
                    "omop_field": omop_field,
                    "expected_source_table": src_t,
                    "expected_source_field": src_f,
                    "status": "MAP",
                    "expected_value": (r.get("expected_value") or "").strip(),
                    "notes": (r.get("notes") or "").strip(),
                })

        elif "target_table" in fieldnames:
            for r in reader:
                section = (r.get("section") or "").strip().lower()
                if section and section not in ("structural_field", ""):
                    continue
                st = (r.get("status") or "").strip().upper()
                if st == "FAIL":
                    continue
                omop_table = (r.get("target_table") or "").strip()
                omop_field = (r.get("target_field") or "").strip()
                src_t = (r.get("source_table") or "").strip()
                src_f = (r.get("source_field") or "").strip()
                if not omop_table or not omop_field or not src_t or not src_f:
                    continue
                if is_semantic_field(omop_field):
                    continue
                rows.append({
                    "omop_table": omop_table,
                    "omop_field": omop_field,
                    "expected_source_table": src_t,
                    "expected_source_field": src_f,
                    "status": "MAP",
                    "expected_value": "",
                    "notes": (r.get("reason") or "").strip(),
                })
        else:
            raise SystemExit(
                f"Gold CSV columns not recognized: {fieldnames}\n"
                "Expected scoped (omop_table, omop_field, ...) "
                "or report-like (target_table, target_field, source_table, ...)."
            )

    if not rows:
        raise SystemExit(f"No MAP rows loaded from gold: {path}")
    return rows


def load_agent_report(path: Path) -> List[dict]:
    path = resolve_agent_csv(path)
    rows: List[dict] = []
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
            if is_semantic_field(target_field):
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
    proposals = defaultdict(set)
    has_any = defaultdict(bool)
    raw_proposals = defaultdict(list)

    for r in agent_rows:
        key = (norm_table(r["target_table"]), norm(r["target_field"]))
        has_any[key] = True
        st, sf = r["source_table"], r["source_field"]
        if st and sf:
            proposals[key].add((norm_table(st), norm(sf)))
            raw_proposals[key].append((st, sf))

    return proposals, has_any, raw_proposals


# ---------------------------------------------------------------------------
# Evaluation (MAP only)
# ---------------------------------------------------------------------------

def evaluate(gold_rows: List[dict], agent_rows: List[dict]) -> dict:
    proposals, has_any, raw_proposals = build_agent_index(agent_rows)

    gold_map: Dict[Tuple[str, str], Set[Tuple[str, str]]] = defaultdict(set)
    gold_meta: Dict[Tuple[str, str], dict] = {}
    gold_readable: Dict[Tuple[str, str], List[str]] = defaultdict(list)

    for g in gold_rows:
        key = (norm_table(g["omop_table"]), norm(g["omop_field"]))
        gold_meta[key] = g
        gold_map[key].add((
            norm_table(g["expected_source_table"]),
            norm(g["expected_source_field"]),
        ))
        gold_readable[key].append(
            f"{g['expected_source_table']}.{g['expected_source_field']}"
        )

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

        prec = _tp / (_tp + _fp) if (_tp + _fp) else (1.0 if not agent_sources and not gold_sources else 0.0)
        rec = _tp / (_tp + _fn) if (_tp + _fn) else (1.0 if not gold_sources else 0.0)
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0

        meta = gold_meta[key]
        map_details.append({
            "omop_table": meta["omop_table"],
            "omop_field": meta["omop_field"],
            "gold_sources": sorted(set(gold_readable.get(key, []))),
            "agent_sources_raw": raw_proposals.get(key, []),
            "tp": _tp,
            "fp": _fp,
            "fn": _fn,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "notes": meta.get("notes", ""),
        })

    micro_p = tp / (tp + fp) if (tp + fp) else 0.0
    micro_r = tp / (tp + fn) if (tp + fn) else 0.0
    micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) else 0.0

    macro_p = sum(d["precision"] for d in map_details) / len(map_details) if map_details else 0.0
    macro_r = sum(d["recall"] for d in map_details) / len(map_details) if map_details else 0.0
    macro_f1 = sum(d["f1"] for d in map_details) / len(map_details) if map_details else 0.0

    over_mapping_rate = fp / (tp + fp) if (tp + fp) else 0.0
    under_mapping_rate = fn / (tp + fn) if (tp + fn) else 0.0

    # Extra agent proposals on OMOP fields not in gold (informational)
    gold_keys = set(gold_map.keys())
    extra = []
    for key, srcs in proposals.items():
        if key not in gold_keys and srcs:
            raw = raw_proposals.get(key, [])
            extra.append({
                "omop_table": raw[0][0] if False else key[0],
                "omop_field": key[1],
                "agent_sources_raw": raw,
            })
    # recover readable table/field from agent rows
    extra_readable = []
    seen = set()
    for r in agent_rows:
        key = (norm_table(r["target_table"]), norm(r["target_field"]))
        if key in gold_keys or key in seen:
            continue
        if not r["source_table"] or not r["source_field"]:
            continue
        seen.add(key)
        extra_readable.append({
            "omop_table": r["target_table"],
            "omop_field": r["target_field"],
            "agent_sources_raw": raw_proposals.get(key, []),
        })

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
        "extra_agent_fields": extra_readable,
        "n_gold_fields": len(gold_map),
        "n_gold_map_rows": len(gold_rows),
    }


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_markdown_report(result: dict, out_path: Path) -> None:
    m = result["map"]
    lines = [
        "# Structural Mapping Evaluation Report",
        "",
        "## Summary (MAP only)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Gold fields (unique table.field) | {result['n_gold_fields']} |",
        f"| Gold MAP rows (sources) | {result['n_gold_map_rows']} |",
        f"| TP | {m['tp']} |",
        f"| FP (over-mapping) | {m['fp']} |",
        f"| FN (under-mapping) | {m['fn']} |",
        f"| **Micro Precision** | **{m['micro_precision']:.4f}** |",
        f"| **Micro Recall** | **{m['micro_recall']:.4f}** |",
        f"| **Micro F1** | **{m['micro_f1']:.4f}** |",
        f"| Macro Precision | {m['macro_precision']:.4f} |",
        f"| Macro Recall | {m['macro_recall']:.4f} |",
        f"| Macro F1 | {m['macro_f1']:.4f} |",
        f"| Over-mapping rate | {m['over_mapping_rate']:.4f} |",
        f"| Under-mapping rate | {m['under_mapping_rate']:.4f} |",
        "",
        "### Per-field details",
        "",
        "| Table | Field | Gold sources | Agent sources | P | R | F1 | TP | FP | FN |",
        "|-------|-------|--------------|---------------|---|---|----|----|----|----|",
    ]
    for d in sorted(m["details"], key=lambda x: (x["omop_table"], x["omop_field"])):
        gold = ", ".join(d["gold_sources"]) if d["gold_sources"] else "—"
        agent = ", ".join(f"{a}.{b}" for a, b in d["agent_sources_raw"]) if d["agent_sources_raw"] else "—"
        lines.append(
            f"| {d['omop_table']} | {d['omop_field']} | {gold} | {agent} | "
            f"{d['precision']:.2f} | {d['recall']:.2f} | {d['f1']:.2f} | "
            f"{d['tp']} | {d['fp']} | {d['fn']} |"
        )

    if result["extra_agent_fields"]:
        lines += [
            "",
            "### Agent fields not in gold (informational)",
            "",
            "| Table | Field | Agent sources |",
            "|-------|-------|---------------|",
        ]
        for e in sorted(result["extra_agent_fields"], key=lambda x: (x["omop_table"], x["omop_field"])):
            src = ", ".join(f"{a}.{b}" for a, b in e["agent_sources_raw"]) or "—"
            lines.append(f"| {e['omop_table']} | {e['omop_field']} | {src} |")

    lines += [
        "",
        "## Notes",
        "",
        "- Only **structural MAP** pairs are scored (source_table + source_field).",
        "- `*_concept_id` / `*_source_concept_id` / `*_type_concept_id` are excluded (semantic or fixed).",
        "- TP = agent source ∈ gold sources for that field.",
        "- FP = agent proposed a source not in gold (over-mapping).",
        "- FN = gold source missing from agent (under-mapping).",
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_details_csv(result: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "category", "omop_table", "omop_field", "gold_sources", "agent_sources",
            "precision", "recall", "f1", "tp", "fp", "fn", "notes",
        ])
        for d in result["map"]["details"]:
            w.writerow([
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
                d.get("notes", ""),
            ])
        for e in result["extra_agent_fields"]:
            w.writerow([
                "EXTRA_AGENT",
                e["omop_table"],
                e["omop_field"],
                "",
                ";".join(f"{a}.{b}" for a, b in e["agent_sources_raw"]),
                "", "", "", "", "", "",
                "field not present in gold MAP set",
            ])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate structural agent mapping vs gold (MAP only)",
    )
    parser.add_argument(
        "--gold",
        type=Path,
        required=True,
        help="Gold CSV (scoped omop_table... or report-like target_table...)",
    )
    parser.add_argument(
        "--agent",
        "--report",
        dest="agent",
        type=Path,
        required=True,
        help="Agent report CSV or directory containing it",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("mapping_evaluation_report/report.md"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("mapping_evaluation_report/evaluation_details.csv"),
    )
    args = parser.parse_args()

    if not args.gold.exists():
        raise SystemExit(f"Gold file not found: {args.gold}")
    if not args.agent.exists():
        raise SystemExit(f"Agent path not found: {args.agent}")

    agent_file = resolve_agent_csv(args.agent)
    print(f"Gold standard : {args.gold}")
    print(f"Agent report  : {agent_file}")
    print()

    gold = load_gold(args.gold)
    agent = load_agent_report(agent_file)
    print(f"Gold MAP rows : {len(gold)}")
    print(f"Agent structural rows : {len(agent)}")
    print()

    result = evaluate(gold, agent)
    write_markdown_report(result, args.out_md)
    write_details_csv(result, args.out_csv)

    m = result["map"]
    print("=" * 60)
    print("STRUCTURAL MAPPING EVALUATION")
    print("=" * 60)
    print(f"Precision         : {m['micro_precision']:.4f}")
    print(f"Recall            : {m['micro_recall']:.4f}")
    print(f"F1                : {m['micro_f1']:.4f}")
    print(f"Over-mapping rate : {m['over_mapping_rate']:.4f}")
    print(f"Under-mapping rate: {m['under_mapping_rate']:.4f}")
    print(f"TP / FP / FN      : {m['tp']} / {m['fp']} / {m['fn']}")
    print("=" * 60)
    print(f"Markdown : {args.out_md}")
    print(f"Details  : {args.out_csv}")


if __name__ == "__main__":
    main()
