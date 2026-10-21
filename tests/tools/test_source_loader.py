"""Genericity check: load_source_tables() must auto-discover DISTINCT
tables in a batch folder (MIMIC-style: PATIENTS/DIAGNOSES/LABEVENTS, or
OMOP-native: person/condition_occurrence, or FHIR: one resource type per
table) WITHOUT merging different tables together - satisfying the "any
source, real multi-table hospital exports" requirement."""
import pandas as pd

from app.tools.data.source_loader import load_source, load_source_tables


def test_load_source_single_csv_file(tmp_path):
    p = tmp_path / "sample.csv"
    p.write_text("patient_id,diagnosis_code\n1,A00.1\n2,B01.0\n")
    df = load_source("csv", p)
    assert "patient_id" in df.columns and "diagnosis_code" in df.columns
    assert len(df) == 2


def test_load_source_tables_mimic_style_batch(tmp_path):
    """A real MIMIC-style batch: several DISTINCT tables in one folder."""
    (tmp_path / "PATIENTS.csv").write_text("subject_id,gender\n1,F\n2,M\n")
    (tmp_path / "DIAGNOSES.csv").write_text("subject_id,icd_code\n1,A00.1\n1,B01.0\n2,C02.3\n")
    (tmp_path / "LABEVENTS.csv").write_text("subject_id,itemid,value\n1,50801,7.4\n")

    tables = load_source_tables("csv", tmp_path)

    assert set(tables.keys()) == {"PATIENTS", "DIAGNOSES", "LABEVENTS"}
    assert len(tables["PATIENTS"]) == 2
    assert len(tables["DIAGNOSES"]) == 3
    assert len(tables["LABEVENTS"]) == 1
    # Tables must NOT be merged: PATIENTS never gets DIAGNOSES' columns.
    assert "icd_code" not in tables["PATIENTS"].columns


def test_load_source_tables_split_file_same_table_merges(tmp_path):
    """Two files of the SAME table (e.g. DIAGNOSES_part1/part2) should
    merge into one table, unlike genuinely different tables."""
    (tmp_path / "DIAGNOSES_part1.csv").write_text("subject_id,icd_code\n1,A00.1\n")
    (tmp_path / "DIAGNOSES_part2.csv").write_text("subject_id,icd_code\n2,B01.0\n")

    tables = load_source_tables("csv", tmp_path)

    assert set(tables.keys()) == {"DIAGNOSES"}
    assert len(tables["DIAGNOSES"]) == 2


def test_load_ndjson_fhir_groups_by_resource_type(tmp_path):
    p = tmp_path / "bundle.ndjson"
    p.write_text(
        '{"resourceType": "Condition", "id": "c1", "code": {"text": "flu"}}\n'
        '{"resourceType": "Observation", "id": "o1", "code": {"text": "glucose"}}\n'
    )
    tables = load_source_tables("fhir", tmp_path)
    assert set(tables.keys()) == {"Condition", "Observation"}


def test_load_fhir_bundle_format_synthea_default(tmp_path):
    """Synthea's DEFAULT FHIR export: one pretty-printed Bundle JSON
    document per patient file, not true NDJSON."""
    import json as _json
    bundle = {
        "resourceType": "Bundle",
        "entry": [
            {"resource": {"resourceType": "Condition", "id": "c1", "code": {"text": "flu"}}},
            {"resource": {"resourceType": "Observation", "id": "o1", "code": {"text": "glucose"}}},
        ],
    }
    p = tmp_path / "patient1_Bundle.json"
    p.write_text(_json.dumps(bundle, indent=2))  # pretty-printed, multi-line

    tables = load_source_tables("fhir", tmp_path)
    assert set(tables.keys()) == {"Condition", "Observation"}


def test_load_fhir_standalone_single_resource(tmp_path):
    import json as _json
    p = tmp_path / "one_resource.json"
    p.write_text(_json.dumps({"resourceType": "Patient", "id": "p1", "gender": "female"}, indent=2))

    tables = load_source_tables("fhir", tmp_path)
    assert set(tables.keys()) == {"Patient"}


def test_load_source_tables_empty_folder_raises(tmp_path):
    try:
        load_source_tables("csv", tmp_path)
        assert False, "should have raised"
    except FileNotFoundError:
        pass


def test_unsupported_format_raises():
    try:
        load_source("xml", "whatever.xml")
        assert False, "should have raised"
    except ValueError:
        pass
