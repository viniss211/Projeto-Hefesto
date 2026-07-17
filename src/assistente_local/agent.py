"""Orquestrador principal do Assistente Local."""

import json
from dataclasses import dataclass, field
from typing import Any
import logging
from assistente_local.observability import (
    redact_sensitive_values,
)
from collections.abc import Callable
from assistente_local.ai import AIProvider
from assistente_local.memory import MemoryStore
from assistente_local.tools import ToolRegistry, ToolResult

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger(
    "assistente_local.audit"
)

ApprovalHandler = Callable[
    [str, dict[str, Any]],
    bool,
]

SYSTEM_INSTRUCTIONS = """
Você é um assistente pessoal executado no computador do usuário.

Responda sempre em português do Brasil, de forma natural, clara e objetiva.

Você possui ferramentas locais. Use essas ferramentas quando forem necessárias
para cumprir uma solicitação.

Regras:
1. Nunca afirme que executou uma ação antes de receber o resultado da ferramenta.
2. Não invente resultados de ferramentas.
3. Se uma ferramenta retornar erro, explique o erro de forma simples.
4. Use remember_information quando o usuário pedir explicitamente para lembrar
   algo ou informar uma preferência duradoura relevante.
5. Use recall_information quando precisar consultar fatos e preferências
   armazenados.
6. Use open_application somente quando o usuário realmente pedir para abrir
   um programa.
7. Não tente executar comandos, programas ou ações que não estejam disponíveis
   nas ferramentas fornecidas.
8. Nunca solicite ou exponha chaves de API, senhas ou outros segredos.
""".strip()


@dataclass(frozen=True, slots=True)
class ToolExecution:
    """Registro de uma ferramenta executada durante a resposta."""

    name: str
    arguments: dict[str, Any]
    result: ToolResult


@dataclass(frozen=True, slots=True)
class AgentResult:
    """Resultado final de uma interação com o agente."""

    text: str
    tool_executions: list[ToolExecution] = field(default_factory=list)


class AssistantAgent:
    """Coordena o modelo, a memória e as ferramentas."""
    def __init__(
        self,
        *,
        provider: AIProvider,
        registry: ToolRegistry,
        memory_store: MemoryStore,
        max_tool_rounds: int = 8,
        approval_handler: ApprovalHandler | None = None,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.memory_store = memory_store
        self.max_tool_rounds = max_tool_rounds
        self.approval_handler = approval_handler
    def run(self, user_message: str) -> AgentResult:
        """Processa uma mensagem do usuário."""

        clean_message = user_message.strip()

        if not clean_message:
            raise ValueError("A mensagem não pode ficar vazia.")

        self.memory_store.add_message(
            role="user",
            content=clean_message,
        )

        input_items = self._build_conversation_input()
        tools = self.registry.list_schemas()
        executions: list[ToolExecution] = []

        for _ in range(self.max_tool_rounds):
            response = self.provider.create_response(
                input_items=input_items,
                tools=tools,
                instructions=SYSTEM_INSTRUCTIONS,
            )

            function_calls = [item for item in response.output if item.type == "function_call"]

            if not function_calls:
                final_text = response.output_text.strip()

                if not final_text:
                    final_text = "Não consegui produzir uma resposta em texto."

                self.memory_store.add_message(
                    role="assistant",
                    content=final_text,
                )

                return AgentResult(
                    text=final_text,
                    tool_executions=executions,
                )

            # Preserva todos os itens produzidos pelo modelo,
            # incluindo possíveis itens internos necessários no próximo turno.
            input_items.extend(response.output)

            for function_call in function_calls:
                arguments = self._parse_arguments(function_call.arguments)

                tool = self.registry.get(
                    function_call.name
                )

                approved = False

                if tool is not None and tool.requires_approval:
                    if self.approval_handler is not None:
                        approved = self.approval_handler(
                            function_call.name,
                            arguments,
                        )

                result = self.registry.execute(
                    function_call.name,
                    arguments,
                    approved=approved,
                )

                safe_arguments = redact_sensitive_values(
                    arguments
                )

                audit_logger.info(
                    "tool=%s requires_approval=%s "
                    "approved=%s success=%s arguments=%s",
                    function_call.name,
                    (
                        tool.requires_approval
                        if tool is not None
                        else False
                    ),
                    approved,
                    result.success,
                    json.dumps(
                        safe_arguments,
                        ensure_ascii=False,
                    ),
                )

                executions.append(
                    ToolExecution(
                        name=function_call.name,
                        arguments=arguments,
                        result=result,
                    )
                )

                input_items.append(
                    {
                        "type": "function_call_output",
                        "call_id": function_call.call_id,
                        "output": self._serialize_tool_result(result),
                    }
                )

        final_text = "A tarefa foi interrompida porque excedeu o limite de etapas permitido."

        self.memory_store.add_message(
            role="assistant",
            content=final_text,
        )

        return AgentResult(
            text=final_text,
            tool_executions=executions,
        )

    def _build_conversation_input(self) -> list[dict[str, str]]:
        """Converte o histórico salvo para o formato do modelo."""

        messages = self.memory_store.recent_messages(limit=20)

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
            if message.role in {"user", "assistant"}
        ]

    @staticmethod
    def _parse_arguments(
        raw_arguments: str,
    ) -> dict[str, Any]:
        """Converte os argumentos JSON enviados pelo modelo."""

        try:
            parsed = json.loads(raw_arguments)
        except json.JSONDecodeError:
            return {}

        if not isinstance(parsed, dict):
            return {}

        return parsed

    @staticmethod
    def _serialize_tool_result(
        result: ToolResult,
    ) -> str:
        """Converte o resultado da ferramenta para JSON."""

        return json.dumps(
            {
                "success": result.success,
                "message": result.message,
                "data": result.data,
            },
            ensure_ascii=False,
        )
