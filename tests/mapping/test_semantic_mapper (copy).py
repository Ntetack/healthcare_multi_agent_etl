"""Placeholder: requires a live cdm_vocab.concept table (OMOP vocab
loaded). Marked for integration-level execution once the DB is up."""
import pytest


@pytest.mark.integration
def test_search_concept_icd10():
    pytest.skip("requires a running PostgreSQL with cdm_vocab.concept loaded")
