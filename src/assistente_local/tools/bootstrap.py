"""Inicialização das ferramentas padrão."""

from assistente_local.memory import (
    MemoryStore,
    create_default_memory_store,
)
from assistente_local.tools.applications import (
    ListApplicationsTool,
    OpenApplicationTool,
)
from assistente_local.tools.memory import (
    RecallInformationTool,
    RememberInformationTool,
)
from assistente_local.tools.registry import ToolRegistry


def build_default_registry(
    memory_store: MemoryStore | None = None,
) -> ToolRegistry:
    """Cria o registro com as ferramentas oficiais."""

    if memory_store is None:
        memory_store = create_default_memory_store()

    registry = ToolRegistry()

    registry.register(ListApplicationsTool())
    registry.register(OpenApplicationTool())
    registry.register(RememberInformationTool(memory_store))
    registry.register(RecallInformationTool(memory_store))

    return registry
