"""LLM_REASONING_EFFORT is optional and only reaches OpenRouter."""
from unittest.mock import patch

import pytest

from app.models import factory
from app.models.config import LLMConfig, get_llm_config


def test_unset_means_no_reasoning_argument(monkeypatch):
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)
    assert get_llm_config().reasoning_effort is None
    with patch.object(factory, "ChatOpenRouter") as chat:
        factory.get_llm(LLMConfig(provider="openrouter", model="x/y"))
    assert "reasoning" not in chat.call_args.kwargs


def test_env_value_is_read_and_normalised(monkeypatch):
    monkeypatch.setenv("LLM_REASONING_EFFORT", " None ")
    assert get_llm_config().reasoning_effort == "none"


def test_effort_is_passed_to_openrouter():
    cfg = LLMConfig(provider="openrouter", model="x/y", reasoning_effort="none")
    with patch.object(factory, "ChatOpenRouter") as chat:
        factory.get_llm(cfg)
    assert chat.call_args.kwargs["reasoning"] == {"effort": "none"}


def test_invalid_value_is_rejected(monkeypatch):
    monkeypatch.setenv("LLM_REASONING_EFFORT", "turbo")
    with pytest.raises(ValueError):
        get_llm_config()


def test_other_providers_ignore_it():
    cfg = LLMConfig(provider="groq", model="m", reasoning_effort="none")
    with patch.object(factory, "ChatGroq") as chat:
        factory.get_llm(cfg)
    assert "reasoning" not in chat.call_args.kwargs
