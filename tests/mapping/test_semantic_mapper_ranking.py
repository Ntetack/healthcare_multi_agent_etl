"""Regression test for a real bug: searching Gender for 'M' or 'Male'
could return FEMALE instead of MALE, since 'FEMALE' contains 'MALE' as
a substring and the old query had no result ordering."""
from app.tools.mapping.semantic.semantic_mapper import _match_rank


def test_exact_code_ranks_above_substring_match():
    male = {"concept_code": "M", "concept_name": "MALE"}
    female = {"concept_code": "F", "concept_name": "FEMALE"}

    # Searching "M": MALE matches exactly on code (rank 0); FEMALE only
    # matches because its name contains "M" as a substring (rank 2).
    assert _match_rank(male, "M") < _match_rank(female, "M")


def test_exact_name_ranks_above_substring_match_for_male_search():
    male = {"concept_code": "M", "concept_name": "MALE"}
    female = {"concept_code": "F", "concept_name": "FEMALE"}

    # Searching "Male": MALE matches its name exactly, case-insensitive
    # (rank 1); FEMALE only matches via substring ("fe-MALE", rank 2).
    assert _match_rank(male, "Male") < _match_rank(female, "Male")


def test_female_search_is_unambiguous():
    male = {"concept_code": "M", "concept_name": "MALE"}
    female = {"concept_code": "F", "concept_name": "FEMALE"}

    assert _match_rank(female, "F") < _match_rank(male, "F")
    assert _match_rank(female, "Female") < _match_rank(male, "Female")


def test_normalize_text_trims_and_collapses_whitespace():
    from app.tools.mapping.semantic.semantic_mapper import normalize_text
    assert normalize_text("  Hispanic  ") == "Hispanic"
    assert normalize_text("Hispanic   Latino") == "Hispanic Latino"
    assert normalize_text("Hispanic") == "Hispanic"


def test_confidence_tiers_reflect_match_quality():
    from app.tools.mapping.semantic.semantic_mapper import _CONFIDENCE_BY_RANK
    assert _CONFIDENCE_BY_RANK[0] > _CONFIDENCE_BY_RANK[1] > _CONFIDENCE_BY_RANK[2]


def test_negation_variant_general_rule():
    from app.tools.mapping.semantic.semantic_mapper import negation_variant
    assert negation_variant("nonhispanic") == "not hispanic"
    assert negation_variant("nonsmoker") == "not smoker"
    assert negation_variant("Nonresponder") == "not responder"
    # No false positives on words that just happen to start with "non"
    # but aren't a negation-prefix pattern intended here - still returns
    # a variant per the simple rule (documented as general, not perfect);
    # words with no letter right after "non" don't match.
    assert negation_variant("hispanic") is None
    assert negation_variant("non") is None  # nothing after the prefix
