import pandas as pd

from app.tools.data.schema_inspector import detect_possible_codings, profile_dataset


def test_profile_dataset_counts_missing():
    df = pd.DataFrame({"a": ["1", "", "3"]})
    profile = profile_dataset(df)
    assert profile["a"]["missing_count"] == 1


def test_detect_possible_codings_loinc():
    df = pd.DataFrame({"lab_code": ["1234-5", "5678-9", "1111-1"]})
    hits = detect_possible_codings(df)
    assert "LOINC" in hits.get("lab_code", [])
