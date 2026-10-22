from app.tools.mapping.semantic.semantic_mapper import STANDARD_TO_VOCABULARY


def test_cpt_is_an_alias_of_cpt4():
    assert STANDARD_TO_VOCABULARY["CPT"] == STANDARD_TO_VOCABULARY["CPT4"] == ["CPT4"]
