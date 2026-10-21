"""
Runs ONLY the Profiling Agent, in isolation - useful to validate/iterate
on profiling (folder detection, table discovery, LLM interpretation)
without needing the rest of the pipeline (mapping/transformation/
validation/loading) to be finished or bug-free yet.

Usage:
    python scripts/test_profiling_only.py --source ln_hospital
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.profiling import ProfilingAgent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--execution-id", default=None)
    args = parser.parse_args()

    execution_id = args.execution_id or f"PROFILE-TEST-{uuid.uuid4().hex[:8]}"
    state = {"execution_id": execution_id, "source_name": args.source}

    agent = ProfilingAgent()
    result = agent.run(state)

    print(f"\n=== Status: {result.status} ===")
    print(f"Reasoning: {result.reasoning_summary}\n")
    print(json.dumps(result.output, indent=2, default=str))
    print(f"\nFull result written to: runs/{execution_id}/profiling/result.json")


if __name__ == "__main__":
    main()
