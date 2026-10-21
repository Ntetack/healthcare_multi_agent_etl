"""ICD9 codes must be normalized to OMOP's dotted format before
matching - confirmed by official OHDSI documentation ('All ICD9CM
codes are represented in the format containing the dot. For example,
... concept_code "307.50"') - a property of the ICD9 coding system
itself (MIMIC-III's raw exports store it undotted), not specific to
any one source."""
from app.tools.mapping.semantic.semantic_mapper import _normalize_icd9_code


def test_the_exact_officially_documented_example():
    assert _normalize_icd9_code("30750", is_procedure=False) == "307.50"


def test_e_code_diagnosis():
    assert _normalize_icd9_code("E9330", is_procedure=False) == "E933.0"


def test_v_code_diagnosis():
    assert _normalize_icd9_code("V707", is_procedure=False) == "V70.7"


def test_procedure_code_two_digit_prefix():
    assert _normalize_icd9_code("3893", is_procedure=True) == "38.93"


def test_already_dotted_code_left_unchanged():
    assert _normalize_icd9_code("307.50", is_procedure=False) == "307.50"


def test_bare_three_digit_category_code_needs_no_dot():
    assert _normalize_icd9_code("486", is_procedure=False) == "486"
