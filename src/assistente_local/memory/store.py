"""Operações de leitura e gravação da memória persistente."""

import unicodedata
from dataclasses import dataclass

from assistente_local.memory.database import MemoryDatabase

VALID_MESSAGE_ROLES = {
    "system",
    "user",
    "assistant",
    "tool",
}


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    """Representa uma memória armazenada."""

    id: int
    category: str
    key: str
    value: str
    importance: int
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    """Representa uma mensagem do histórico."""

    id: int
    role: str
    content: str
    created_at: str


def normalize_identifier(value: str) -> str:
    """Normaliza uma chave ou categoria de memória."""

    normalized = unicodedata.normalize("NFKD", value)

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return "_".join(without_accents.lower().strip().split())


class MemoryStore:
    """Interface de alto nível para a memória do assistente."""

    def __init__(self, database: MemoryDatabase) -> None:
        self.database = database
        self.database.initialize()

    def remember(
        self,
        *,
        key: str,
        value: str,
        category: str = "general",
        importance: int = 1,
    ) -> MemoryEntry:
        """Salva uma memória ou atualiza uma já existente."""

        normalized_key = normalize_identifier(key)
        normalized_category = normalize_identifier(category)
        clean_value = value.strip()

        if not normalized_key:
            raise ValueError("A chave da memória não pode ficar vazia.")

        if not normalized_category:
            raise ValueError("A categoria da memória não pode ficar vazia.")

        if not clean_value:
            raise ValueError("O conteúdo da memória não pode ficar vazio.")

        if not isinstance(importance, int) or not 1 <= importance <= 5:
            raise ValueError("A importância deve ser um número entre 1 e 5.")

        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO memories (
                    category,
                    key,
                    value,
                    importance
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(category, key)
                DO UPDATE SET
                    value = excluded.value,
                    importance = excluded.importance,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    normalized_category,
                    normalized_key,
                    clean_value,
                    importance,
                ),
            )

            row = connection.execute(
                """
                SELECT
                    id,
                    category,
                    key,
                    value,
                    importance,
                    created_at,
                    updated_at
                FROM memories
                WHERE category = ? AND key = ?
                """,
                (
                    normalized_category,
                    normalized_key,
                ),
            ).fetchone()

        if row is None:
            raise RuntimeError("Não foi possível recuperar a memória salva.")

        return self._row_to_memory(row)

    def recall(
        self,
        *,
        query: str | None = None,
        category: str | None = None,
        key: str | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Pesquisa memórias por texto, categoria ou chave."""

        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("O limite deve ser um número entre 1 e 100.")

        conditions: list[str] = []
        values: list[object] = []

        if category:
            conditions.append("category = ?")
            values.append(normalize_identifier(category))

        if key:
            conditions.append("key = ?")
            values.append(normalize_identifier(key))

        if query:
            conditions.append("(key LIKE ? OR value LIKE ?)")
            pattern = f"%{query.strip()}%"
            values.extend([pattern, pattern])

        where_clause = ""

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        values.append(limit)

        with self.database.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT
                    id,
                    category,
                    key,
                    value,
                    importance,
                    created_at,
                    updated_at
                FROM memories
                {where_clause}
                ORDER BY importance DESC, updated_at DESC
                LIMIT ?
                """,
                values,
            ).fetchall()

        return [self._row_to_memory(row) for row in rows]

    def add_message(
        self,
        *,
        role: str,
        content: str,
    ) -> ConversationMessage:
        """Adiciona uma mensagem ao histórico da conversa."""

        normalized_role = role.lower().strip()
        clean_content = content.strip()

        if normalized_role not in VALID_MESSAGE_ROLES:
            raise ValueError(f"Tipo de mensagem inválido: {role}.")

        if not clean_content:
            raise ValueError("A mensagem não pode ficar vazia.")

        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO conversation_messages (
                    role,
                    content
                )
                VALUES (?, ?)
                """,
                (
                    normalized_role,
                    clean_content,
                ),
            )

            message_id = cursor.lastrowid

            row = connection.execute(
                """
                SELECT
                    id,
                    role,
                    content,
                    created_at
                FROM conversation_messages
                WHERE id = ?
                """,
                (message_id,),
            ).fetchone()

        if row is None:
            raise RuntimeError("Não foi possível recuperar a mensagem salva.")

        return ConversationMessage(
            id=row["id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
        )

    def recent_messages(
        self,
        *,
        limit: int = 20,
    ) -> list[ConversationMessage]:
        """Retorna as mensagens mais recentes em ordem cronológica."""

        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("O limite deve ser um número entre 1 e 100.")

        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    role,
                    content,
                    created_at
                FROM conversation_messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        messages = [
            ConversationMessage(
                id=row["id"],
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

        messages.reverse()

        return messages

    @staticmethod
    def _row_to_memory(row: object) -> MemoryEntry:
        """Converte uma linha SQLite em uma memória."""

        return MemoryEntry(
            id=row["id"],
            category=row["category"],
            key=row["key"],
            value=row["value"],
            importance=row["importance"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )