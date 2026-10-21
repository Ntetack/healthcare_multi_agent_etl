"""
Entry point. Usage:
    python -m app.main --source hospital_a --execution-id RUN-001
"""
from __future__ import annotations

import argparse
import re
import time
import uuid

from app.graph.workflow import build_workflow
from app.tools.common.metrics import format_summary, summarize_run, write_summary
from app.tools.data.folder_watcher import find_next_folder
from app.tools.data.metadata_loader import source_root_path
from app.tools.mapping.mapping_snapshot import (
    ON_MISMATCH_CHOICES,
    save_snapshot_from_final_state,
    snapshot_path,
)


def _build_execution_id(source_name: str) -> str:
    """RUN-<batch_name>-<random suffix> when a batch can be identified
    ahead of time, so run folders are recognizable at a glance instead
    of an opaque random id - falls back to the old random-only form if
    no new batch is found (Profiling will itself report
    NOTHING_TO_PROCESS as before) or discovery fails for any reason
    (e.g. a malformed source_metadata.yaml - naming the run should
    never be why a run fails to start)."""
    suffix = uuid.uuid4().hex[:8]
    try:
        next_folder = find_next_folder(source_name, source_root_path(source_name))
    except Exception:
        next_folder = None
    if next_folder is None:
        return f"RUN-{suffix}"
    batch_name = re.sub(r"[^A-Za-z0-9_-]", "_", next_folder.name)
    return f"RUN-{batch_name}-{suffix}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Source name as declared in source_metadata.yaml")
    parser.add_argument("--execution-id", default=None)
    parser.add_argument(
        "--save-mapping", metavar="NAME", default=None,
        help="After a run that reached promotion, save its complete mapping as mappings/<source>/NAME.json",
    )
    parser.add_argument(
        "--overwrite-mapping", action="store_true",
        help="Allow --save-mapping to replace an existing snapshot of the same name",
    )
    parser.add_argument(
        "--replay-mapping", metavar="NAME", default=None,
        help="Replay the mapping snapshot NAME of this source instead of asking the model again",
    )
    parser.add_argument(
        "--replay-on-mismatch", choices=ON_MISMATCH_CHOICES, default="fallback",
        help="What to do with a decision the snapshot cannot provide for this batch: resolve it the "
             "normal way (fallback, default) or stop the run (fail)",
    )
    args = parser.parse_args()

    # Fail before the run, not after: both checks only concern files.
    if args.save_mapping and not args.overwrite_mapping and snapshot_path(args.source, args.save_mapping).exists():
        parser.error(
            f"mapping snapshot '{args.save_mapping}' already exists for source '{args.source}' "
            f"(use --overwrite-mapping to replace it)"
        )
    if args.replay_mapping and not snapshot_path(args.source, args.replay_mapping).exists():
        parser.error(f"mapping snapshot '{args.replay_mapping}' not found for source '{args.source}'")

    execution_id = args.execution_id or _build_execution_id(args.source)
    workflow = build_workflow()

    initial_state = {
        "execution_id": execution_id,
        "source_name": args.source,
        "retry_counts": {},
    }
    if args.replay_mapping:
        initial_state["mapping_replay"] = {"name": args.replay_mapping, "on_mismatch": args.replay_on_mismatch}

    started = time.perf_counter()
    final_state = workflow.invoke(initial_state)
    wall_seconds = round(time.perf_counter() - started, 3)
    print(f"Run {execution_id} finished. Final state keys: {list(final_state.keys())}")

    # Wall-clock time of the whole graph is slightly larger than the sum of
    # the agents' times (routing, state merging, Coordinator hops).
    write_summary(
        execution_id,
        extra={"wall_clock_seconds": wall_seconds, "mapping_replay": args.replay_mapping},
    )
    if args.save_mapping:
        saved, message = save_snapshot_from_final_state(
            final_state, args.save_mapping, overwrite=args.overwrite_mapping
        )
        print(f"Mapping snapshot saved to {saved}" if saved else f"Mapping snapshot NOT saved: {message}.")

    summary = summarize_run(execution_id)
    if summary["agents"]:
        print(f"\nExecution metrics (wall clock: {wall_seconds:.1f} s)\n")
        print(format_summary(summary))


if __name__ == "__main__":
    main()