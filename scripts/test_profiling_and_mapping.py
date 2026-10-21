"""
Runs Profiling THEN Mapping, in isolation - stops there, without
Transformation/Validation/Loading (not yet validated end-to-end).
Useful to check the two agents together: does Mapping correctly receive
what Profiling produced (_raw_tables, batch_metadata)?

Usage:
    python scripts/test_profiling_and_mapping.py --source hospital_a
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.mapping import MappingAgent
from app.agents.profiling import ProfilingAgent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--execution-id", default=None)
    args = parser.parse_args()

    execution_id = args.execution_id or f"PROFMAP-TEST-{uuid.uuid4().hex[:8]}"
    state = {"execution_id": execution_id, "source_name": args.source}

    print(f"=== Profiling ({execution_id}) ===")
    profiling_result = ProfilingAgent().run(state)
    print(f"Status: {profiling_result.status}")
    print(f"Reasoning: {profiling_result.reasoning_summary}\n")

    if profiling_result.output.get("status") == "NOTHING_TO_PROCESS":
        print("Nothing to process - stopping before Mapping.")
        return

    print(f"=== Mapping ({execution_id}) ===")
    mapping_result = MappingAgent().run(state)
    print(f"Status: {mapping_result.status}")
    print(f"Reasoning: {mapping_result.reasoning_summary}\n")
    print(json.dumps(mapping_result.output, indent=2, default=str))

    print(f"\nFull results written to: runs/{execution_id}/profiling/ and runs/{execution_id}/mapping/")


if __name__ == "__main__":
    main()
