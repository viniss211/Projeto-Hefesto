"""Ferramentas para armazenamento e consulta de memórias."""

from dataclasses import asdict
from typing import Any

from assistente_local.memory import MemoryStore
from assistente_local.tools.base import BaseTool, ToolResult


class RememberInformationTool(BaseTool):
    """Salva uma informação na memória persistente."""

    name = "remember_information"
    description = (
        "Salva uma informação importante, preferência ou fato na memória persistente do assistente."
    )
    requires_approval = False

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": (
                    "Identificador curto da informação, como editor_preferido ou nome_usuario."
                ),
            },
            "value": {
                "type": "string",
                "description": "Informação que deve ser lembrada.",
            },
            "category": {
                "type": "string",
                "description": (
                    "Categoria da memória, como preferencias, perfil, trabalho ou projetos."
                ),
                "default": "general",
            },
            "importance": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "default": 1,
                "description": "Importância da memória entre 1 e 5.",
            },
        },
        "required": [
            "key",
            "value",
        ],
        "additionalProperties": False,
    }

    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Salva a memória recebida."""

        key = arguments.get("key")
        value = arguments.get("value")
        category = arguments.get("category", "general")
        importance = arguments.get("importance", 1)

        if not isinstance(key, str):
            return ToolResult(
                success=False,
                message="O parâmetro 'key' deve ser um texto.",
            )

        if not isinstance(value, str):
            return ToolResult(
                success=False,
                message="O parâmetro 'value' deve ser um texto.",
            )

        if not isinstance(category, str):
            return ToolResult(
                success=False,
                message="O parâmetro 'category' deve ser um texto.",
            )

        try:
            memory = self.store.remember(
                key=key,
                value=value,
                category=category,
                importance=importance,
            )
        except ValueError as error:
            return ToolResult(
                success=False,
                message=str(error),
            )

        return ToolResult(
            success=True,
            message=f"Informação lembrada: {memory.key}.",
            data={"memory": asdict(memory)},
        )


class RecallInformationTool(BaseTool):
    """Pesquisa informações armazenadas."""

    name = "recall_information"
    description = "Pesquisa fatos e preferências armazenados na memória persistente do assistente."
    requires_approval = False

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Texto que deve ser procurado nas memórias.",
            },
            "category": {
                "type": "string",
                "description": "Categoria opcional da memória.",
            },
            "key": {
                "type": "string",
                "description": "Chave exata opcional da memória.",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 10,
            },
        },
        "required": [],
        "additionalProperties": False,
    }

    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Consulta a memória persistente."""

        query = arguments.get("query")
        category = arguments.get("category")
        key = arguments.get("key")
        limit = arguments.get("limit", 10)

        if query is not None and not isinstance(query, str):
            return ToolResult(
                success=False,
                message="O parâmetro 'query' deve ser um texto.",
            )

        if category is not None and not isinstance(category, str):
            return ToolResult(
                success=False,
                message="O parâmetro 'category' deve ser um texto.",
            )

        if key is not None and not isinstance(key, str):
            return ToolResult(
                success=False,
                message="O parâmetro 'key' deve ser um texto.",
            )

        try:
            memories = self.store.recall(
                query=query,
                category=category,
                key=key,
                limit=limit,
            )
        except ValueError as error:
            return ToolResult(
                success=False,
                message=str(error),
            )

        return ToolResult(
            success=True,
            message=f"{len(memories)} memória(s) encontrada(s).",
            data={"memories": [asdict(memory) for memory in memories]},
        )
