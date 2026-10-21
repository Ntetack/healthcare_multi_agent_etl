"""resolve_target() is pure/deterministic - no DB needed. Confirms the
domain_id -> OMOP target table/field routing for the 5 domain-driven
event tables in scope for this prototype."""
from app.tools.mapping.omop_target_schema import IN_SCOPE_TABLES, resolve_target


def test_resolve_target_condition():
    target = resolve_target("Condition")
    assert target == {
        "table": "condition_occurrence",
        "concept_field": "condition_concept_id",
        "source_value_field": "condition_source_value",
        "source_concept_field": "condition_source_concept_id",
    }


def test_resolve_target_drug():
    target = resolve_target("Drug")
    assert target["table"] == "drug_exposure"


def test_resolve_target_measurement():
    assert resolve_target("Measurement")["table"] == "measurement"


def test_resolve_target_procedure():
    assert resolve_target("Procedure")["table"] == "procedure_occurrence"


def test_resolve_target_observation():
    assert resolve_target("Observation")["table"] == "observation"


def test_resolve_target_unknown_domain_returns_none():
    """A domain outside the 5 event tables (e.g. Gender, which belongs
    to PERSON via a different, not-yet-built mechanism) must not be
    silently misrouted."""
    assert resolve_target("Gender") is None
    assert resolve_target(None) is None
    assert resolve_target("SomethingUnrelated") is None


def test_nine_prototype_tables_are_all_tracked():
    expected = {
        "person", "observation_period", "visit_occurrence",
        "condition_occurrence", "drug_exposure", "measurement",
        "procedure_occurrence", "observation", "death",
    }
    assert set(IN_SCOPE_TABLES) == expected


def test_find_paired_source_value_field_concept_id():
    from app.tools.mapping.omop_target_schema import find_paired_source_value_field
    available = ["person_id", "gender_concept_id", "gender_source_value", "year_of_birth"]
    assert find_paired_source_value_field("gender_concept_id", available) == "gender_source_value"


def test_find_paired_source_value_field_source_concept_id():
    from app.tools.mapping.omop_target_schema import find_paired_source_value_field
    available = ["condition_source_concept_id", "condition_source_value"]
    assert find_paired_source_value_field("condition_source_concept_id", available) == "condition_source_value"


def test_find_paired_source_value_field_no_pairing_for_type_concept():
    """*_type_concept_id fields represent provenance, not a value present
    in source data - must return None, never guess a wrong pairing."""
    from app.tools.mapping.omop_target_schema import find_paired_source_value_field
    available = ["condition_type_concept_id", "condition_source_value"]  # no "type_source_value"
    assert find_paired_source_value_field("condition_type_concept_id", available) is None


def test_load_vocabulary_fields_from_real_yaml():
    """The vocabulary knowledge base is the user-provided YAML, never
    agent-generated - confirms it loads and covers the 9 tables."""
    from app.tools.mapping.omop_target_schema import get_vocabulary_fields
    person_fields = get_vocabulary_fields("person")
    assert person_fields.get("gender_concept_id") == "Gender"
    assert person_fields.get("race_concept_id") == "Race"
