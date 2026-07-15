"""Ponto de entrada do Assistente Local."""

import argparse
import json
from typing import Any

from assistente_local import __version__
from assistente_local.tools import ToolRegistry, build_default_registry

APP_NAME = "Assistente Local"


def get_system_status(registry: ToolRegistry | None = None) -> dict[str, Any]:
    """Retorna informações sobre o estado atual do sistema."""

    tools_loaded = registry.count() if registry is not None else 0

    return {
        "name": APP_NAME,
        "version": __version__,
        "status": "online",
        "tools_loaded": tools_loaded,
    }


def build_parser() -> argparse.ArgumentParser:
    """Cria os argumentos aceitos pela linha de comando."""

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
        help="Abre um programa permitido.",
    )

    return parser


def print_result(result_message: str, result_data: dict[str, Any]) -> None:
    """Exibe o resultado de uma ferramenta."""

    print(result_message)

    if result_data:
        print(json.dumps(result_data, ensure_ascii=False, indent=2))


def main() -> None:
    """Inicializa o Assistente Local."""

    parser = build_parser()
    args = parser.parse_args()

    registry = build_default_registry()

    if args.listar_ferramentas:
        print(json.dumps(registry.list_schemas(), ensure_ascii=False, indent=2))
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

    status = get_system_status(registry)

    print("=" * 50)
    print(f"{status['name']} v{status['version']}")
    print(f"Status: {status['status']}")
    print(f"Ferramentas carregadas: {status['tools_loaded']}")
    print("=" * 50)
    print("Sistema de ferramentas inicializado.")


if __name__ == "__main__":
    main()
