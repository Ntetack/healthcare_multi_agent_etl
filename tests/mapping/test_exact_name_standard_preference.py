"""A free-text label resolved by exact name must yield a STANDARD, valid
concept, never a classification or deprecated one that merely shares the name.

Regression for a real defect: the LOINC name "Heart rate" belongs to a
Standard concept (3027018) and to a Classification one (45876226). The
resolver took whichever row came first, so 15,490 measurement rows carried
the classification concept. No database is needed: sessions are faked.
"""
from contextlib import contextmanager

import pytest

from app.tools.mapping import local_vocab_resolver as lvr
from app.tools.mapping.semantic import semantic_mapper as sm


class _Result:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows

    def first(self):
        return self._rows[0] if self._rows else None


class _Session:
    def __init__(self, answers):
        self.answers = list(answers)
        self.statements = []

    def execute(self, statement, params=None):
        self.statements.append(str(statement))
        return _Result(self.answers.pop(0) if self.answers else [])


def _row(cid, name, standard, invalid=None, vocab="LOINC", domain="Measurement"):
    return {"concept_id": cid, "concept_name": name, "concept_code": str(cid),
            "vocabulary_id": vocab, "domain_id": domain,
            "standard_concept": standard, "invalid_reason": invalid}


@pytest.fixture
def install(monkeypatch):
    def _install(*answers):
        session = _Session(answers)

        @contextmanager
        def scope():
            yield session

        monkeypatch.setattr(lvr, "session_scope", scope)
        monkeypatch.setattr(sm, "session_scope", scope)
        return session
    return _install


def test_standard_beats_classification_whatever_the_row_order(install):
    classif = _row(45876226, "Heart rate", "C")
    standard = _row(3027018, "Heart rate", "S")
    for rows in ([classif, standard], [standard, classif]):
        install(rows)
        out = lvr.resolve_concept_exact_by_name("Heart Rate", ["LOINC"])
        assert out["standard_concept"]["concept_id"] == 3027018
        assert out["source_concept"]["concept_id"] == 3027018


def test_a_deprecated_standard_is_not_chosen_over_a_valid_one(install):
    old = _row(1, "Creatine kinase.MB", "S", invalid="D")
    new = _row(2, "Creatine kinase.MB", "S")
    install([old, new])
    assert lvr.resolve_concept_exact_by_name("creatine kinase.mb", ["LOINC"])["standard_concept"]["concept_id"] == 2


def test_a_deprecated_only_name_gives_no_standard_concept(install):
    install([_row(1, "Old lab", "S", invalid="D")], [])
    out = lvr.resolve_concept_exact_by_name("Old lab", ["LOINC"])
    assert out["standard_concept"] is None


def test_non_standard_name_follows_maps_to(install):
    source = _row(10, "Some local name", None, vocab="SNOMED")
    target = _row(20, "Standard target", "S", vocab="SNOMED")
    session = install([source], [target])
    out = lvr.resolve_concept_exact_by_name("Some local name", ["SNOMED"])
    assert out["source_concept"]["concept_id"] == 10
    assert out["standard_concept"]["concept_id"] == 20
    assert "maps to" in session.statements[1].lower()


def test_non_standard_without_target_is_source_only(install):
    install([_row(10, "Orphan", "C")], [])
    out = lvr.resolve_concept_exact_by_name("Orphan", ["LOINC"])
    assert out["standard_concept"] is None
    assert out["source_concept"]["concept_id"] == 10


def test_classification_is_never_returned_as_standard(install):
    install([_row(45876226, "Heart rate", "C")], [])
    assert lvr.search_concept_exact_only("Heart rate", ["LOINC"]) is None


def test_later_vocabulary_standard_beats_earlier_non_standard(install):
    install([_row(1, "Dopamine", None, vocab="RxNorm")], [], [_row(2, "Dopamine", "S", vocab="LOINC")])
    out = lvr.resolve_concept_exact_by_name("Dopamine", ["RxNorm", "LOINC"])
    assert out["standard_concept"]["concept_id"] == 2


def test_placeholder_and_empty_never_reach_the_database(install):
    session = install()
    assert lvr.resolve_concept_exact_by_name("0", ["LOINC"]) == {"source_concept": None, "standard_concept": None}
    assert lvr.resolve_concept_exact_by_name("x", []) == {"source_concept": None, "standard_concept": None}
    assert session.statements == []


def test_name_query_is_exact_and_ordered_by_status():
    sql = lvr._NAME_CANDIDATES_SQL.lower()
    for forbidden in ("ilike", "similarity", " like "):
        assert forbidden not in sql
    assert "standard_concept = 's'" in sql and "invalid_reason is null" in sql
    assert sql.index("order by") < sql.index("limit")


def test_code_search_orders_standard_valid_first(install):
    session = install([])
    sm.search_concept("3027018", "LOINC", require_standard=False)
    sql = session.statements[0].lower()
    assert "standard_concept = 's'" in sql and "invalid_reason is null" in sql
    assert sql.index("order by") < sql.index("limit")
