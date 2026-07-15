"""Inicialização das ferramentas padrão."""

from assistente_local.tools.applications import (
    ListApplicationsTool,
    OpenApplicationTool,
)
from assistente_local.tools.registry import ToolRegistry


def build_default_registry() -> ToolRegistry:
    """Cria o registro com as ferramentas oficiais do assistente."""

    registry = ToolRegistry()

    registry.register(ListApplicationsTool())
    registry.register(OpenApplicationTool())

    return registry
