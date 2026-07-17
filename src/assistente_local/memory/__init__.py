"""Memória persistente do assistente."""

from pathlib import Path

from assistente_local.memory.database import MemoryDatabase
from assistente_local.memory.store import (
    ConversationMessage,
    MemoryEntry,
    MemoryStore,
)


def create_default_memory_store(
    path: str | Path = Path("data") / "assistant.db",
) -> MemoryStore:
    """Cria a memória usando o banco padrão da aplicação."""

    database = MemoryDatabase(path)
    return MemoryStore(database)


__all__ = [
    "ConversationMessage",
    "MemoryDatabase",
    "MemoryEntry",
    "MemoryStore",
    "create_default_memory_store",
]
