"""
Model configuration.

The developer chooses the LLM provider/model here (or via .env).
Agents never select their own model - they receive an already-built
LLM instance from the Model Factory (see factory.py).
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    temperature: float = 0.0
    # OpenRouter only. None = leave the model's default behaviour alone.
    reasoning_effort: str | None = None


# Values accepted by OpenRouter's `reasoning.effort`. "none" disables
# reasoning entirely (not every model allows it - some reject it).
VALID_REASONING_EFFORTS = ("xhigh", "high", "medium", "low", "minimal", "none")


def _read_reasoning_effort() -> str | None:
    raw = os.getenv("LLM_REASONING_EFFORT", "").strip().lower()
    if not raw:
        return None
    if raw not in VALID_REASONING_EFFORTS:
        raise ValueError(
            f"LLM_REASONING_EFFORT={raw!r} is not one of {VALID_REASONING_EFFORTS}"
        )
    return raw


def get_llm_config() -> LLMConfig:
    return LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "groq").lower(),
        model=os.getenv("LLM_MODEL", "openai/gpt-oss-20b"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
        reasoning_effort=_read_reasoning_effort(),
    )
