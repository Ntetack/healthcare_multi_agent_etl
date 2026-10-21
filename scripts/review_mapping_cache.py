"""
Reviews and corrects entries in the persistent mapping cache
(pipeline_meta.mapping_cache) - runs completely independently of the
pipeline itself, at any time, before or after any run.

Reminder of the design principle: the pipeline NEVER waits for this
review. Every cache entry is used immediately and autonomously the
moment it exists, whether 'llm_suggested' or 'human_confirmed'. This
script exists purely so a human can, AFTER THE FACT, correct a mistake
once and have it stick permanently for every future batch of that
source - never to gate execution.

Usage:
    # List everything still awaiting a human look, for one source
    python scripts/review_mapping_cache.py list --source hospital_b --status llm_suggested

    # List everything, across all sources
    python scripts/review_mapping_cache.py list

    # Correct (or simply confirm as-is) one specific entry
    python scripts/review_mapping_cache.py confirm \\
        --source hospital_b --table labevents --field ITEMID \\
        --join-table D_LABITEMS --join-key-source ITEMID --join-key-target ITEMID \\
        --resolved-column LOINC_CODE --resolved-kind code \\
        --confirmed-by "your_name"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tools.mapping.mapping_cache import (
    confirm_resolution,
    ensure_mapping_cache_table,
    get_cached_resolution,
    list_cache_entries,
)


def cmd_list(args):
    entries = list_cache_entries(source_name=args.source, status=args.status)
    if not entries:
        print("Aucune entrée trouvée pour ces filtres.")
        return

    print(f"{len(entries)} entrée(s) :\n")
    for e in entries:
        marker = "✅" if e["status"] == "human_confirmed" else "🤖"
        print(f"{marker} [{e['status']}] {e['source_name']} / {e['table_name']}.{e['field_name']} ({e['cache_kind']})")
        for key, val in e["resolution"].items():
            print(f"      {key}: {val}")
        if e.get("confirmed_by"):
            print(f"      confirmé par {e['confirmed_by']} le {e['confirmed_at']}")
        print()


def cmd_confirm(args):
    existing = get_cached_resolution(args.source, "local_vocab_join", args.table, args.field)
    if existing:
        print(f"Entrée actuelle ({existing.get('_cache_status', 'inconnue')}) :")
        for key, val in existing.items():
            if not key.startswith("_"):
                print(f"  {key}: {val}")
        print()

    resolution = {
        "join_table": args.join_table,
        "join_key_source": args.join_key_source,
        "join_key_target": args.join_key_target,
        "resolved_column": args.resolved_column,
        "resolved_kind": args.resolved_kind,
    }
    confirm_resolution(args.source, "local_vocab_join", args.table, args.field, resolution, confirmed_by=args.confirmed_by)
    print(f"✅ Confirmée : {args.source} / {args.table}.{args.field} -> {resolution}")
    print("Cette correction sera utilisée pour tous les prochains batches de cette source, sans jamais être écrasée automatiquement.")


def main():
    ensure_mapping_cache_table()

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List cache entries")
    list_parser.add_argument("--source", default=None, help="Filter by source name")
    list_parser.add_argument("--status", default=None, choices=["llm_suggested", "human_confirmed"])
    list_parser.set_defaults(func=cmd_list)

    confirm_parser = subparsers.add_parser("confirm", help="Confirm or correct one local-vocab-join entry")
    confirm_parser.add_argument("--source", required=True)
    confirm_parser.add_argument("--table", required=True)
    confirm_parser.add_argument("--field", required=True)
    confirm_parser.add_argument("--join-table", required=True)
    confirm_parser.add_argument("--join-key-source", required=True)
    confirm_parser.add_argument("--join-key-target", required=True)
    confirm_parser.add_argument("--resolved-column", required=True)
    confirm_parser.add_argument("--resolved-kind", required=True, choices=["code", "text"])
    confirm_parser.add_argument("--confirmed-by", required=True, help="Your name, for the audit trail")
    confirm_parser.set_defaults(func=cmd_confirm)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
