"""Regression test for the empty-value false-positive bug found in
production output: an empty source_value must never match any concept
(previously, ILIKE '%%' matched everything)."""
from app.tools.mapping.semantic.semantic_mapper import search_concept


def test_empty_source_value_returns_no_candidates():
    assert search_concept("", "SNOMED") == []


def test_whitespace_only_source_value_returns_no_candidates():
    assert search_concept("   ", "SNOMED") == []
