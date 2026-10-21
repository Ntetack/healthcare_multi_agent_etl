"""The agent finds out WHICH VARIANT of a concept a source means.

No person declares it: the vocabulary is searched for the sampled labels, the
qualifiers found for most of them are shown to the model with real rows, and
it picks among them. Vocabulary lookups and the model are faked.
"""
import json

import pandas as pd
import pytest

from app.tools.mapping import local_vocab_resolver as lvr

GENERIC = " [Susceptibility]"
MIC = " [Susceptibility] by Minimum inhibitory concentration (MIC)"
DISK = " [Susceptibility] by Disk diffusion (KB)"

ANTIBIOTICS = ["GENTAMICIN", "AMIKACIN", "VANCOMYCIN", "CEFEPIME"]


def _concepts(label, suffixes, domain="Measurement"):
    return [{"concept_name": label.title() + s, "domain_id": domain, "vocabulary_id": "LOINC"} for s in suffixes]


@pytest.fixture
def vocabulary(monkeypatch):
    """label -> list of (suffix, domain); anything absent has no concept."""
    table = {}

    def find(label, vocab_ids):
        return [{"concept_name": label.title() + s, "domain_id": d, "vocabulary_id": "LOINC"}
                for s, d in table.get(label, [])]

    monkeypatch.setattr(lvr, "find_name_extensions", find)
    return table


def _full(vocabulary, labels=ANTIBIOTICS, suffixes=(GENERIC, MIC, DISK)):
    for label in labels:
        vocabulary[label] = [(s, "Measurement") for s in suffixes]


# --- context rows ---------------------------------------------------------------

def test_context_rows_leave_out_identifiers_dates_and_the_key():
    df = pd.DataFrame({
        "row_id": range(6), "subject_id": range(6), "ab_itemid": ["1", "", "2", "3", "4", "5"],
        "charttime": ["2100-01-01"] * 6, "chartdate": ["2100-01-01"] * 6, "spec_itemid": ["9"] * 6,
        "org_name": ["E COLI"] * 6, "dilution_text": ["<=0.25", "", "4", "8", "=>16", "2"],
        "interpretation": ["S", "", "S", "R", "R", "I"],
    })
    rows = lvr.sample_context_rows(df, "ab_itemid")
    assert rows and set(rows[0]) == {"org_name", "dilution_text", "interpretation"}
    assert len(rows) == 5                           # the empty-key row is never shown
    assert all(r["dilution_text"] != "" for r in rows)


def test_context_rows_are_deterministic_and_truncated():
    df = pd.DataFrame({"k": [str(i) for i in range(50)], "text": ["x" * 200] * 50})
    first, again = lvr.sample_context_rows(df, "k"), lvr.sample_context_rows(df.copy(), "k")
    assert first == again and len(first) == 5 and len(first[0]["text"]) == 40


def test_context_rows_empty_cases():
    assert lvr.sample_context_rows(pd.DataFrame({"k": ["", " "], "v": ["a", "b"]}), "k") == []
    assert lvr.sample_context_rows(pd.DataFrame({"k": ["1"]}), "k") == []


# --- candidates found in the vocabulary -------------------------------------------

def test_qualifiers_present_for_most_labels_are_offered(vocabulary):
    _full(vocabulary)
    out = lvr.collect_suffix_candidates(ANTIBIOTICS, ["LOINC"])
    assert {c["suffix"] for c in out} == {GENERIC, MIC, DISK}
    assert all(c["coverage"] == 4 and c["domains"] == {"Measurement": 4} for c in out)


def test_a_rare_qualifier_and_a_longer_word_are_not_offered(vocabulary):
    _full(vocabulary, suffixes=(GENERIC, MIC))
    vocabulary["GENTAMICIN"].append((" [Presence] in Blood", "Measurement"))   # 1 label of 4
    vocabulary["AMIKACIN"].append(("s syndrome", "Condition"))                  # a longer word
    out = {c["suffix"] for c in lvr.collect_suffix_candidates(ANTIBIOTICS, ["LOINC"])}
    assert out == {GENERIC, MIC}


def test_nothing_consistent_gives_no_candidate(vocabulary):
    vocabulary["GENTAMICIN"] = [(MIC, "Measurement")]
    assert lvr.collect_suffix_candidates(ANTIBIOTICS, ["LOINC"]) == []


def test_unknown_vocabulary_gives_no_candidate(vocabulary):
    _full(vocabulary)
    assert lvr.collect_suffix_candidates(ANTIBIOTICS, ["NOT_A_VOCAB"]) == []


# --- the model chooses among what was found ----------------------------------------

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


ROWS = [{"org_name": "E COLI", "dilution_text": "<=0.25", "interpretation": "S"}]


def _discover(llm):
    return lvr.discover_name_templates(llm, "MICRO", "ab_itemid", ANTIBIOTICS, ["LOINC"], ROWS, "src")


def test_the_choice_becomes_ordered_templates_and_is_traceable(vocabulary, cache):
    _full(vocabulary)
    llm = _LLM(json.dumps({"suffixes": [MIC, GENERIC], "confidence": 0.8, "reason": "dilution_text holds concentrations"}))
    assert _discover(llm) == ["{label}" + MIC, "{label}" + GENERIC]
    prompt = llm.prompts[0]
    assert "Minimum inhibitory concentration" in prompt and "dilution_text" in prompt and "4/4" in prompt
    entry = cache[("src", "local_vocab_name_pattern", "MICRO", "ab_itemid")]
    assert entry["name_templates"] == ["{label}" + MIC, "{label}" + GENERIC]
    assert set(entry["offered_suffixes"]) == {GENERIC, MIC, DISK}


def test_the_model_cannot_invent_a_qualifier(vocabulary, cache):
    _full(vocabulary)
    llm = _LLM(json.dumps({"suffixes": [" [Susceptibility] by Etest", MIC, MIC]}))
    assert _discover(llm) == ["{label}" + MIC]


def test_a_second_run_uses_the_cache(vocabulary, cache):
    _full(vocabulary)
    llm = _LLM(json.dumps({"suffixes": [MIC]}))
    first = _discover(llm)
    assert _discover(llm) == first and llm.calls == 1


def test_no_fitting_qualifier_means_a_plain_lookup_and_is_remembered(vocabulary, cache):
    _full(vocabulary)
    llm = _LLM(json.dumps({"suffixes": []}))
    assert _discover(llm) is None
    assert _discover(llm) is None and llm.calls == 1


def test_nothing_to_decide_never_asks_the_model(vocabulary, cache):
    vocabulary["GENTAMICIN"] = [("", "Measurement")]          # only the label itself exists
    llm = _LLM("{}")
    assert _discover(llm) is None and llm.calls == 0


@pytest.mark.parametrize("content", ["not json", json.dumps({"suffixes": "x"})])
def test_an_unusable_answer_is_not_cached(vocabulary, cache, content):
    _full(vocabulary)
    assert _discover(_LLM(content)) is None
    assert cache == {}
