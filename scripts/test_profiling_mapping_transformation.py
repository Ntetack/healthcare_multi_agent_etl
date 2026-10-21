"""
Runs Profiling -> Mapping -> Transformation, in isolation - stops there,
without Validation/Loading (not yet validated end-to-end).

Usage:
    python scripts/test_profiling_mapping_transformation.py --source hospital_a
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
from app.agents.transformation import TransformationAgent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--execution-id", default=None)
    args = parser.parse_args()

    execution_id = args.execution_id or f"PMT-TEST-{uuid.uuid4().hex[:8]}"
    state = {"execution_id": execution_id, "source_name": args.source}

    print(f"=== Profiling ({execution_id}) ===")
    profiling_result = ProfilingAgent().run(state)
    print(f"Status: {profiling_result.status} - {profiling_result.reasoning_summary}\n")
    if profiling_result.output.get("status") == "NOTHING_TO_PROCESS":
        print("Nothing to process - stopping.")
        return

    print("=== Mapping ===")
    mapping_result = MappingAgent().run(state)
    state["mapping_output"] = mapping_result.output  # normally forwarded by mapping_node in the real graph
    print(f"Status: {mapping_result.status} - {mapping_result.reasoning_summary}\n")

    print("=== Transformation ===")
    transformation_result = TransformationAgent().run(state)
    print(f"Status: {transformation_result.status} - {transformation_result.reasoning_summary}\n")
    print(json.dumps(transformation_result.output, indent=2, default=str))

    print(f"\nFull results written under runs/{execution_id}/")


if __name__ == "__main__":
    main()
