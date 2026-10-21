"""End-to-end smoke test, requires PostgreSQL + R/DQD configured.
Not run by default in CI without those services."""
import pytest


@pytest.mark.integration
def test_full_pipeline_smoke():
    pytest.skip("requires PostgreSQL, OMOP vocab, and R/DataQualityDashboard")
