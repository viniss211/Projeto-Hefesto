"""Implementação do provedor OpenAI."""

from typing import Any

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)

from assistente_local.ai.base import (
    AIProviderUnavailableError,
)
from assistente_local.config import Settings

TRANSIENT_ERRORS = (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
    NotFoundError,
)


class OpenAIProvider:
    """Conecta o assistente à Responses API da OpenAI."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        self.client = OpenAI(
            api_key=settings.openai_api_key,
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
        """Solicita uma resposta ao modelo configurado."""

        try:
            return self.client.responses.create(
                model=self.settings.openai_model,
                instructions=instructions,
                input=input_items,
                tools=tools,
                tool_choice="auto",
            )
        except TRANSIENT_ERRORS as error:
            raise AIProviderUnavailableError(
                provider="openai",
                message=str(error),
            ) from error