"""Ponto de entrada do Assistente Local."""

import argparse
import json
from typing import Any

from assistente_local import __version__
from assistente_local.agent import AssistantAgent
from assistente_local.ai import (
    AIProvider,
    FallbackProvider,
    GroqProvider,
    OllamaProvider,
    OpenAIProvider,
    ProviderEntry,
)
from assistente_local.config import Settings, load_settings
from assistente_local.observability import setup_logging
from assistente_local.memory import (
    MemoryStore,
    create_default_memory_store,
)
from assistente_local.tools import (
    ToolRegistry,
    build_default_registry,
)

APP_NAME = "Assistente Local"


def get_system_status(
    registry: ToolRegistry | None = None,
) -> dict[str, Any]:
    """Retorna informações sobre o sistema."""

    tools_loaded = registry.count() if registry is not None else 0

    return {
        "name": APP_NAME,
        "version": __version__,
        "status": "online",
        "tools_loaded": tools_loaded,
    }


def build_parser() -> argparse.ArgumentParser:
    """Cria os argumentos da linha de comando."""

    parser = argparse.ArgumentParser(
        prog="assistente",
        description="Assistente de IA local.",
    )

    parser.add_argument(
        "--listar-ferramentas",
        action="store_true",
        help="Lista as ferramentas registradas.",
    )

    parser.add_argument(
        "--listar-programas",
        action="store_true",
        help="Lista os programas permitidos.",
    )

    parser.add_argument(
        "--abrir",
        metavar="PROGRAMA",
        help="Abre diretamente um programa permitido.",
    )

    parser.add_argument(
        "--lembrar",
        nargs=2,
        metavar=("CHAVE", "VALOR"),
        help="Salva diretamente uma informação.",
    )

    parser.add_argument(
        "--recordar",
        metavar="CONSULTA",
        help="Pesquisa diretamente uma memória.",
    )

    parser.add_argument(
        "--categoria",
        default="general",
        help="Categoria da memória.",
    )

    parser.add_argument(
        "--importancia",
        type=int,
        choices=range(1, 6),
        default=1,
        help="Importância da memória entre 1 e 5.",
    )

    parser.add_argument(
        "--perguntar",
        metavar="MENSAGEM",
        help="Envia uma mensagem natural para a IA.",
    )

    parser.add_argument(
        "--chat",
        action="store_true",
        help="Inicia uma conversa contínua com a IA.",
    )

    return parser


def print_result(
    result_message: str,
    result_data: dict[str, Any],
) -> None:
    """Exibe o resultado de uma ferramenta."""

    print(result_message)

    if result_data:
        print(
            json.dumps(
                result_data,
                ensure_ascii=False,
                indent=2,
            )
        )

def build_ai_provider(
    settings: Settings,
) -> AIProvider:
    """Cria a cadeia de provedores configurada."""

    providers: list[ProviderEntry] = []

    for provider_name in settings.ai_provider_chain:
        if provider_name == "groq":
            provider = GroqProvider(settings)

        elif provider_name == "ollama":
            provider = OllamaProvider(settings)

        elif provider_name == "openai":
            provider = OpenAIProvider(settings)

        else:
            raise ValueError(
                f"Provedor não suportado: {provider_name}."
            )

        providers.append(
            ProviderEntry(
                name=provider_name,
                provider=provider,
            )
        )

    return FallbackProvider(providers)

def terminal_approval_handler(
    tool_name: str,
    arguments: dict[str, Any],
) -> bool:
    """Solicita autorização para uma ação sensível."""

    print("\n" + "=" * 50)
    print("AÇÃO SENSÍVEL SOLICITADA")
    print(f"Ferramenta: {tool_name}")
    print(
        json.dumps(
            arguments,
            ensure_ascii=False,
            indent=2,
        )
    )
    print("=" * 50)

    answer = input(
        "Autorizar execução? [s/N]: "
    ).strip().lower()

    return answer in {
        "s",
        "sim",
        "y",
        "yes",
    }

def build_agent(
    memory_store: MemoryStore,
    registry: ToolRegistry,
) -> AssistantAgent:
    """Cria o agente com fallback automático."""

    settings = load_settings()
    provider = build_ai_provider(settings)

    return AssistantAgent(
        provider=provider,
        registry=registry,
        memory_store=memory_store,
        max_tool_rounds=settings.max_tool_rounds,
        approval_handler=terminal_approval_handler,
    )


def print_agent_result(result: Any) -> None:
    """Exibe a resposta e as ferramentas utilizadas."""

    for execution in result.tool_executions:
        status = "OK" if execution.result.success else "ERRO"

        print(f"[FERRAMENTA: {execution.name} | {status}]")

    print(f"\nAssistente: {result.text}")


def run_chat(agent: AssistantAgent) -> None:
    """Inicia a conversa contínua pelo terminal."""

    print("=" * 50)
    print(f"{APP_NAME} v{__version__}")
    print("Digite 'sair' para encerrar.")
    print("=" * 50)

    while True:
        try:
            user_message = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nConversa encerrada.")
            return

        if user_message.lower() in {
            "sair",
            "exit",
            "encerrar",
        }:
            print("Conversa encerrada.")
            return

        if not user_message:
            continue

        try:
            result = agent.run(user_message)
        except Exception as error:
            print(f"\nNão foi possível processar a mensagem: {error}")
            continue

        print_agent_result(result)


def main() -> None:
    """Inicializa o Assistente Local."""

    setup_logging()

    parser = build_parser()
    args = parser.parse_args()

    memory_store = create_default_memory_store()
    registry = build_default_registry(memory_store)

    if args.listar_ferramentas:
        print(
            json.dumps(
                registry.list_schemas(),
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.listar_programas:
        result = registry.execute("list_applications")
        print_result(result.message, result.data)
        return

    if args.abrir:
        result = registry.execute(
            "open_application",
            {"application": args.abrir},
        )
        print_result(result.message, result.data)
        return

    if args.lembrar:
        key, value = args.lembrar

        result = registry.execute(
            "remember_information",
            {
                "key": key,
                "value": value,
                "category": args.categoria,
                "importance": args.importancia,
            },
        )

        print_result(result.message, result.data)
        return

    if args.recordar:
        result = registry.execute(
            "recall_information",
            {
                "query": args.recordar,
                "category": args.categoria,
            },
        )

        print_result(result.message, result.data)
        return

    if args.perguntar:
        agent = build_agent(
            memory_store,
            registry,
        )

        result = agent.run(args.perguntar)
        print_agent_result(result)
        return

    if args.chat:
        agent = build_agent(
            memory_store,
            registry,
        )

        run_chat(agent)
        return

    status = get_system_status(registry)

    print("=" * 50)
    print(f"{status['name']} v{status['version']}")
    print(f"Status: {status['status']}")
    print(f"Ferramentas carregadas: {status['tools_loaded']}")
    print("=" * 50)
    print("IA, memória e ferramentas inicializadas.")
    print("Use 'assistente --chat' para conversar.")


if __name__ == "__main__":
    main()
