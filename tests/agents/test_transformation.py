"""TransformationAgent must cast ONLY fields identified by Mapping's
structural_target_mappings, using the REAL introspected data_type to
choose the cast - not a hand-picked field-name list, and not blind
pattern-matching on columns that merely look date-adjacent."""
import datetime as dt

import pandas as pd

from app.agents.transformation import TransformationAgent


def test_date_type_cast_applied_based_on_real_data_type():
    """The bug being fixed: without a real data_type-driven cast, a date
    string was just copied as text rather than becoming an actual date
    object - this test asserts a real `date` instance, not a
    string-equality check that would pass either way."""
    agent = TransformationAgent(llm=None)
    state = {
        "execution_id": "RUN-1",
        "_enriched_tables": {
            "patients": pd.DataFrame({
                "Id": ["p1", "p2"],
                "BIRTHDATE": ["1975-03-21", "1988-11-02"],
                "DESCRIPTION": ["not a date field", "also not a date"],
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "birth_datetime",
                 "source_table": "patients", "source_field": "BIRTHDATE",
                 "data_type": "timestamp without time zone"},
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id",
                 "data_type": "character varying"},
            ]
        },
    }

    result = agent.run(state)
    transformed = state["_transformed_tables"]["patients"]

    assert isinstance(transformed["__omop_person__birth_datetime"].iloc[0], dt.date)
    assert transformed["__omop_person__birth_datetime"].iloc[0] == dt.date(1975, 3, 21)
    # varchar field -> copied as-is (string), not touched by any cast.
    assert transformed["__omop_person__person_source_value"].tolist() == ["p1", "p2"]
    # A column that merely *looks* date-adjacent but wasn't targeted must
    # be left completely untouched.
    assert "__omop_person__DESCRIPTION" not in transformed.columns
    assert result.status.value == "SUCCESS"


def test_vocabulary_field_grouped_and_applied_across_all_rows():
    """Vocabulary-field records (source_value set) must be grouped into
    one value->concept_id mapping and applied to the WHOLE column, not
    just the row that happened to produce each record."""
    agent = TransformationAgent(llm=None)
    state = {
        "execution_id": "RUN-1",
        "_enriched_tables": {
            "patients": pd.DataFrame({"gender": ["F", "M", "F"]}),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "gender_concept_id",
                 "source_table": "patients", "source_field": "gender",
                 "source_value": "F", "target_concept_id": 8532, "data_type": "integer"},
                {"target_table": "person", "target_field": "gender_concept_id",
                 "source_table": "patients", "source_field": "gender",
                 "source_value": "M", "target_concept_id": 8507, "data_type": "integer"},
            ]
        },
    }

    agent.run(state)
    transformed = state["_transformed_tables"]["patients"]

    assert transformed["__omop_person__gender_concept_id"].tolist() == [8532, 8507, 8532]


def test_skips_target_when_source_table_absent_this_batch():
    agent = TransformationAgent(llm=None)
    state = {
        "execution_id": "RUN-1",
        "_enriched_tables": {"patients": pd.DataFrame({"Id": ["p1"]})},
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "death", "target_field": "death_date",
                 "source_table": "deaths", "source_field": "DATE", "data_type": "date"},
            ]
        },
    }
    result = agent.run(state)
    assert len(result.output["skipped"]) == 1
    assert "__omop_death__death_date" not in state["_transformed_tables"]["patients"].columns


def test_falls_back_to_raw_tables_when_mapping_hasnt_run():
    """Standalone testing (before Mapping) shouldn't crash."""
    agent = TransformationAgent(llm=None)
    state = {
        "execution_id": "RUN-1",
        "_raw_tables": {"patients": pd.DataFrame({"Id": ["p1"]})},
    }
    result = agent.run(state)
    assert result.status.value == "SUCCESS"
    assert result.output["applied"] == []


def test_date_type_truncates_datetime_when_source_has_time_component():
    """If the OMOP target column is DATE (not TIMESTAMP) but the source
    value carries a time (e.g. "2024-01-15 14:30:00"), the result must
    be truncated to a plain date, not left as a datetime."""
    import datetime as dt
    agent = TransformationAgent(llm=None)
    state = {
        "execution_id": "RUN-1",
        "_enriched_tables": {
            "encounters": pd.DataFrame({"START": ["2024-01-15 14:30:00"]}),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "visit_occurrence", "target_field": "visit_start_date",
                 "source_table": "encounters", "source_field": "START", "data_type": "date"},
            ]
        },
    }
    agent.run(state)
    result = state["_transformed_tables"]["encounters"]["__omop_visit_occurrence__visit_start_date"].iloc[0]
    assert result == dt.date(2024, 1, 15)
    assert not isinstance(result, dt.datetime)
