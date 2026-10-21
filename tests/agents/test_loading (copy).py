"""LoadingAgent tests - LLM (join key resolution) and DB writes
(load_to_omop) are mocked, so these run without a real database. Proves
the core scenario discussed: PERSON resolved first, then a table whose
fields live on a DIFFERENT source table gets correctly joined via an
LLM-proposed key, and person_id is correctly threaded through."""
import json
from unittest.mock import MagicMock

import pandas as pd
import pytest

from app.agents.loading import LoadingAgent


@pytest.fixture
def captured_loads(monkeypatch):
    captured = {}
    monkeypatch.setattr("app.agents.loading.reset_temp_for_new_run", lambda: None)
    monkeypatch.setattr("app.agents.loading.verify_load", lambda table, n: True)

    def fake_load(table, df):
        captured[table] = df
        return len(df)

    monkeypatch.setattr("app.agents.loading.load_to_omop", fake_load)
    return captured


def test_person_resolved_first_and_visit_joined_via_llm(captured_loads):
    """The exact scenario discussed: visit_start_date lives on
    'encounters', person_source_value lives on 'patients' - the LLM is
    asked once for the join key (encounters.PATIENT <-> patients.Id),
    and person_id is correctly assigned and threaded through."""
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({
        "key_a": "PATIENT", "key_b": "Id", "confidence": 0.95, "reason": "patient identifier",
    }))

    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({
                "Id": ["p1", "p2"],
                "__omop_person__person_source_value": ["p1", "p2"],
            }),
            "encounters": pd.DataFrame({
                "PATIENT": ["p1", "p2", "p1"],
                "__omop_visit_occurrence__visit_start_date": ["2024-01-15", "2024-02-01", "2024-03-10"],
                "__omop_visit_occurrence__visit_concept_id": [9202, 9202, 9202],
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id"},
                {"target_table": "visit_occurrence", "target_field": "visit_start_date",
                 "source_table": "encounters", "source_field": "__omop_visit_occurrence__visit_start_date"},
                {"target_table": "visit_occurrence", "target_field": "visit_concept_id",
                 "source_table": "encounters", "source_field": "__omop_visit_occurrence__visit_concept_id"},
            ],
            "per_table": {},
        },
    }

    result = agent.run(state)

    assert result.status.value == "SUCCESS"
    # PERSON: 2 distinct patients, sequential ids assigned.
    assert len(captured_loads["person"]) == 2
    assert set(captured_loads["person"]["person_id"]) == {1, 2}
    # VISIT_OCCURRENCE: 3 rows, correctly joined to the right person_id.
    visits = captured_loads["visit_occurrence"]
    assert len(visits) == 3
    p1_id = captured_loads["person"].loc[captured_loads["person"]["person_source_value"] == "p1", "person_id"].iloc[0]
    assert set(visits.loc[visits["visit_start_date"].isin(["2024-01-15", "2024-03-10"]), "person_id"]) == {p1_id}
    # The join key is found deterministically (100% real overlap) -
    # the LLM is never even consulted for a case this unambiguous.
    assert agent.llm.invoke.call_count == 0


def test_domain_driven_rows_grouped_by_per_row_target_table(captured_loads):
    """A single source table (conditions) with values resolving to
    DIFFERENT target tables (condition_occurrence vs observation) must
    be split correctly using the per-row _target_table column."""
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({"key_a": None, "key_b": None}))

    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({"Id": ["p1"]}),
            "conditions": pd.DataFrame({
                "PATIENT": ["p1", "p1"],
                "CODE": ["44054006", "162864005"],
                "CODE_concept_id": [201826, 4238598],
                "CODE_target_table": ["condition_occurrence", "observation"],
                "__omop_condition_occurrence__condition_start_date": [
                    pd.Timestamp("2020-01-01").date(), pd.Timestamp("2020-01-01").date()
                ],
                "__omop_observation__observation_date": [
                    pd.Timestamp("2020-01-01").date(), pd.Timestamp("2020-01-01").date()
                ],
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id"},
                {"target_table": "condition_occurrence", "target_field": "condition_start_date",
                 "source_table": "conditions", "source_field": "START", "data_type": "date"},
                {"target_table": "observation", "target_field": "observation_date",
                 "source_table": "conditions", "source_field": "START", "data_type": "date"},
            ],
            "per_table": {
                "conditions": {"semantic_mapping": [
                    {"field": "conditions.CODE", "target_concept_field": "condition_concept_id",
                     "target_source_value_field": "condition_source_value"},
                ]},
            },
        },
    }

    result = agent.run(state)

    assert result.status.value == "SUCCESS"
    assert len(captured_loads["condition_occurrence"]) == 1
    assert len(captured_loads["observation"]) == 1
    assert captured_loads["condition_occurrence"]["condition_concept_id"].iloc[0] == 201826


def test_observation_period_computed_from_visit_occurrence_dates(captured_loads):
    """The current behavior: observation_period_start_date/end_date are
    derived from visit_occurrence's own dates (one period per visit, or
    per group of overlapping/adjacent visits) - following the OMOP
    convention that a real gap between admissions must produce SEPARATE
    periods, never a single span across every clinical event a person
    ever had (which would falsely imply continuous observation through
    any gap)."""
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({
        "key_a": "PATIENT", "key_b": "Id", "confidence": 0.9, "reason": "patient id",
    }))
    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({"Id": ["p1"], "__omop_person__person_source_value": ["p1"]}),
            "encounters": pd.DataFrame({
                "PATIENT": ["p1"],
                "__omop_visit_occurrence__visit_start_date": [pd.Timestamp("2020-01-01").date()],
                "__omop_visit_occurrence__visit_end_date": [pd.Timestamp("2020-01-05").date()],
                "__omop_visit_occurrence__visit_concept_id": [9201],
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id"},
                {"target_table": "visit_occurrence", "target_field": "visit_start_date",
                 "source_table": "encounters", "source_field": "__omop_visit_occurrence__visit_start_date"},
                {"target_table": "visit_occurrence", "target_field": "visit_end_date",
                 "source_table": "encounters", "source_field": "__omop_visit_occurrence__visit_end_date"},
                {"target_table": "visit_occurrence", "target_field": "visit_concept_id",
                 "source_table": "encounters", "source_field": "__omop_visit_occurrence__visit_concept_id"},
            ],
            "per_table": {},
        },
    }
    agent.run(state)

    op = captured_loads["observation_period"]
    assert len(op) == 1
    assert op["observation_period_start_date"].iloc[0] == pd.Timestamp("2020-01-01").date()
    assert op["observation_period_end_date"].iloc[0] == pd.Timestamp("2020-01-05").date()
    assert op["person_id"].iloc[0] == 1


def test_observation_period_splits_on_a_real_gap_between_visits(captured_loads):
    """The exact scenario that motivated this design: a patient with two
    admissions separated by a real gap (no information about them in
    between) must get TWO separate, non-overlapping observation
    periods - never one merged span that would falsely imply continuous
    observation through the gap (OMOP's own documented convention)."""
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({
        "key_a": "PATIENT", "key_b": "Id", "confidence": 0.9, "reason": "patient id",
    }))
    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({"Id": ["p1"], "__omop_person__person_source_value": ["p1"]}),
            "encounters": pd.DataFrame({
                "PATIENT": ["p1", "p1"],
                "__omop_visit_occurrence__visit_start_date": [
                    pd.Timestamp("2020-01-01").date(), pd.Timestamp("2025-06-01").date()
                ],
                "__omop_visit_occurrence__visit_end_date": [
                    pd.Timestamp("2020-01-05").date(), pd.Timestamp("2025-06-08").date()
                ],
                "__omop_visit_occurrence__visit_concept_id": [9201, 9201],
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id"},
                {"target_table": "visit_occurrence", "target_field": "visit_start_date",
                 "source_table": "encounters", "source_field": "__omop_visit_occurrence__visit_start_date"},
                {"target_table": "visit_occurrence", "target_field": "visit_end_date",
                 "source_table": "encounters", "source_field": "__omop_visit_occurrence__visit_end_date"},
                {"target_table": "visit_occurrence", "target_field": "visit_concept_id",
                 "source_table": "encounters", "source_field": "__omop_visit_occurrence__visit_concept_id"},
            ],
            "per_table": {},
        },
    }
    agent.run(state)

    op = captured_loads["observation_period"].sort_values("observation_period_start_date")
    assert len(op) == 2, "A real multi-year gap must produce two separate periods, not one merged span"
    assert op["observation_period_end_date"].iloc[0] == pd.Timestamp("2020-01-05").date()
    assert op["observation_period_start_date"].iloc[1] == pd.Timestamp("2025-06-01").date()


def test_missing_person_source_value_fails_cleanly(captured_loads):
    agent = LoadingAgent(llm=MagicMock())
    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {},
        "mapping_output": {"structural_target_mappings": [], "per_table": {}},
    }
    result = agent.run(state)
    assert result.status.value == "FAIL"


def test_year_of_birth_derived_from_birth_datetime(captured_loads):
    """OMOP requires year_of_birth NOT NULL, but a source like Synthea
    only provides a full birth_datetime - it must be derived
    deterministically, not left NULL."""
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({"key_a": None, "key_b": None}))

    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({
                "Id": ["p1"],
                "__omop_person__person_source_value": ["p1"],
                "__omop_person__birth_datetime": [pd.Timestamp("1994-09-27")],
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id"},
                {"target_table": "person", "target_field": "birth_datetime",
                 "source_table": "patients", "source_field": "Id"},
            ],
            "per_table": {},
        },
    }
    agent.run(state)
    person = captured_loads["person"]
    assert person["year_of_birth"].iloc[0] == 1994
    assert person["month_of_birth"].iloc[0] == 9
    assert person["day_of_birth"].iloc[0] == 27


def test_unmapped_concept_id_defaults_to_zero_not_null(captured_loads):
    """OMOP convention: an unmapped concept field must be 0 ('No
    matching concept'), never NULL - this is what prevents NOT NULL
    constraint violations for values that genuinely have no vocabulary
    match (e.g. after all matching tiers were exhausted)."""
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({"key_a": None, "key_b": None}))

    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({
                "Id": ["p1"],
                "__omop_person__person_source_value": ["p1"],
                "__omop_person__ethnicity_concept_id": [None],  # genuinely unmapped
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id"},
                {"target_table": "person", "target_field": "ethnicity_concept_id",
                 "source_table": "patients", "source_field": "Id"},
            ],
            "per_table": {},
        },
    }
    agent.run(state)
    person = captured_loads["person"]
    assert person["ethnicity_concept_id"].iloc[0] == 0
    assert person["ethnicity_concept_id"].dtype.kind == "i"  # real integer, not float/NaN


def test_failure_placeholder_records_are_ignored_not_crashed_on(captured_loads):
    """structural_target_mappings can contain explicit failure
    placeholders (source_table=None, e.g. 'no paired field found') mixed
    in with valid resolutions - these must be filtered out, not treated
    as a source table to join against."""
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({"key_a": None, "key_b": None}))

    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({
                "Id": ["p1"],
                "__omop_person__person_source_value": ["p1"],
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id"},
                # Explicit failure placeholder - must not crash assembly.
                {"target_table": "person", "target_field": "condition_type_concept_id",
                 "source_table": None, "source_field": None,
                 "reason": "No paired source_value field for this table"},
            ],
            "per_table": {},
        },
    }
    result = agent.run(state)
    assert result.status.value == "SUCCESS"
    assert len(captured_loads["person"]) == 1


def test_source_concept_id_reaches_the_final_table_alongside_standard_concept_id(captured_loads):
    """End-to-end proof that Mapping's two-step resolution (see
    resolve_concept_pair) actually survives all the way to the final
    loaded table: condition_source_concept_id (the ICD9CM code's own
    concept) and condition_concept_id (the mapped SNOMED standard
    concept) must BOTH be present and distinct."""
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({"key_a": None, "key_b": None}))

    state = {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({"Id": ["p1"], "__omop_person__person_source_value": ["p1"]}),
            "diagnoses_icd": pd.DataFrame({
                "PATIENT": ["p1"], "ICD9_CODE": ["307.50"],
                # As Mapping's mechanism 1 now actually produces:
                "ICD9_CODE_concept_id": [4263084],           # STANDARD (SNOMED)
                "ICD9_CODE_source_concept_id": [44821974],   # SOURCE (ICD9CM)
                "ICD9_CODE_target_table": ["condition_occurrence"],
                "__omop_condition_occurrence__condition_start_date": [pd.Timestamp("2020-01-01").date()],
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "Id"},
                {"target_table": "condition_occurrence", "target_field": "condition_start_date",
                 "source_table": "diagnoses_icd", "source_field": "CHARTDATE", "data_type": "date"},
            ],
            "per_table": {},
        },
    }
    agent.run(state)

    conditions = captured_loads["condition_occurrence"]
    assert conditions["condition_concept_id"].iloc[0] == 4263084
    assert conditions["condition_source_concept_id"].iloc[0] == 44821974
    # The two must be genuinely distinct columns, not the same value
    # duplicated - this is exactly the bug being fixed.
    assert conditions["condition_concept_id"].iloc[0] != conditions["condition_source_concept_id"].iloc[0]

# ---------------------------------------------------------------------------
# Date fallback to the visit start, applied per row (not only per column)
# ---------------------------------------------------------------------------

def _mimic_like_state(cpt_dates):
    """patients + admissions (visit_start_date) + a CPTEVENTS-like source whose
    date column EXISTS but is empty for some rows (ICU cost-center rows)."""
    return {
        "execution_id": "RUN-1",
        "loading_mode": "load_temp",
        "_transformed_tables": {
            "patients": pd.DataFrame({
                "SUBJECT_ID": ["1", "2"],
                "__omop_person__person_source_value": ["1", "2"],
            }),
            "admissions": pd.DataFrame({
                "SUBJECT_ID": ["1", "2"],
                "HADM_ID": ["100", "200"],
                "__omop_visit_occurrence__visit_start_date": [
                    pd.Timestamp("2101-01-10").date(), pd.Timestamp("2102-03-05").date(),
                ],
                "__omop_visit_occurrence__visit_concept_id": [9201, 9201],
            }),
            "cptevents": pd.DataFrame({
                "SUBJECT_ID": ["1", "1", "2"],
                "HADM_ID": ["100", "100", "200"],
                "CPT_CD": ["99232", "94002", "99291"],
                "CPT_CD_concept_id": [2514408, 2314001, 2514441],
                "CPT_CD_target_table": ["procedure_occurrence"] * 3,
                "__omop_procedure_occurrence__procedure_date": cpt_dates,
            }),
        },
        "mapping_output": {
            "structural_target_mappings": [
                {"target_table": "person", "target_field": "person_source_value",
                 "source_table": "patients", "source_field": "SUBJECT_ID"},
                {"target_table": "visit_occurrence", "target_field": "visit_start_date",
                 "source_table": "admissions", "source_field": "__omop_visit_occurrence__visit_start_date"},
                {"target_table": "visit_occurrence", "target_field": "visit_concept_id",
                 "source_table": "admissions", "source_field": "__omop_visit_occurrence__visit_concept_id"},
                {"target_table": "procedure_occurrence", "target_field": "procedure_date",
                 "source_table": "cptevents", "source_field": "CHARTDATE", "data_type": "date"},
            ],
            "per_table": {
                "cptevents": {"semantic_mapping": [
                    {"field": "cptevents.CPT_CD", "target_concept_field": "procedure_concept_id",
                     "target_source_value_field": "procedure_source_value"},
                ]},
            },
        },
    }


def _run(state):
    agent = LoadingAgent(llm=MagicMock())
    agent.llm.invoke.return_value = MagicMock(content=json.dumps({"key_a": None, "key_b": None}))
    return agent, agent.run(state)


def test_empty_dates_are_filled_from_the_visit_start_and_counted(captured_loads):
    """CHARTDATE exists but is NULL for two of three rows: those rows are
    kept, dated with their admission's start, and the imputation is counted."""
    real = pd.Timestamp("2101-01-12").date()
    state = _mimic_like_state([real, pd.NaT, pd.NaT])

    agent, result = _run(state)

    assert result.status.value == "SUCCESS"
    procs = captured_loads["procedure_occurrence"].sort_values("procedure_source_value").reset_index(drop=True)
    assert len(procs) == 3
    by_code = dict(zip(procs["procedure_source_value"], pd.to_datetime(procs["procedure_date"]).dt.date))
    assert by_code["99232"] == real                              # real date never overwritten
    assert by_code["94002"] == pd.Timestamp("2101-01-10").date()  # filled from admission 100
    assert by_code["99291"] == pd.Timestamp("2102-03-05").date()  # filled from admission 200

    log = result.output["dates_imputed_from_visit"]
    assert log["procedure_occurrence<-cptevents"]["rows_imputed"] == 2
    assert result.output["per_table"]["procedure_occurrence"]["dates_imputed_from_visit"][
        "cptevents"]["rows_imputed"] == 2
    assert "dropped_missing_date" not in result.output["per_table"]["procedure_occurrence"]


def test_no_date_is_imputed_when_the_source_provides_every_date(captured_loads):
    dates = [pd.Timestamp("2101-01-12").date(), pd.Timestamp("2101-01-13").date(), pd.Timestamp("2102-04-01").date()]
    agent, result = _run(_mimic_like_state(dates))

    assert result.output["dates_imputed_from_visit"] == {}
    procs = captured_loads["procedure_occurrence"]
    assert sorted(pd.to_datetime(procs["procedure_date"]).dt.date) == sorted(dates)


def test_fill_helper_only_touches_missing_values():
    frame = pd.DataFrame({"d": [pd.Timestamp("2100-01-01").date(), pd.NaT, pd.NaT]})
    visit = [pd.Timestamp("2100-06-01").date(), pd.Timestamp("2100-06-02").date(), pd.NaT]

    n = LoadingAgent._fill_missing_dates_from_visit(frame, "d", visit)

    assert n == 1                                              # third row has no visit date either
    assert frame["d"].iloc[0] == pd.Timestamp("2100-01-01").date()
    assert frame["d"].iloc[1] == pd.Timestamp("2100-06-02").date()
    assert pd.isna(frame["d"].iloc[2])                         # stays missing -> dropped later, with its diagnostic


def test_fill_helper_creates_the_column_when_absent():
    frame = pd.DataFrame({"x": [1, 2]})
    n = LoadingAgent._fill_missing_dates_from_visit(frame, "d", [pd.Timestamp("2100-06-01").date(), pd.NaT])
    assert n == 1
    assert list(frame.columns) == ["x", "d"]
