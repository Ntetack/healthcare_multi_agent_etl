"""Metadata now lives INSIDE each batch folder, not at the source level -
so schema drift between batches of the same source can never make a
stale central/source-level file lie about the current batch's structure.

YAML shape is nested by file, then field:
    format: csv
    files:
      conditions.csv:
        CODE:
          standard: SNOMED
"""
import pytest

from app.tools.data.metadata_loader import (
    get_declared_fields_for_table,
    get_field_standard,
    read_batch_metadata,
)

_YAML_TEMPLATE = """format: csv
files:
  {table}.csv:
    {field}:
      standard: {standard}
"""


def test_read_batch_metadata(tmp_path):
    (tmp_path / "metadata.yaml").write_text(_YAML_TEMPLATE.format(table="DIAGNOSES", field="icd_code", standard="ICD10"))
    cfg = read_batch_metadata(tmp_path)
    assert cfg["format"] == "csv"
    assert cfg["tables"] == {"diagnoses": {"icd_code": "ICD10"}}


def test_read_batch_metadata_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_batch_metadata(tmp_path)


def test_table_key_extension_is_optional(tmp_path):
    """'conditions.csv' and 'conditions' as a YAML key must both resolve
    to the table name 'conditions' that load_source_tables() derives."""
    (tmp_path / "metadata.yaml").write_text(
        "format: csv\nfiles:\n  conditions.csv:\n    CODE:\n      standard: SNOMED\n"
    )
    cfg = read_batch_metadata(tmp_path)
    assert "conditions" in cfg["tables"]
    assert get_field_standard(cfg, "conditions", "CODE") == "SNOMED"


def test_standard_alias_normalized(tmp_path):
    """'SNOMED-CT' (as commonly written) must resolve to 'SNOMED' (the
    OMOP vocabulary_id used everywhere else, e.g. semantic_mapper.py)."""
    (tmp_path / "metadata.yaml").write_text(
        "format: csv\nfiles:\n  conditions.csv:\n    CODE:\n      standard: SNOMED-CT\n"
    )
    cfg = read_batch_metadata(tmp_path)
    assert get_field_standard(cfg, "conditions", "CODE") == "SNOMED"


def test_two_batches_can_declare_different_schemas(tmp_path):
    """The core requirement: schema drift between batches must not bleed
    across - each batch's metadata is independent."""
    batch1 = tmp_path / "batch1"
    batch1.mkdir()
    (batch1 / "metadata.yaml").write_text(_YAML_TEMPLATE.format(table="DIAGNOSES", field="icd_code", standard="ICD10"))

    batch2 = tmp_path / "batch2"
    batch2.mkdir()
    (batch2 / "metadata.yaml").write_text(_YAML_TEMPLATE.format(table="DIAGNOSES", field="diagnosis_code", standard="ICD10"))

    cfg1 = read_batch_metadata(batch1)
    cfg2 = read_batch_metadata(batch2)

    assert get_field_standard(cfg1, "DIAGNOSES", "icd_code") == "ICD10"
    assert get_field_standard(cfg1, "DIAGNOSES", "diagnosis_code") is None  # batch1 doesn't know this field
    assert get_field_standard(cfg2, "DIAGNOSES", "diagnosis_code") == "ICD10"  # batch2 renamed the column


def test_get_declared_fields_for_table_multiple_fields(tmp_path):
    (tmp_path / "metadata.yaml").write_text(
        "format: csv\nfiles:\n"
        "  medications.csv:\n"
        "    CODE:\n      standard: RxNorm\n"
        "    REASONCODE:\n      standard: SNOMED-CT\n"
    )
    cfg = read_batch_metadata(tmp_path)
    fields = get_declared_fields_for_table(cfg, "medications")
    assert {f["name"] for f in fields} == {"CODE", "REASONCODE"}
    standards = {f["name"]: f["standard"] for f in fields}
    assert standards["CODE"] == "RxNorm"
    assert standards["REASONCODE"] == "SNOMED"  # alias normalized here too


def test_fhir_resources_shape(tmp_path):
    """The FHIR variant uses 'resources:' keyed by resource type instead
    of 'files:' keyed by filename - must normalize into the exact same
    internal shape as the CSV variant."""
    (tmp_path / "metadata.yaml").write_text(
        "format: fhir\nresources:\n"
        "  Condition:\n    code:\n      standard: SNOMED-CT\n"
        "  MedicationRequest:\n    medicationCodeableConcept:\n      standard: RxNorm\n"
    )
    cfg = read_batch_metadata(tmp_path)
    assert cfg["format"] == "fhir"
    assert get_field_standard(cfg, "Condition", "code") == "SNOMED"
    assert get_field_standard(cfg, "MedicationRequest", "medicationCodeableConcept") == "RxNorm"


def test_csv_and_fhir_normalize_to_the_same_internal_shape(tmp_path):
    """Exactly two canonical YAML shapes exist - downstream code
    (get_field_standard, get_declared_fields_for_table) must not need to
    know which one was used."""
    csv_folder = tmp_path / "csv_batch"
    csv_folder.mkdir()
    (csv_folder / "metadata.yaml").write_text(
        "format: csv\nfiles:\n  conditions.csv:\n    CODE:\n      standard: SNOMED\n"
    )
    fhir_folder = tmp_path / "fhir_batch"
    fhir_folder.mkdir()
    (fhir_folder / "metadata.yaml").write_text(
        "format: fhir\nresources:\n  Condition:\n    CODE:\n      standard: SNOMED\n"
    )

    csv_cfg = read_batch_metadata(csv_folder)
    fhir_cfg = read_batch_metadata(fhir_folder)

    # Same table name ("conditions" vs "Condition" differ by content, not
    # shape) - the point is both produce the same {table: {field: standard}}
    # dict structure, just with different keys reflecting the real names.
    assert list(csv_cfg["tables"].values()) == list(fhir_cfg["tables"].values())
    assert get_field_standard(csv_cfg, "conditions", "CODE") == "SNOMED"
    assert get_field_standard(fhir_cfg, "Condition", "CODE") == "SNOMED"


def test_table_matching_is_case_insensitive(tmp_path):
    """The exact production bug: MIMIC-III's real files are named in
    ALL CAPS (DIAGNOSES_ICD.csv), but metadata.yaml declared them in
    lowercase - every declared field was silently lost because the
    lookup was an exact, case-sensitive match. Must work regardless of
    which case either side uses."""
    (tmp_path / "metadata.yaml").write_text(
        "format: csv\nfiles:\n  diagnoses_icd.csv:\n    ICD9_CODE:\n      standard: ICD9CM\n"
    )
    cfg = read_batch_metadata(tmp_path)
    fields = get_declared_fields_for_table(cfg, "DIAGNOSES_ICD")
    assert fields == [{"name": "ICD9_CODE", "standard": "ICD9CM"}]
    assert get_field_standard(cfg, "DIAGNOSES_ICD", "ICD9_CODE") == "ICD9CM"


def test_local_vocab_overrides_survive_loading(tmp_path):
    """A source's declared lookup policy for a local field must reach the
    Mapping Agent: the loader returns only the keys it knows, so a key it
    does not list is silently dropped."""
    from app.tools.mapping.local_vocab_resolver import get_local_vocab_override

    (tmp_path / "metadata.yaml").write_text(
        "format: csv\n"
        "files:\n  microbiologyevents.csv:\n    AB_ITEMID:\n      standard: local\n"
        "local_vocab_overrides:\n"
        "  MICROBIOLOGYEVENTS:\n    ab_itemid:\n      resolved_standards: [LOINC]\n"
        "      name_templates: ['{label} [Susceptibility]']\n"
    )
    cfg = read_batch_metadata(tmp_path)
    override = get_local_vocab_override(cfg, "microbiologyevents", "AB_ITEMID")
    assert override == {"resolved_standards": ["LOINC"], "name_templates": ["{label} [Susceptibility]"]}


def test_no_override_declared_gives_an_empty_mapping(tmp_path):
    (tmp_path / "metadata.yaml").write_text(_YAML_TEMPLATE.format(table="X", field="f", standard="local"))
    assert read_batch_metadata(tmp_path)["local_vocab_overrides"] == {}
