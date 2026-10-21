"""A *_source_value should keep the CODE the source recorded (declared
standard) rather than a descriptive column: the model is told which
columns carry a declared vocabulary, and the prompt says what to do with it."""
import json

import pandas as pd

from app.agents.mapping import MappingAgent
from app.prompts.structural_target_mapping_prompt import STRUCTURAL_TARGET_MAPPING_PROMPT

TABLES = {"PRESCRIPTIONS": pd.DataFrame({"drug": ["Acetaminophen"], "ndc": ["00677178110"], "route": ["PO"]})}
CFG = {"tables": {"prescriptions": {"ndc": "NDC", "drug": None, "route": "local", "gsn": "LOINC"}}}


def _summary(cfg):
    return MappingAgent._build_tables_summary(TABLES, {}, cfg)["PRESCRIPTIONS"]


def test_a_declared_standard_is_shown_on_its_column():
    s = _summary(CFG)
    assert s["ndc"]["declared_standard"] == "NDC"
    assert "declared_standard" not in s["drug"]          # nothing declared
    assert "declared_standard" not in s["route"]         # 'local' is not a vocabulary
    assert "gsn" not in s                                # a declaration for an absent column is ignored


def test_without_metadata_the_summary_is_unchanged():
    assert _summary(None) == _summary({})
    assert all("declared_standard" not in v for v in _summary(None).values())


def test_the_summary_remains_serialisable_for_the_prompt():
    json.dumps(_summary(CFG), default=str)


def test_the_prompt_asks_for_the_code_before_the_description():
    assert "declared_standard" in STRUCTURAL_TARGET_MAPPING_PROMPT
    assert "rather than a column of names or descriptions" in STRUCTURAL_TARGET_MAPPING_PROMPT
    STRUCTURAL_TARGET_MAPPING_PROMPT.format(target_table="t", target_fields="[]", tables_summary="{}")
