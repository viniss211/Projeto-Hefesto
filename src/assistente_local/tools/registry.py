"""Registro e execução controlada das ferramentas."""

import re
from typing import Any

from assistente_local.tools.base import BaseTool, ToolResult

TOOL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class ToolRegistry:
    """Mantém as ferramentas disponíveis para o assistente."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registra uma ferramenta no sistema."""

        if not TOOL_NAME_PATTERN.fullmatch(tool.name):
            raise ValueError(
                f"Nome de ferramenta inválido: {tool.name!r}. "
                "Use apenas letras minúsculas, números e underline."
            )

        if tool.name in self._tools:
            raise ValueError(f"A ferramenta {tool.name!r} já está registrada.")

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        """Obtém uma ferramenta pelo nome."""

        return self._tools.get(name)

    def count(self) -> int:
        """Retorna a quantidade de ferramentas registradas."""

        return len(self._tools)

    def list_names(self) -> list[str]:
        """Retorna os nomes das ferramentas em ordem alfabética."""

        return sorted(self._tools)

    def list_schemas(self) -> list[dict[str, Any]]:
        """Retorna os schemas que serão enviados ao modelo de IA."""

        return [self._tools[name].as_schema() for name in self.list_names()]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        *,
        approved: bool = False,
    ) -> ToolResult:
        """Executa uma ferramenta registrada."""

        tool = self.get(name)

        if tool is None:
            return ToolResult(
                success=False,
                message=f"Ferramenta desconhecida: {name}.",
                data={"available_tools": self.list_names()},
            )

        if tool.requires_approval and not approved:
            return ToolResult(
                success=False,
                message=f"A ferramenta {name} precisa de aprovação.",
                data={
                    "approval_required": True,
                    "tool": name,
                    "arguments": arguments or {},
                },
            )

        try:
            return tool.execute(arguments or {})
        except Exception as exc:
            return ToolResult(
                success=False,
                message=f"Erro ao executar a ferramenta {name}: {exc}",
                data={"exception_type": type(exc).__name__},
            )
