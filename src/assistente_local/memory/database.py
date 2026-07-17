"""Configuração e gerenciamento do banco SQLite."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL DEFAULT 'general',
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    importance INTEGER NOT NULL DEFAULT 1
        CHECK (importance BETWEEN 1 AND 5),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (category, key)
);

CREATE INDEX IF NOT EXISTS idx_memories_category
ON memories (category);

CREATE INDEX IF NOT EXISTS idx_memories_updated_at
ON memories (updated_at DESC);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL
        CHECK (role IN ('system', 'user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_created_at
ON conversation_messages (created_at DESC);
"""


class MemoryDatabase:
    """Gerencia conexões com o banco de memória."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Fornece uma conexão SQLite com commit e rollback automáticos."""

        connection = sqlite3.connect(
            self.path,
            timeout=10,
        )

        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        """Cria as tabelas necessárias caso ainda não existam."""

        with self.connection() as connection:
            connection.executescript(DATABASE_SCHEMA)
