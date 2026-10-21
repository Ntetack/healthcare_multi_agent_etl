"""A weak structural guess must never reach row assembly.

Regression: a model returned DIAGNOSES_ICD.hadm_id -> condition_start_date at
confidence 0.30. With the old threshold (0.3, strict '<') it passed and put
admission ids in a date column.
"""
from app.agents.loading import MIN_STRUCTURAL_CONFIDENCE, LoadingAgent


def _plain(conf):
    return {"target_field": "condition_start_date", "source_value": None, "confidence": conf}


def test_threshold_is_above_the_weak_guess_seen_in_practice():
    assert MIN_STRUCTURAL_CONFIDENCE > 0.30


def test_plain_guess_at_030_is_dropped():
    assert LoadingAgent._filter_low_confidence_plain_fields([_plain(0.30)]) == []


def test_plain_guess_at_threshold_is_kept():
    m = _plain(MIN_STRUCTURAL_CONFIDENCE)
    assert LoadingAgent._filter_low_confidence_plain_fields([m]) == [m]


def test_confident_plain_guess_is_kept():
    m = _plain(0.8)
    assert LoadingAgent._filter_low_confidence_plain_fields([m]) == [m]


def test_missing_confidence_is_kept():
    m = {"target_field": "x", "source_value": None, "confidence": None}
    assert LoadingAgent._filter_low_confidence_plain_fields([m]) == [m]


def test_vocab_field_threshold_unchanged():
    weak = {"target_field": "race_concept_id", "source_value": "ASIAN", "confidence": 0.5}
    strong = {"target_field": "race_concept_id", "source_value": "WHITE", "confidence": 0.95}
    assert LoadingAgent._filter_low_confidence_plain_fields([weak, strong]) == [strong]
