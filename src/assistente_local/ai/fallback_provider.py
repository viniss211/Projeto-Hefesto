"""Fallback automático entre provedores de IA."""

import logging
from dataclasses import dataclass
from typing import Any

from assistente_local.ai.base import (
    AIProvider,
    AIProviderUnavailableError,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ProviderEntry:
    """Associa um nome a uma implementação de provedor."""

    name: str
    provider: AIProvider


class FallbackProvider:
    """Tenta os provedores disponíveis na ordem configurada."""

    def __init__(
        self,
        providers: list[ProviderEntry],
    ) -> None:
        if not providers:
            raise ValueError(
                "É necessário configurar pelo menos um provedor."
            )

        self.providers = providers
        self.last_provider_name: str | None = None

    def create_response(
        self,
        *,
        input_items: list[Any],
        tools: list[dict[str, Any]],
        instructions: str,
    ) -> Any:
        """Tenta cada provedor até obter uma resposta."""

        errors: list[str] = []

        for entry in self.providers:
            try:
                logger.info(
                    "Tentando provedor de IA: %s",
                    entry.name,
                )

                response = entry.provider.create_response(
                    input_items=input_items,
                    tools=tools,
                    instructions=instructions,
                )

                self.last_provider_name = entry.name

                logger.info(
                    "Resposta obtida pelo provedor: %s",
                    entry.name,
                )

                return response

            except AIProviderUnavailableError as error:
                logger.warning(
                    "Provedor %s indisponível. "
                    "Tentando próximo provedor.",
                    entry.name,
                )

                errors.append(str(error))

        detail = " | ".join(errors)

        raise AIProviderUnavailableError(
            provider="fallback",
            message=(
                "Nenhum provedor respondeu. "
                f"Detalhes: {detail}"
            ),
        )