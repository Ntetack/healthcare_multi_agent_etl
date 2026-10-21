"""Tests for the snapshot of omop_temp. The SQL itself is built and checked
here; running it against the database is left to a real run."""
from __future__ import annotations

import pytest

from scripts.snapshot_omop_temp import build_snapshot_statements, validate_target_schema

TABLES = ["person", "visit_occurrence", "measurement"]


def test_a_plain_schema_name_is_accepted():
    assert validate_target_schema("omop_csv", "omop_temp", "omop") == "omop_csv"
    assert validate_target_schema("_run_2", "omop_temp", "omop") == "_run_2"


@pytest.mark.parametrize(
    "name",
    ["Omop_CSV", "omop-csv", "1omop", "omop csv", 'x"; DROP TABLE person; --', "omop;", "", "a" * 64],
)
def test_an_unsafe_or_invalid_schema_name_is_rejected(name):
    with pytest.raises(ValueError):
        validate_target_schema(name, "omop_temp", "omop")


@pytest.mark.parametrize("name", ["omop_temp", "omop", "cdm_vocab", "staging", "pipeline_meta", "public"])
def test_the_schemas_of_the_pipeline_can_never_be_a_target(name):
    with pytest.raises(ValueError, match="used by the pipeline"):
        validate_target_schema(name, "omop_temp", "omop")


def test_a_renamed_final_schema_is_protected_too():
    with pytest.raises(ValueError, match="used by the pipeline"):
        validate_target_schema("omop_prod", "omop_temp", "omop_prod")


def test_the_statements_create_the_schema_then_copy_each_table():
    statements = build_snapshot_statements("omop_temp", "omop_csv", TABLES, replace=False)
    assert statements[0] == 'CREATE SCHEMA "omop_csv"'
    assert statements[1:] == [
        'CREATE TABLE "omop_csv"."person" AS TABLE "omop_temp"."person"',
        'CREATE TABLE "omop_csv"."visit_occurrence" AS TABLE "omop_temp"."visit_occurrence"',
        'CREATE TABLE "omop_csv"."measurement" AS TABLE "omop_temp"."measurement"',
    ]


def test_without_replace_nothing_is_dropped():
    assert not any("DROP" in s for s in build_snapshot_statements("omop_temp", "omop_csv", TABLES, replace=False))


def test_replace_drops_the_target_schema_first():
    statements = build_snapshot_statements("omop_temp", "omop_csv", TABLES, replace=True)
    assert statements[0] == 'DROP SCHEMA IF EXISTS "omop_csv" CASCADE'
    assert statements[1] == 'CREATE SCHEMA "omop_csv"'


def test_the_nine_cdm_tables_are_copied_by_default():
    from app.tools.database.db import OMOP_TABLES

    statements = build_snapshot_statements("omop_temp", "omop_csv", list(OMOP_TABLES), replace=False)
    assert len(statements) == 1 + 9
    assert any('"death"' in s for s in statements) and any('"observation_period"' in s for s in statements)
