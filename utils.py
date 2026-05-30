"""LangChain LLM wrapper for the Red Room AI Stress Tester.

Exposes:
    AVAILABLE_PROVIDERS  - providers supported by the sandbox
    DEFAULT_MODELS       - default model per provider
    get_llm(provider, model) - build a configured LangChain chat model
    call_llm(llm, system_prompt, user_input) - invoke and return response text
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

AVAILABLE_PROVIDERS = ("openai", "anthropic", "xai")

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "xai": "grok-2-latest",
}

_API_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "xai": "XAI_API_KEY",
}


def get_llm(provider: str, model: str | None = None):
    """Return a LangChain chat model for `provider`.

    Raises ValueError if the provider is unknown or its API key is missing.
    """
    provider = provider.lower()
    if provider not in AVAILABLE_PROVIDERS:
        raise ValueError(
            f"Unknown provider {provider!r}. Choose one of {AVAILABLE_PROVIDERS}."
        )

    key_name = _API_KEY_ENV[provider]
    if not os.getenv(key_name):
        raise ValueError(
            f"{key_name} is missing from .env - add it to use {provider}."
        )

    model = model or DEFAULT_MODELS[provider]

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model)
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model)
    if provider == "xai":
        from langchain_xai import ChatXAI
        return ChatXAI(model=model)


def call_llm(llm, system_prompt: str, user_input: str) -> str:
    """Invoke `llm` with a system prompt and user input. Returns the text response."""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input),
    ]
    response = llm.invoke(messages)
    return response.content
