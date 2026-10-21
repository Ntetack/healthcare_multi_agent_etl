"""Matching is exact for every vocabulary, and placeholder values are never
searched.

Regression for a real defect: the NDC placeholder "0" was searched with
`concept_name ILIKE '%0%'`, matched concepts whose names merely contain a
zero, and attached a rectal cream to 1,477 drug_exposure rows. "Solution" and
"Lactic acid" came from the same substring tier. These tests need no database:
a recording session stands in for the CONCEPT table.
"""
from contextlib import contextmanager

import pytest

from app.tools.mapping.semantic import semantic_mapper as sm


class _Result:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _RecordingSession:
    def __init__(self, rows_by_call):
        self.statements: list[str] = []
        self.params: list[dict] = []
        self._rows_by_call = list(rows_by_call)

    def execute(self, statement, params=None):
        self.statements.append(str(statement))
        self.params.append(params or {})
        rows = self._rows_by_call.pop(0) if self._rows_by_call else []
        return _Result(rows)


@pytest.fixture
def recorder(monkeypatch):
    """Returns a function installing a session that answers with the given
    rows, one list per SQL call, and returns that session."""
    def install(*rows_by_call):
        session = _RecordingSession(rows_by_call)

        @contextmanager
        def fake_scope():
            yield session

        monkeypatch.setattr(sm, "session_scope", fake_scope)
        return session

    return install


def _row(concept_id, code, name, standard="S"):
    return {
        "concept_id": concept_id, "concept_code": code, "concept_name": name,
        "vocabulary_id": "NDC", "domain_id": "Drug", "standard_concept": standard,
    }


# ----------------------------------------------------------- placeholders ---

@pytest.mark.parametrize("value", ["0", " 0 ", "nan", "NaN", "None", "null", "N/A", "n/a", "NA", "-", "--", "?", "."])
def test_placeholder_values_are_never_searched(recorder, value):
    session = recorder([_row(1, "003630641", "glycerin 10mg/g Rectal Cream", standard=None)])
    assert sm.search_concept(value, "NDC", require_standard=False) == []
    assert session.statements == [], "a placeholder must not reach the database"


def test_is_placeholder_keeps_real_values():
    for value in ["00074729501", "Unknown", "Other", "10", "40", "J45.909", "Male", "M"]:
        assert not sm.is_placeholder(value), value
    for value in ["", "   ", None, "0", "NAN"]:
        assert sm.is_placeholder(value), value


def test_resolve_concept_pair_returns_nothing_for_a_placeholder(recorder):
    session = recorder()
    assert sm.resolve_concept_pair("0", "NDC") == {"source_concept": None, "standard_concept": None}
    assert session.statements == []


# ------------------------------------------------------- no approximate tiers ---

@pytest.mark.parametrize("standard", ["NDC", "SNOMED", "LOINC", "RxNorm", "CPT4", "ICD9CM", "Gender"])
def test_no_substring_or_similarity_sql_for_any_vocabulary(recorder, standard):
    session = recorder([], [], [])
    sm.search_concept("Solution", standard, require_standard=False)
    assert session.statements, "the exact query must run"
    for sql in session.statements:
        lowered = sql.lower()
        assert "ilike" not in lowered
        assert "similarity" not in lowered
        assert " like " not in lowered
    assert all("like_code" not in p and "threshold" not in p for p in session.params)


def test_a_miss_ends_the_search(recorder):
    # One query for an ordinary value; no second "fuzzy" round after a miss.
    session = recorder([], [])
    assert sm.search_concept("something absent", "SNOMED") == []
    assert len(session.statements) == 1


def test_the_negation_variant_is_still_tried_exactly(recorder):
    session = recorder([], [])
    sm.search_concept("nonsmoker", "SNOMED")
    assert [p["code"] for p in session.params] == ["nonsmoker", "not smoker"]
    assert all("ilike" not in s.lower() and "similarity" not in s.lower() for s in session.statements)


def test_query_is_ordered_so_the_exact_code_wins_inside_the_limit(recorder):
    session = recorder([])
    sm.search_concept("003630641", "NDC", require_standard=False)
    sql = session.statements[0].lower()
    assert "order by" in sql
    assert sql.index("order by") < sql.index("limit")


# --------------------------------------------------------- exact results ---

def test_exact_code_match_has_full_confidence(recorder):
    recorder([_row(36189414, "003630641", "some drug")])
    found = sm.resolve_concept_pair("003630641", "NDC")
    assert found["source_concept"]["concept_id"] == 36189414
    assert found["source_concept"]["_match_confidence"] == 1.0


def test_exact_name_match_has_the_name_confidence(recorder):
    recorder([_row(1707687, "11124", "vancomycin")])
    found = sm.map_concept("Vancomycin", "RxNorm")
    assert found["concept_id"] == 1707687
    assert found["_match_confidence"] == pytest.approx(0.95)


def test_exact_code_outranks_a_name_match_in_the_same_result(recorder):
    by_name = _row(2, "X1", "ABC")
    by_code = _row(1, "ABC", "something else")
    recorder([by_name, by_code])
    assert sm.search_concept("ABC", "SNOMED", limit=1)[0]["concept_id"] == 1


def test_no_row_means_no_concept(recorder):
    recorder([])
    assert sm.map_concept("Hyspanic", "Ethnicity") is None
    recorder([])
    assert sm.resolve_concept_pair("not a code", "SNOMED") == {"source_concept": None, "standard_concept": None}
