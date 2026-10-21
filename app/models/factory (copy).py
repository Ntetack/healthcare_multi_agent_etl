"""
Model Factory.

Deliberately minimal for the first implementation: no base.py, no
providers/ package. Groq, Mistral, and OpenRouter are handled directly
here. Introduce an abstraction layer only if/when a further provider
makes it necessary (see architecture decision doc, v6 section 16).
"""
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_openrouter import ChatOpenRouter

from app.models.config import LLMConfig, get_llm_config


def get_llm(config: LLMConfig | None = None):
    """Builds and returns a chat model instance for the configured provider.

    Agents call this once (typically via the Coordinator / graph wiring)
    and receive a ready-to-use LangChain chat model. They must not import
    ChatGroq / ChatMistralAI / ChatOpenRouter directly.
    """
    config = config or get_llm_config()

    if config.provider == "groq":
        return ChatGroq(model=config.model, temperature=config.temperature)

    if config.provider == "mistral":
        return ChatMistralAI(model=config.model, temperature=config.temperature)

    if config.provider == "openrouter":
        # OpenRouter model strings are "provider/model", e.g.
        # "anthropic/claude-sonnet-4.6" or "openai/gpt-oss-20b" - the
        # same LLM_MODEL value works whether reached directly via Groq
        # or routed through OpenRouter, as long as OpenRouter carries it.
        return ChatOpenRouter(model=config.model, temperature=config.temperature)

    raise ValueError(f"Unsupported provider: {config.provider}")
