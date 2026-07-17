"""Implementação do provedor GroqCloud."""

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


class GroqProvider:
    """Conecta o Hefesto à Responses API da Groq."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        self.client = OpenAI(
            base_url=f"{settings.groq_base_url}/",
            api_key=settings.groq_api_key,
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
        """Solicita uma resposta ao modelo da Groq."""

        try:
            return self.client.responses.create(
                model=self.settings.groq_model,
                instructions=instructions,
                input=input_items,
                tools=tools,
                tool_choice="auto",
            )
        except TRANSIENT_ERRORS as error:
            raise AIProviderUnavailableError(
                provider="groq",
                message=str(error),
            ) from error