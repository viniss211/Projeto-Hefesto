"""Estruturas fundamentais do sistema de ferramentas."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Resultado padronizado retornado por uma ferramenta."""

    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """Contrato que todas as ferramentas devem seguir."""

    name: str
    description: str
    parameters: dict[str, Any]
    requires_approval: bool = False

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Executa a ferramenta."""

    def as_schema(self) -> dict[str, Any]:
        """Retorna o schema compatível com function calling."""

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
