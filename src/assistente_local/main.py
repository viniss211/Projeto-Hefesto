"""Ponto de entrada do Assistente Local."""

import argparse
import json
from typing import Any

from assistente_local import __version__
from assistente_local.memory import create_default_memory_store
from assistente_local.tools import ToolRegistry, build_default_registry

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
        help="Abre um programa permitido.",
    )

    parser.add_argument(
        "--lembrar",
        nargs=2,
        metavar=("CHAVE", "VALOR"),
        help="Salva uma informação na memória.",
    )

    parser.add_argument(
        "--recordar",
        metavar="CONSULTA",
        help="Pesquisa uma informação na memória.",
    )

    parser.add_argument(
        "--categoria",
        default="general",
        help="Categoria usada ao salvar ou consultar uma memória.",
    )

    parser.add_argument(
        "--importancia",
        type=int,
        choices=range(1, 6),
        default=1,
        help="Importância da memória entre 1 e 5.",
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


def main() -> None:
    """Inicializa o Assistente Local."""

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

    status = get_system_status(registry)

    print("=" * 50)
    print(f"{status['name']} v{status['version']}")
    print(f"Status: {status['status']}")
    print(f"Ferramentas carregadas: {status['tools_loaded']}")
    print("=" * 50)
    print("Memória persistente inicializada.")


if __name__ == "__main__":
    main()