"""Contratos e exceções dos provedores de IA."""

from typing import Any, Protocol


class AIProviderUnavailableError(RuntimeError):
    """Indica indisponibilidade temporária de um provedor."""

    def __init__(
        self,
        *,
        provider: str,
        message: str,
    ) -> None:
        self.provider = provider
        self.detail = message

        super().__init__(
            f"Provedor {provider} indisponível: {message}"
        )


class AIProvider(Protocol):
    """Contrato que todo provedor de IA deve implementar."""

    def create_response(
        self,
        *,
        input_items: list[Any],
        tools: list[dict[str, Any]],
        instructions: str,
    ) -> Any:
        """Envia uma solicitação ao modelo."""