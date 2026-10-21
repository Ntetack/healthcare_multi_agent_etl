"""Local vocabulary fields: join check on sparse keys, vocabulary chosen from
real labels, and the lookup policy a source declares in metadata.yaml.

No database and no model are needed: lookups and the LLM are faked.
"""
import json

import pandas as pd
import pytest

from app.tools.mapping import local_vocab_resolver as lvr


# --- apply_local_vocab_join: overlap measured on the filled keys ------------

SPEC = {"join_key_source": "ab_itemid", "join_key_target": "itemid", "resolved_column": "label"}
DICTIONARY = pd.DataFrame({"itemid": ["1", "2"], "label": ["GENTAMICIN", "AMIKACIN"]})


def test_sparse_key_with_every_filled_key_matching_is_accepted():
    # 3 of 6 rows carry a key (0.5 would be rejected if empties counted)
    facts = pd.DataFrame({"ab_itemid": ["1", "", "2", "", "1", ""]})
    out = lvr.apply_local_vocab_join(facts, DICTIONARY, SPEC)
    assert out is not None
    assert out.tolist()[0] == "GENTAMICIN"


def test_wrong_join_is_still_rejected():
    facts = pd.DataFrame({"ab_itemid": ["9", "8", "7", "1"]})
    assert lvr.apply_local_vocab_join(facts, DICTIONARY, SPEC) is None


def test_column_without_any_key_is_rejected():
    facts = pd.DataFrame({"ab_itemid": ["", " ", None]})
    assert lvr.apply_local_vocab_join(facts, DICTIONARY, SPEC) is None


# --- sample_distinct_labels ---------------------------------------------------

def test_sample_is_small_distinct_and_deterministic():
    labels = pd.Series([f"item {i:03d}" for i in range(100)] * 2 + ["Heart Rate"] * 50)
    first, n = lvr.sample_distinct_labels(labels)
    again, _ = lvr.sample_distinct_labels(labels.sample(frac=1, random_state=3))
    assert n == 101
    assert len(first) == 10 and len(set(first)) == 10
    assert first == again
    assert first[0] == "Heart Rate"            # most frequent first
    assert any(x.startswith("item 09") for x in first)  # tail is represented


def test_short_list_is_returned_whole_and_blanks_ignored():
    sample, n = lvr.sample_distinct_labels(pd.Series(["B", "A", "", None, " ", "A"]))
    assert n == 2 and sample == ["A", "B"]


# --- resolve_standards_from_labels -------------------------------------------

class _LLM:
    def __init__(self, content):
        self.content, self.calls, self.prompts = content, 0, []

    def invoke(self, prompt):
        self.calls += 1
        self.prompts.append(prompt)
        return type("R", (), {"content": self.content})()


@pytest.fixture
def cache(monkeypatch):
    store = {}
    monkeypatch.setattr(lvr, "get_cached_resolution", lambda s, k, t, f: store.get((s, k, t, f)))
    monkeypatch.setattr(lvr, "store_resolution", lambda s, k, t, f, r: store.__setitem__((s, k, t, f), dict(r)))
    return store


def _ask(llm, fallback=("RxNorm",)):
    return lvr.resolve_standards_from_labels(
        llm, "MICRO", "ab_itemid", ["GENTAMICIN", "AMIKACIN"], 28, "src", list(fallback))


def test_labels_are_shown_and_answer_is_cached(cache):
    llm = _LLM(json.dumps({"resolved_standards": ["LOINC"], "confidence": 0.9, "reason": "susceptibility"}))
    assert _ask(llm) == ["LOINC"]
    assert "GENTAMICIN" in llm.prompts[0] and "28 in total" in llm.prompts[0]
    assert _ask(llm) == ["LOINC"]
    assert llm.calls == 1                      # second call served from the cache


def test_unusable_answers_fall_back_and_are_not_cached(cache):
    for content in ("not json", json.dumps({"resolved_standards": "LOINC"}),
                    json.dumps({"resolved_standards": ["NOT_A_VOCAB"]})):
        assert _ask(_LLM(content)) == ["RxNorm"]
    assert cache == {}


def test_empty_list_is_kept_and_unknown_names_are_dropped(cache):
    assert _ask(_LLM(json.dumps({"resolved_standards": []}))) == []
    cache.clear()
    assert _ask(_LLM(json.dumps({"resolved_standards": ["NOT_A_VOCAB", "LOINC"]}))) == ["LOINC"]


# --- declared override --------------------------------------------------------

CFG = {"local_vocab_overrides": {"microbiologyevents": {"AB_ITEMID": {"resolved_standards": ["LOINC"]}}}}


def test_override_is_found_whatever_the_case():
    assert lvr.get_local_vocab_override(CFG, "MICROBIOLOGYEVENTS", "ab_itemid") == {"resolved_standards": ["LOINC"]}
    assert lvr.get_local_vocab_override(CFG, "LABEVENTS", "itemid") is None
    assert lvr.get_local_vocab_override({}, "X", "y") is None


# --- resolve_concept_with_policy -----------------------------------------------

def _fake_lookup(monkeypatch, names):
    seen = []

    def lookup(name, standards):
        seen.append(name)
        concept = names.get(name.casefold())
        if concept is None:
            return {"source_concept": None, "standard_concept": None}
        return {"source_concept": concept, "standard_concept": concept}

    monkeypatch.setattr(lvr, "resolve_concept_exact_by_name", lookup)
    return seen


MIC = "{label} [Susceptibility] by Minimum inhibitory concentration (MIC)"
GENERIC = "{label} [Susceptibility]"


def test_first_template_wins_and_is_traced(monkeypatch):
    seen = _fake_lookup(monkeypatch, {
        "gentamicin [susceptibility] by minimum inhibitory concentration (mic)": {"concept_id": 1},
        "gentamicin [susceptibility]": {"concept_id": 2}})
    out = lvr.resolve_concept_with_policy("GENTAMICIN", ["LOINC"], [MIC, GENERIC])
    assert out["standard_concept"]["concept_id"] == 1
    assert out["matched_name"].startswith("GENTAMICIN [Susceptibility] by")
    assert len(seen) == 1


def test_falls_back_to_the_next_template(monkeypatch):
    _fake_lookup(monkeypatch, {"vancomycin [susceptibility]": {"concept_id": 2}})
    out = lvr.resolve_concept_with_policy("VANCOMYCIN", ["LOINC"], [MIC, GENERIC])
    assert out["standard_concept"]["concept_id"] == 2


def test_alias_rewrites_the_label_before_the_templates(monkeypatch):
    _fake_lookup(monkeypatch, {"piperacillin+tazobactam [susceptibility]": {"concept_id": 3}})
    out = lvr.resolve_concept_with_policy(
        "piperacillin/tazo", ["LOINC"], [GENERIC], {"PIPERACILLIN/TAZO": "Piperacillin+Tazobactam"})
    assert out["standard_concept"]["concept_id"] == 3


def test_nothing_found_stays_unresolved_and_never_guesses(monkeypatch):
    _fake_lookup(monkeypatch, {})
    out = lvr.resolve_concept_with_policy("UNKNOWN DRUG", ["LOINC"], [MIC, GENERIC])
    assert out["standard_concept"] is None and out["source_concept"] is None


def test_without_policy_it_is_the_plain_exact_lookup(monkeypatch):
    seen = _fake_lookup(monkeypatch, {"heart rate": {"concept_id": 4}})
    out = lvr.resolve_concept_with_policy("  Heart   Rate ", ["LOINC"])
    assert out["standard_concept"]["concept_id"] == 4
    assert seen == ["Heart Rate"]


def test_placeholder_is_not_looked_up(monkeypatch):
    seen = _fake_lookup(monkeypatch, {})
    out = lvr.resolve_concept_with_policy("", ["LOINC"], [GENERIC])
    assert out["standard_concept"] is None and seen == []
