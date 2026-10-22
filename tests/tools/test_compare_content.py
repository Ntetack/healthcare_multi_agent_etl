"""Tests for the row-level comparison between two OMOP systems.

The comparison reads two databases, but everything that decides a score is a
pure function of two frames: these tests run on in-memory tables that reproduce,
one by one, the situations met in the first FHIR versus CSV report.
"""
from __future__ import annotations

import contextlib
import importlib.util
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _load_script(name: str):
    path = Path(__file__).resolve().parents[2] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cc = _load_script("compare_content")
runner = _load_script("run_full_comparison")

CROSSWALK = pd.DataFrame({"b1_person_id": [1, 2, 3], "b0_person_id": [10, 20, 30]})


def _frames(b1: dict, b0: dict):
    """Two frames whose person ids follow the crosswalk (1->10, 2->20, 3->30)."""
    n = len(next(iter(b1.values())))
    return (pd.DataFrame({"person_id": [1, 2, 3][:n], **b1}),
            pd.DataFrame({"person_id": [10, 20, 30][:n], **b0}))


# ---------------------------------------------------------------- the rules

@pytest.mark.parametrize("kind, value, expected", [
    ("concept", None, True), ("concept", float("nan"), True), ("concept", 0, True), ("concept", "0", True),
    ("concept", 8527, False), ("exact", 0, False), ("exact", "", True), ("exact", "  ", True),
    ("text", "x", False), ("date", pd.NaT, True),
])
def test_what_counts_as_missing(kind, value, expected):
    assert cc.is_missing(value, kind) is expected


@pytest.mark.parametrize("b1, b0, expected", [
    (19.38, 19.4, True), (58.563, 58.6, True), (1.1441, 1.1, True),       # rounding by the less precise side
    (19.35, 19.3, True), (1.0, 3.0, False), (19.38, 19.5, False), (7, 7.0, True), ("5.00", 5, True),
])
def test_a_number_agrees_within_the_rounding_of_the_less_precise_side(b1, b0, expected):
    assert cc.values_agree("number", b1, b0) is expected


@pytest.mark.parametrize("b1, b0, expected", [
    (date(2021, 4, 7), pd.Timestamp("2021-04-07"), True),
    ("2021-04-07", date(2021, 4, 7), True),
    (date(2021, 7, 4), date(2021, 4, 7), False),                          # day and month swapped
])
def test_a_date_is_compared_by_its_day(b1, b0, expected):
    assert cc.values_agree("date", b1, b0) is expected


@pytest.mark.parametrize("b1, b0, expected", [
    (pd.Timestamp("1993-12-28 00:10:35"), pd.Timestamp("1993-12-28 00:00:00"), True),   # a date stored as midnight
    (pd.Timestamp("1993-12-28 00:10:35"), pd.Timestamp("1993-12-28 00:10:35"), True),
    (pd.Timestamp("1993-12-28 00:10:35"), pd.Timestamp("1993-12-28 00:10:36"), False),
    (pd.Timestamp("1993-12-28 08:00:00"), pd.Timestamp("1993-12-29 00:00:00"), False),
])
def test_a_datetime_is_compared_to_the_day_when_one_side_has_no_time(b1, b0, expected):
    assert cc.values_agree("datetime", b1, b0) is expected


@pytest.mark.parametrize("kind, b1, b0, expected", [
    ("text", "White", "white", True), ("text", "  Not   Hispanic ", "not hispanic", True),
    ("text", "female", "F", False),                                       # a real difference of representation
    ("concept", 8527, "8527", True), ("concept", 8527, 8516, False),
    ("exact", 1976, 1976.0, True), ("exact", "1976", 1976, True), ("exact", 1976, 1977, False),
])
def test_text_concept_and_exact_rules(kind, b1, b0, expected):
    assert cc.values_agree(kind, b1, b0) is expected


@pytest.mark.parametrize("field, kind", [
    ("gender_concept_id", "concept"), ("condition_start_date", "date"), ("death_datetime", "datetime"),
    ("value_as_number", "number"), ("quantity", "number"), ("race_source_value", "text"),
    ("value_as_string", "text"), ("year_of_birth", "exact"),
])
def test_the_kind_of_a_field_is_inferred_from_its_name(field, kind):
    assert cc.infer_kind(field) == kind


def test_a_table_described_by_plain_lists_gets_roles_and_kinds():
    spec = cc.spec_from_lists(
        "person", ["person_source_value"],
        ["gender_concept_id", "gender_source_value", "person_source_value", "year_of_birth", "x_type_concept_id"],
        ["x_type_concept_id"],
    )
    assert spec["content"] == {"gender_concept_id": "concept", "year_of_birth": "exact"}
    assert spec["provenance"] == {"gender_source_value": "text"}
    assert spec["key"] == ["person_source_value"]


# ------------------------------------------------------ the first report's person table

PERSON_SPEC = {
    "table": "person", "key": ["person_source_value"],
    "content": {"gender_concept_id": "concept", "year_of_birth": "exact", "race_concept_id": "concept",
                 "ethnicity_concept_id": "concept"},
    "provenance": {"gender_source_value": "text", "race_source_value": "text"},
}


def _person_frames():
    return _frames(
        {"person_source_value": ["a", "b", "c"], "gender_concept_id": [8532, 8507, 8532],
         "year_of_birth": [1990, 1980, 1975], "race_concept_id": [8527, 8516, 8527],
         "ethnicity_concept_id": [38003564, 38003563, 38003564],
         "gender_source_value": ["female", "male", "female"], "race_source_value": ["White", "Black or African American", "White"]},
        {"person_source_value": ["a", "b", "c"], "gender_concept_id": [8532, 8507, 8532],
         "year_of_birth": [1990, 1980, 1975], "race_concept_id": [8527, 8516, 8527],
         "ethnicity_concept_id": [38003564, 38003563, 38003564],
         "gender_source_value": ["F", "M", "F"], "race_source_value": ["white", "black", "white"]},
    )


def test_a_row_with_the_right_meaning_agrees_even_if_the_source_wrote_it_differently():
    """The case of the report: every concept of the person agreed, only the
    source values differed, and the old score said 0 identical rows out of 114."""
    _, summary = cc.compare_frames(PERSON_SPEC, *_person_frames(), CROSSWALK)
    assert summary["content_agree_rows"] == 3 and summary["content_agree_pct"] == 100.0


def test_the_provenance_fields_enter_the_mean_like_any_other_field():
    lines, summary = cc.compare_frames(PERSON_SPEC, *_person_frames(), CROSSWALK)
    per_field = summary["per_field"]
    assert per_field["gender_source_value"]["pct"] == 0.0
    assert per_field["gender_source_value"]["role"] == "provenance"
    pcts = [v["pct"] for v in per_field.values() if v["pct"] is not None]
    assert summary["field_mean_pct"] == round(sum(pcts) / len(pcts), 1)
    content_only = [v["pct"] for v in per_field.values() if v["role"] == "content" and v["pct"] is not None]
    assert summary["field_mean_pct"] < round(sum(content_only) / len(content_only), 1)
    assert "compared fields" in "\n".join(lines)


def test_person_is_compared_without_the_patient_identifier_the_two_systems_may_keep_differently():
    """MIMIC case: B1 wrote ROW_ID in person_source_value, B0 wrote SUBJECT_ID. The patient bridge
    already pairs the persons, so the identifier is neither a key nor a compared field."""
    spec = next(c for c in runner.TABLE_CONFIGS if c["table"] == "person")
    assert spec["key"] == [] and "person_source_value" in spec["ignored"]
    b1, b0 = _frames(
        {"person_source_value": ["9557", "9550", "9527"], "gender_concept_id": [8532, 8507, 8532],
         "year_of_birth": [1990, 1980, 1975]},
        {"person_source_value": ["10098", "10035", "10093"], "gender_concept_id": [8532, 8507, 8532],
         "year_of_birth": [1990, 1980, 1975]},
    )
    _, summary = cc.compare_frames(spec, b1, b0, CROSSWALK)
    assert summary["matched_rows"] == 3 and summary["coverage_pct"] == 100.0
    assert summary["per_field"]["gender_concept_id"]["pct"] == 100.0
    assert "person_source_value" not in summary["per_field"]


def test_a_real_content_difference_lowers_the_score():
    b1, b0 = _person_frames()
    b1.loc[1, "race_concept_id"] = 8527                                     # wrong race for the second person
    _, summary = cc.compare_frames(PERSON_SPEC, b1, b0, CROSSWALK)
    assert summary["content_agree_rows"] == 2
    assert summary["per_field"]["race_concept_id"]["agree"] == 2


# ------------------------------------------------------------- missing values

MEASUREMENT_SPEC = {
    "table": "measurement", "key": ["measurement_concept_id"],
    "content": {"value_as_number": "number", "unit_concept_id": "concept"}, "provenance": {},
}


def _measurements(b1_unit, b0_unit):
    return _frames(
        {"measurement_concept_id": [1, 1, 1], "value_as_number": [19.38, 5.0, 7.0], "unit_concept_id": b1_unit},
        {"measurement_concept_id": [1, 1, 1], "value_as_number": [19.4, 5.0, 7.0], "unit_concept_id": b0_unit},
    )


def test_a_value_missing_on_one_side_only_is_a_disagreement():
    """The old comparison ignored a field our side left empty, which hid the gap."""
    _, summary = cc.compare_frames(MEASUREMENT_SPEC, *_measurements([8582, 8582, None], [8582, 8582, 9529]), CROSSWALK)
    assert summary["per_field"]["unit_concept_id"]["agree"] == 2
    assert summary["per_field"]["unit_concept_id"]["total"] == 3
    assert summary["content_agree_rows"] == 2


def test_a_value_missing_on_both_sides_is_not_counted_at_all():
    _, summary = cc.compare_frames(MEASUREMENT_SPEC, *_measurements([8582, 8582, None], [8582, 8582, None]), CROSSWALK)
    assert summary["per_field"]["unit_concept_id"]["total"] == 2
    assert summary["content_agree_pct"] == 100.0


def test_a_concept_of_zero_is_treated_as_missing_but_not_as_equal_to_a_real_concept():
    _, summary = cc.compare_frames(MEASUREMENT_SPEC, *_measurements([0, 8582, 0], [8582, 8582, 0]), CROSSWALK)
    assert summary["per_field"]["unit_concept_id"]["total"] == 2          # the pair of zeros is left out
    assert summary["per_field"]["unit_concept_id"]["agree"] == 1          # 0 against 8582 disagrees


def test_a_rounded_value_agrees_with_its_precise_counterpart():
    _, summary = cc.compare_frames(MEASUREMENT_SPEC, *_measurements([1, 1, 1], [1, 1, 1]), CROSSWALK)
    assert summary["per_field"]["value_as_number"]["pct"] == 100.0       # 19.38 against 19.4


def test_a_field_the_baseline_fills_and_we_never_do_is_scored_at_zero():
    lines, summary = cc.compare_frames(MEASUREMENT_SPEC, *_measurements([None] * 3, [8582, 8582, 9529]), CROSSWALK)
    assert summary["gaps"] == {}
    assert summary["per_field"]["unit_concept_id"]["pct"] == 0.0 and summary["per_field"]["unit_concept_id"]["total"] == 3
    assert _detail(summary, "unit_concept_id")["status"] == "never_b1" and _detail(summary, "unit_concept_id")["agree_pct"] == 0.0
    assert summary["content_agree_pct"] == 0.0


def test_a_field_only_we_fill_is_outside_the_baseline_scope_and_does_not_count_against_us():
    _, summary = cc.compare_frames(MEASUREMENT_SPEC, *_measurements([8582, 8582, 9529], [None] * 3), CROSSWALK)
    assert summary["gaps"] == {"unit_concept_id": "populated only in B1, outside the baseline scope (not populated)"}
    assert summary["content_agree_pct"] == 100.0


def test_a_field_empty_on_both_sides_is_listed_not_scored():
    _, summary = cc.compare_frames(MEASUREMENT_SPEC, *_measurements([None] * 3, [None] * 3), CROSSWALK)
    assert summary["gaps"] == {"unit_concept_id": "empty on both sides"}


# --------------------------------------------------------- existence and coverage

EVENT_SPEC = {
    "table": "condition_occurrence", "key": ["condition_concept_id", "condition_start_date"],
    "content": {"condition_end_date": "date"}, "provenance": {},
}


def _events(b1_rows, b0_rows):
    cols = ["person_id", "condition_concept_id", "condition_start_date", "condition_end_date"]
    return pd.DataFrame(b1_rows, columns=cols), pd.DataFrame(b0_rows, columns=cols)


def test_coverage_and_precision_count_rows_not_values():
    b1, b0 = _events(
        [(1, 7, date(2020, 1, 1), None), (1, 7, date(2020, 2, 2), None), (2, 7, date(2020, 3, 3), None)],
        [(10, 7, date(2020, 1, 1), None), (10, 7, date(2020, 2, 2), None), (20, 7, date(2021, 1, 1), None), (30, 8, date(2021, 1, 1), None)],
    )
    _, summary = cc.compare_frames(EVENT_SPEC, b1, b0, CROSSWALK)
    assert summary["matched_rows"] == 2
    assert summary["coverage_pct"] == 50.0           # 2 of the 4 rows of the reference
    assert summary["precision_pct"] == 66.7          # 2 of our 3 rows


def test_the_same_event_found_with_another_date_is_told_apart_from_a_missing_row():
    """The signature of the date defect: the person and the concept exist on both
    sides, the date differs."""
    b1, b0 = _events([(1, 7, date(2021, 7, 4), None)], [(10, 7, date(2021, 4, 7), None)])
    lines, summary = cc.compare_frames(EVENT_SPEC, b1, b0, CROSSWALK)
    assert summary["matched_rows"] == 0 and summary["date_shifted_keys"] == 1
    assert "AUTRE date" in "\n".join(lines)


def test_a_row_absent_on_one_side_is_not_reported_as_a_shifted_date():
    b1, b0 = _events([(1, 7, date(2021, 7, 4), None)], [(10, 8, date(2021, 7, 4), None)])
    _, summary = cc.compare_frames(EVENT_SPEC, b1, b0, CROSSWALK)
    assert summary["date_shifted_keys"] == 0


def test_a_day_and_month_swapped_in_a_non_key_date_is_a_content_disagreement():
    b1, b0 = _events([(1, 7, date(2020, 1, 1), date(2021, 7, 4))], [(10, 7, date(2020, 1, 1), date(2021, 4, 7))])
    _, summary = cc.compare_frames(EVENT_SPEC, b1, b0, CROSSWALK)
    assert summary["matched_rows"] == 1 and summary["content_agree_pct"] == 0.0


def test_nothing_matched_gives_a_clear_message_and_no_score():
    b1, b0 = _events([(1, 7, date(2020, 1, 1), None)], [(10, 8, date(2020, 1, 1), None)])
    lines, summary = cc.compare_frames(EVENT_SPEC, b1, b0, CROSSWALK)
    assert summary["content_agree_pct"] is None and summary["coverage_pct"] == 0.0
    assert "No matched row" in "\n".join(lines)


# ------------------------------------------------------ duplicated keys

def test_duplicates_of_a_key_are_paired_with_their_true_counterpart():
    """Two rows share a key and arrive in a different order on each side. Pairing
    them by position would compare 1.0 with 5.0 and report two disagreements."""
    spec = {"table": "measurement", "key": ["measurement_concept_id"],
            "content": {"value_as_number": "number"}, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1, 1], "measurement_concept_id": [3, 3], "value_as_number": [1.0, 5.0]})
    b0 = pd.DataFrame({"person_id": [10, 10], "measurement_concept_id": [3, 3], "value_as_number": [5.0, 1.0]})
    _, summary = cc.compare_frames(spec, b1, b0, CROSSWALK)
    assert summary["matched_rows"] == 2 and summary["content_agree_pct"] == 100.0
    assert summary["b1_duplicates"] == 1 and summary["b0_duplicates"] == 1


def test_duplicates_never_produce_more_matches_than_the_smaller_side():
    spec = {"table": "measurement", "key": ["measurement_concept_id"], "content": {"value_as_number": "number"}, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1] * 4, "measurement_concept_id": [3] * 4, "value_as_number": [1.0] * 4})
    b0 = pd.DataFrame({"person_id": [10] * 2, "measurement_concept_id": [3] * 2, "value_as_number": [1.0] * 2})
    _, summary = cc.compare_frames(spec, b1, b0, CROSSWALK)
    assert summary["matched_rows"] == 2


# ------------------------------------------------------ the read of the two schemas

def test_only_the_columns_both_schemas_have_are_compared():
    usable, skipped = cc._comparable_columns(["a", "b", "c"], {"a", "b"}, {"a", "c"})
    assert usable == ["a"] and skipped == ["b", "c"]


class _FakeSession:
    def connection(self):
        return None


@contextlib.contextmanager
def _fake_scope():
    yield _FakeSession()


def _patch_database(monkeypatch, b1_columns, b0_columns, b1, b0):
    monkeypatch.setattr(cc, "b1_session_scope", _fake_scope)
    columns = iter([set(b1_columns), set(b0_columns)])
    monkeypatch.setattr(cc, "_get_columns", lambda session, schema, table: next(columns))
    frames = iter([b1, b0])
    monkeypatch.setattr(cc.pd, "read_sql", lambda query, connection: next(frames)[
        [c for c in str(query).split("SELECT ")[1].split(" FROM ")[0].replace(" ", "").split(",")]])


def test_a_column_missing_from_one_schema_is_skipped_and_reported(monkeypatch):
    b1, b0 = _frames(
        {"person_source_value": ["a"], "gender_concept_id": [8532], "year_of_birth": [1990], "race_concept_id": [8527]},
        {"person_source_value": ["a"], "gender_concept_id": [8532], "year_of_birth": [1990]},
    )
    spec = {"table": "person", "key": ["person_source_value"],
            "content": {"gender_concept_id": "concept", "year_of_birth": "exact", "race_concept_id": "concept"}, "provenance": {}}
    _patch_database(monkeypatch, b1.columns, b0.columns, b1, b0)
    lines, summary = cc.compare_table(spec, CROSSWALK, "omop_fhir", lambda: _fake_scope(), "omop_csv")
    assert "race_concept_id" in "\n".join(lines) and "missing from one of the two schemas" in "\n".join(lines)
    assert "race_concept_id" not in summary["per_field"]
    assert summary["content_agree_pct"] == 100.0


def test_a_table_without_a_key_is_read_and_compared_through_the_database_path(monkeypatch):
    b1, b0 = _frames({"person_source_value": ["9557", "9550", "9527"], "gender_concept_id": [8532, 8507, 8532]},
                     {"person_source_value": ["10098", "10035", "10093"], "gender_concept_id": [8532, 8507, 8532]})
    spec = {"table": "person", "key": [], "content": {"gender_concept_id": "concept"},
            "provenance": {"person_source_value": "text"}}
    _patch_database(monkeypatch, b1.columns, b0.columns, b1, b0)
    lines, summary = cc.compare_table(spec, CROSSWALK, "omop_fhir", lambda: _fake_scope(), "omop_csv")
    assert "error" not in summary and summary["matched_rows"] == 3
    assert summary["per_field"]["gender_concept_id"]["pct"] == 100.0


def test_a_missing_key_column_stops_the_comparison_of_that_table_only(monkeypatch):
    b1, b0 = _frames({"person_source_value": ["a"]}, {"other": ["a"]})
    spec = {"table": "person", "key": ["person_source_value"], "content": {}, "provenance": {}}
    _patch_database(monkeypatch, b1.columns, b0.columns, b1, b0)
    lines, summary = cc.compare_table(spec, CROSSWALK, "omop_fhir", lambda: _fake_scope(), "omop_csv")
    assert "Comparison impossible" in "\n".join(lines) and "error" in summary


# ------------------------------------------------------------- the configuration

def test_every_table_of_the_standard_configuration_is_complete_and_consistent():
    assert sorted(c["table"] for c in runner.TABLE_CONFIGS) == sorted(cc.OUR_TABLES)
    for config in runner.TABLE_CONFIGS:
        # person is already one row per patient, paired by the patient bridge: it needs no further key
        assert config["key"] or config["table"] == "person", config["table"]
        assert config["content"], f"{config['table']} has no content field"
        for field, kind in {**config["content"], **config["provenance"]}.items():
            assert kind in cc.KINDS, f"{config['table']}.{field}: unknown kind {kind}"
        both = set(config["content"]) & set(config["provenance"])
        assert not both, f"{config['table']}: {both} listed as both content and provenance"
        assert not (set(config["content"]) | set(config["provenance"])) & set(config["key"]), config["table"]


def test_provenance_fields_are_always_source_values_or_source_concepts():
    for config in runner.TABLE_CONFIGS:
        for field in config["provenance"]:
            assert field.endswith(("_source_value", "_source_concept_id")), f"{config['table']}.{field}"


def test_no_content_field_is_a_source_representation():
    for config in runner.TABLE_CONFIGS:
        for field in config["content"]:
            assert not field.endswith(("_source_value", "_source_concept_id")), f"{config['table']}.{field}"


def test_the_type_concept_of_a_table_stays_out_of_the_comparison():
    for config in runner.TABLE_CONFIGS:
        compared = set(config["content"]) | set(config["provenance"])
        assert not [f for f in compared if f.endswith("type_concept_id")], config["table"]


# ------------------------------------------------------------ the executive summary

def _summary_for(name, b1, b0, spec_content):
    spec = {"table": name, "key": ["k"], "content": spec_content, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1] * len(b1), "k": range(len(b1)), "v": b1})
    b0 = pd.DataFrame({"person_id": [10] * len(b0), "k": range(len(b0)), "v": b0})
    return cc.compare_frames(spec, b1, b0, CROSSWALK)[1]


def test_the_summary_gives_three_different_figures():
    good = _summary_for("t1", [1, 2, 3, 4], [1, 2, 3, 4], {"v": "exact"})                  # all found, all agree
    partial = _summary_for("t2", [1, 2], [1, 9, 3, 4], {"v": "exact"})                      # 2 of 4 found, 1 agrees
    text = "\n".join(runner.build_executive_summary([good, partial]))
    assert "Coverage of B0 (B0 rows found in B1 / B0 rows): 6/8 (75.0%)" in text
    assert "Content agreement (matched rows whose content fields all agree, weighted by rows): 5/6 (83.3%)" in text
    assert "B0 rows reproduced with the same content (found AND agreeing): 5/8 (62.5%)" in text


def test_a_table_with_little_coverage_cannot_hide_behind_a_high_agreement():
    """One matched row out of ten, and that row agrees: the agreement alone would
    say 100 percent, which is what 44 matched visits out of 6,700 used to say."""
    spec = {"table": "big", "key": ["k"], "content": {"v": "exact"}, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1] * 10, "k": range(10), "v": range(10)})
    b0 = pd.DataFrame({"person_id": [10] * 10, "k": [0] + list(range(100, 109)), "v": [0] + list(range(100, 109))})
    summary = cc.compare_frames(spec, b1, b0, CROSSWALK)[1]
    assert summary["matched_rows"] == 1
    assert summary["content_agree_pct"] == 100.0 and summary["coverage_pct"] == 10.0
    text = "\n".join(runner.build_executive_summary([summary]))
    assert "Content agreement (matched rows whose content fields all agree, weighted by rows): 1/1 (100.0%)" in text
    assert "B0 rows reproduced with the same content (found AND agreeing): 1/10 (10.0%)" in text


def test_a_table_that_failed_is_shown_without_breaking_the_totals():
    good = _summary_for("t1", [1, 2], [1, 2], {"v": "exact"})
    text = "\n".join(runner.build_executive_summary([good, {"table": "broken", "error": "missing key columns ['x']"}]))
    assert "| broken | - | - | - | - | - | - | missing key columns ['x'] |" in text
    assert "2/2 (100.0%)" in text


def test_the_provenance_note_says_the_content_score_leaves_them_out():
    text = "\n".join(runner.build_executive_summary([_summary_for("t1", [1], [1], {"v": "exact"})]))
    assert "Content agreement above covers the content fields only" in text


# ------------------------------------------------ every field, and the cause of each gap

@pytest.mark.parametrize("field, excluded", [
    ("drug_type_concept_id", True), ("provider_id", True), ("care_site_id", True), ("visit_detail_id", True),
    ("person_id", True), ("drug_exposure_id", True), ("visit_occurrence_id", True),
    ("race_concept_id", False), ("unit_concept_id", False), ("quantity", False), ("year_of_birth", False),
    ("drug_source_concept_id", False), ("value_source_value", False),
])
def test_which_fields_are_left_out_when_every_field_is_compared(field, excluded):
    assert cc.is_excluded_field(field) is excluded


def test_expanding_a_spec_adds_every_other_field_with_its_kind_and_role():
    spec = {"table": "person", "key": ["person_source_value"], "content": {"gender_concept_id": "concept"},
            "provenance": {}, "ignored": ["death_type_concept_id"]}
    out = cc.expand_spec(spec, {"person_id", "person_source_value", "gender_concept_id", "year_of_birth", "gender_source_value", "provider_id"},
                         {"gender_concept_id", "birth_datetime", "death_type_concept_id"})
    assert out["content"] == {"gender_concept_id": "concept", "year_of_birth": "exact", "birth_datetime": "datetime"}
    assert out["provenance"] == {"gender_source_value": "text"}
    assert spec["content"] == {"gender_concept_id": "concept"}          # the input is not modified


def _detail(summary, field):
    return next(d for d in summary["field_details"] if d["field"] == field)


def test_a_field_the_baseline_fills_only_with_zero_is_outside_its_scope():
    """ETL-Synthea writes 0 in quantity, refills, lot_number: no valid mapping, so no data."""
    spec = {"table": "drug", "key": ["k"], "content": {"quantity": "number", "dose": "number"}, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1, 2, 3], "k": [1, 2, 3], "quantity": [1.0, 1.0, 1.0], "dose": [5, 6, 7]})
    b0 = pd.DataFrame({"person_id": [10, 20, 30], "k": [1, 2, 3], "quantity": [0.0, 0.0, 0.0], "dose": [9, 6, 1]})
    summary = cc.compare_frames(spec, b1, b0, CROSSWALK)[1]
    assert "quantity" not in summary["per_field"] and "outside the baseline scope" in summary["gaps"]["quantity"]
    assert _detail(summary, "quantity")["status"] == "only_b1" and _detail(summary, "quantity")["agree_pct"] is None
    assert summary["per_field"]["dose"]["pct"] == pytest.approx(33.3, abs=0.1)


def test_a_zero_is_a_value_when_the_baseline_also_writes_other_values():
    spec = {"table": "m", "key": ["k"], "content": {"value_as_number": "number"}, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1, 2], "k": [1, 2], "value_as_number": [0.0, 5.0]})
    b0 = pd.DataFrame({"person_id": [10, 20], "k": [1, 2], "value_as_number": [0.0, 5.0]})
    assert cc.compare_frames(spec, b1, b0, CROSSWALK)[1]["per_field"]["value_as_number"]["pct"] == 100.0


def test_a_constant_of_the_baseline_is_told_apart_from_a_difference_to_review():
    spec = {"table": "drug", "key": ["k"], "content": {"quantity": "number", "dose": "number"}, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1, 2, 3], "k": [1, 2, 3], "quantity": [1.0, 1.0, 1.0], "dose": [5, 6, 7]})
    b0 = pd.DataFrame({"person_id": [10, 20, 30], "k": [1, 2, 3], "quantity": [2.0, 2.0, 2.0], "dose": [9, 6, 1]})
    summary = cc.compare_frames(spec, b1, b0, CROSSWALK)[1]
    assert _detail(summary, "quantity")["cause_auto"] == "baseline_constant"
    assert _detail(summary, "dose")["cause_auto"] == "to_review" and _detail(summary, "dose")["agree"] == 1


def test_a_field_the_baseline_leaves_empty_is_a_gap_with_its_own_cause():
    spec = {"table": "m", "key": ["k"], "content": {"value_as_string": "text"}, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1, 2], "k": [1, 2], "value_as_string": ["a", "b"]})
    b0 = pd.DataFrame({"person_id": [10, 20], "k": [1, 2], "value_as_string": [None, None]})
    detail = _detail(cc.compare_frames(spec, b1, b0, CROSSWALK)[1], "value_as_string")
    assert detail["status"] == "only_b1" and detail["cause_auto"] == "baseline_not_populated"


def test_a_difference_on_a_provenance_field_is_labelled_provenance():
    spec = {"table": "v", "key": ["k"], "content": {}, "provenance": {"visit_source_value": "text"}}
    b1 = pd.DataFrame({"person_id": [1], "k": [1], "visit_source_value": ["410620009"]})
    b0 = pd.DataFrame({"person_id": [10], "k": [1], "visit_source_value": ["534f299e"]})
    assert _detail(cc.compare_frames(spec, b1, b0, CROSSWALK)[1], "visit_source_value")["cause_auto"] == "provenance"


def test_the_key_fields_are_listed_as_not_compared():
    spec = {"table": "v", "key": ["k"], "content": {"x": "exact"}, "provenance": {}}
    frame = pd.DataFrame({"person_id": [1], "k": [1], "x": [1]})
    b0 = frame.assign(person_id=10)
    detail = _detail(cc.compare_frames(spec, frame, b0, CROSSWALK)[1], "k")
    assert detail["role"] == "key" and detail["cause_auto"] == "matched_by_construction" and detail["agree_pct"] is None


def test_the_mean_of_the_fields_does_not_depend_on_how_many_rows_each_field_has():
    spec = {"table": "t", "key": ["k"], "content": {"a": "exact", "b": "exact"}, "provenance": {}}
    b1 = pd.DataFrame({"person_id": [1, 1, 1, 1], "k": range(4), "a": [1, 1, 1, 1], "b": [1, 1, 1, 1]})
    b0 = pd.DataFrame({"person_id": [10] * 4, "k": range(4), "a": [1, 1, 1, 1], "b": [1, 9, 9, 9]})
    summary = cc.compare_frames(spec, b1, b0, CROSSWALK)[1]
    assert summary["field_mean_pct"] == 62.5          # (100 + 25) / 2


def test_compare_table_with_every_field_reports_a_column_only_one_schema_has(monkeypatch):
    b1, b0 = _frames(
        {"person_source_value": ["a"], "gender_concept_id": [8532], "year_of_birth": [1990], "extra_ours": [1]},
        {"person_source_value": ["a"], "gender_concept_id": [8532], "year_of_birth": [1990]},
    )
    spec = {"table": "person", "key": ["person_source_value"], "content": {"gender_concept_id": "concept"},
            "provenance": {}, "all_fields": True}
    _patch_database(monkeypatch, b1.columns, b0.columns, b1, b0)
    summary = cc.compare_table(spec, CROSSWALK, "omop_fhir", lambda: _fake_scope(), "omop_csv")[1]
    assert _detail(summary, "year_of_birth")["agree_pct"] == 100.0
    assert _detail(summary, "extra_ours")["cause_auto"] == "baseline_not_populated"
    assert _detail(summary, "extra_ours")["status"] == "absent_from_baseline_schema"


def test_the_field_file_has_one_row_per_field_and_empty_columns_for_the_human_review(tmp_path):
    spec = {"table": "t", "key": ["k"], "content": {"a": "exact"}, "provenance": {}}
    frame = pd.DataFrame({"person_id": [1], "k": [1], "a": [1]})
    summary = cc.compare_frames(spec, frame, frame.assign(person_id=10, a=2), CROSSWALK)[1]
    path = tmp_path / "out_fields.csv"
    assert runner.write_field_details([summary], path) == 2           # the key and the field
    rows = pd.read_csv(path, dtype=str, keep_default_na=False)
    assert list(rows.columns) == runner.FIELD_DETAIL_COLUMNS
    assert rows.loc[rows.field == "a", "cause_auto"].iloc[0] == "baseline_constant"
    assert (rows["cause_manual"] == "").all()


def test_the_main_report_gives_the_field_mean_per_table_and_no_single_overall_figure():
    summary = _summary_for("t1", [1, 2], [1, 2], {"v": "exact"})
    text = "\n".join(runner.field_agreement_section([summary]))
    assert "| t1 | 1 | 100.0% | - |" in text and "overall" not in text.lower()


# ------------------------------------------------------ output for scripts/aggregate_runs.py
def test_append_run_rows_writes_one_value_per_table_and_replaces_a_rerun(tmp_path):
    import csv
    path = tmp_path / "runs.csv"
    summaries = [{"table": "person", "field_mean_pct": 99.9}, {"table": "death", "field_mean_pct": None},
                 {"table": "visit_occurrence", "field_mean_pct": 88.5, "error": "boom"}]
    assert runner.append_run_rows(summaries, path, "S1", 1) == 1
    runner.append_run_rows([{"table": "person", "field_mean_pct": 97.0}], path, "S1", 1)   # rerun of run 1
    runner.append_run_rows([{"table": "person", "field_mean_pct": 98.0}], path, "S1", 2)
    rows = list(csv.DictReader(path.open()))
    assert [(r["scenario"], r["unit"], r["run"], r["value"]) for r in rows] == [
        ("S1", "person", "1", "0.970000"), ("S1", "person", "2", "0.980000")]
    assert rows[0]["metric"] == "field_agreement" and rows[0]["batch"] == ""


def test_runs_csv_feeds_the_aggregation(tmp_path):
    spec = importlib.util.spec_from_file_location("agg", Path(__file__).resolve().parents[2] / "scripts" / "aggregate_runs.py")
    agg = importlib.util.module_from_spec(spec); spec.loader.exec_module(agg)
    path = tmp_path / "runs.csv"
    for run, v in enumerate([97.0, 98.0, 96.5, 97.5, 98.2], start=1):
        runner.append_run_rows([{"table": "person", "field_mean_pct": v}], path, "S1", run)
    res = agg.analyse(agg.read_runs(str(path)))
    assert res["H2"][("S1", "person")]["n"] == 5 and res["H2"][("S1", "person")]["reject"] is True


# ------------------------------------------------------ the identifier B1 wrote may change from one run to another
def _patients():
    return pd.DataFrame({"ROW_ID": ["9467", "9468", "9469"], "SUBJECT_ID": ["10006", "10011", "10013"]})


def test_pick_source_column_follows_what_each_run_wrote():
    pk = cc.pick_source_column
    assert pk(_patients(), "ROW_ID,SUBJECT_ID", ["9467", "9468", "9469"], "B1") == "ROW_ID"
    assert pk(_patients(), "ROW_ID,SUBJECT_ID", ["10006", "10011"], "B1") == "SUBJECT_ID"
    assert pk(_patients(), "auto", ["10006", "10011", "10013"], "B1") == "SUBJECT_ID"


def test_pick_source_column_names_are_used_as_given_and_ambiguity_is_refused():
    pk = cc.pick_source_column
    assert pk(_patients(), "SUBJECT_ID", ["9467"], "B1") == "SUBJECT_ID"
    assert pk(_patients(), "subject_id", ["9467"], "B1") == "SUBJECT_ID"
    with pytest.raises(ValueError):
        pk(_patients(), "ROW_ID,SUBJECT_ID", ["zzz"], "B1")
    same = pd.DataFrame({"A": ["1", "2"], "B": ["1", "2"]})
    with pytest.raises(ValueError):
        pk(same, "auto", ["1", "2"], "B1")
    with pytest.raises(ValueError):
        pk(_patients(), "ROW_ID,NOPE", ["9467"], "B1")


def test_pick_source_column_ignores_case_of_names_and_returns_the_real_column():
    lower = _patients().rename(columns=str.lower)
    assert cc.pick_source_column(lower, "ROW_ID,SUBJECT_ID", ["10006", "10011"], "B1") == "subject_id"
    assert cc.pick_source_column(lower, "Row_Id", ["9467"], "B1") == "row_id"
    with pytest.raises(ValueError):
        cc.pick_source_column(lower, "NOPE", ["9467"], "B1")
