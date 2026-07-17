"""Carregamento das configurações do Hefesto."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

SUPPORTED_AI_PROVIDERS = {
    "groq",
    "ollama",
    "openai",
}


@dataclass(frozen=True, slots=True)
class Settings:
    """Configurações usadas pelo assistente."""

    ai_provider_chain: tuple[str, ...]
    ai_timeout_seconds: float
    max_tool_rounds: int
    log_level: str

    groq_api_key: str = field(repr=False)
    groq_base_url: str
    groq_model: str

    ollama_base_url: str
    ollama_model: str

    openai_api_key: str = field(repr=False)
    openai_model: str


def parse_provider_chain(raw_value: str) -> tuple[str, ...]:
    """Converte a lista textual de provedores em uma tupla validada."""

    providers = tuple(
        provider.strip().lower()
        for provider in raw_value.split(",")
        if provider.strip()
    )

    if not providers:
        raise ValueError(
            "AI_PROVIDER_CHAIN precisa conter pelo menos um provedor."
        )

    unsupported = [
        provider
        for provider in providers
        if provider not in SUPPORTED_AI_PROVIDERS
    ]

    if unsupported:
        available = ", ".join(
            sorted(SUPPORTED_AI_PROVIDERS)
        )

        raise ValueError(
            f"Provedor não suportado: {unsupported[0]}. "
            f"Disponíveis: {available}."
        )

    # Remove duplicados preservando a ordem.
    return tuple(dict.fromkeys(providers))


def load_settings() -> Settings:
    """Carrega e valida as configurações do arquivo .env."""

    load_dotenv()

    provider_chain_raw = os.getenv(
        "AI_PROVIDER_CHAIN",
        os.getenv("AI_PROVIDER", "groq,ollama"),
    )

    provider_chain = parse_provider_chain(
        provider_chain_raw
    )

    try:
        timeout = float(
            os.getenv(
                "AI_TIMEOUT_SECONDS",
                "120",
            )
        )
    except ValueError as error:
        raise ValueError(
            "AI_TIMEOUT_SECONDS deve ser um número."
        ) from error

    try:
        max_tool_rounds = int(
            os.getenv(
                "MAX_TOOL_ROUNDS",
                "8",
            )
        )
    except ValueError as error:
        raise ValueError(
            "MAX_TOOL_ROUNDS deve ser um número inteiro."
        ) from error

    if timeout <= 0:
        raise ValueError(
            "AI_TIMEOUT_SECONDS deve ser maior que zero."
        )

    if not 1 <= max_tool_rounds <= 20:
        raise ValueError(
            "MAX_TOOL_ROUNDS deve ficar entre 1 e 20."
        )

    log_level = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).strip().upper()

    groq_api_key = os.getenv(
        "GROQ_API_KEY",
        "",
    ).strip()

    groq_base_url = os.getenv(
        "GROQ_BASE_URL",
        "https://api.groq.com/openai/v1",
    ).strip().rstrip("/")

    groq_model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b",
    ).strip()

    ollama_base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434/v1",
    ).strip().rstrip("/")

    ollama_model = os.getenv(
        "OLLAMA_MODEL",
        "qwen2.5:3b",
    ).strip()

    openai_api_key = os.getenv(
        "OPENAI_API_KEY",
        "",
    ).strip()

    openai_model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    ).strip()

    if "groq" in provider_chain and not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY não foi configurada."
        )

    if "openai" in provider_chain and not openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY não foi configurada."
        )

    if not groq_base_url:
        raise ValueError(
            "GROQ_BASE_URL não pode ficar vazia."
        )

    if not groq_model:
        raise ValueError(
            "GROQ_MODEL não pode ficar vazio."
        )

    if not ollama_base_url:
        raise ValueError(
            "OLLAMA_BASE_URL não pode ficar vazia."
        )

    if not ollama_model:
        raise ValueError(
            "OLLAMA_MODEL não pode ficar vazio."
        )

    return Settings(
        ai_provider_chain=provider_chain,
        ai_timeout_seconds=timeout,
        max_tool_rounds=max_tool_rounds,
        log_level=log_level,
        groq_api_key=groq_api_key,
        groq_base_url=groq_base_url,
        groq_model=groq_model,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
    )