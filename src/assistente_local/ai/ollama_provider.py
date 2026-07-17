"""Implementação do provedor local Ollama."""

from typing import Any

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    NotFoundError,
    OpenAI,
)

from assistente_local.ai.base import (
    AIProviderUnavailableError,
)
from assistente_local.config import Settings

TRANSIENT_ERRORS = (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    NotFoundError,
)


class OllamaProvider:
    """Conecta o Hefesto ao Ollama local."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        self.client = OpenAI(
            base_url=f"{settings.ollama_base_url}/",
            api_key="ollama",
            timeout=settings.ai_timeout_seconds,
            max_retries=1,
        )

    def create_response(
        self,
        *,
        input_items: list[Any],
        tools: list[dict[str, Any]],
        instructions: str,
    ) -> Any:
        """Solicita uma resposta ao modelo local."""

        try:
            return self.client.responses.create(
                model=self.settings.ollama_model,
                instructions=instructions,
                input=input_items,
                tools=tools,
            )
        except TRANSIENT_ERRORS as error:
            raise AIProviderUnavailableError(
                provider="ollama",
                message=str(error),
            ) from error