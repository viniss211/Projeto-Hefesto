"""Ferramentas seguras para abertura de programas permitidos."""

import shutil
import subprocess
import unicodedata
from typing import Any

from assistente_local.tools.base import BaseTool, ToolResult

APPLICATIONS: dict[str, list[str]] = {
    "calculadora": ["calc.exe"],
    "bloco_de_notas": ["notepad.exe"],
    "paint": ["mspaint.exe"],
    "explorador_de_arquivos": ["explorer.exe"],
    "vscode": ["code"],
}

APPLICATION_ALIASES: dict[str, str] = {
    "calc": "calculadora",
    "calculator": "calculadora",
    "calculadora": "calculadora",
    "notepad": "bloco_de_notas",
    "bloco de notas": "bloco_de_notas",
    "bloco_de_notas": "bloco_de_notas",
    "paint": "paint",
    "explorer": "explorador_de_arquivos",
    "explorador": "explorador_de_arquivos",
    "explorador de arquivos": "explorador_de_arquivos",
    "explorador_de_arquivos": "explorador_de_arquivos",
    "code": "vscode",
    "vs code": "vscode",
    "vscode": "vscode",
    "visual studio code": "vscode",
}


def normalize_text(value: str) -> str:
    """Normaliza texto para comparação de comandos."""

    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )

    return " ".join(without_accents.lower().strip().split())


def resolve_application(value: str) -> str | None:
    """Converte um nome ou apelido para o nome oficial da aplicação."""

    normalized = normalize_text(value)
    return APPLICATION_ALIASES.get(normalized)


class ListApplicationsTool(BaseTool):
    """Lista os programas que o assistente está autorizado a abrir."""

    name = "list_applications"
    description = "Lista os programas permitidos para abertura no computador."
    requires_approval = False

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        del arguments

        applications = sorted(APPLICATIONS)

        return ToolResult(
            success=True,
            message=f"{len(applications)} programas estão disponíveis.",
            data={"applications": applications},
        )


class OpenApplicationTool(BaseTool):
    """Abre uma aplicação presente na lista permitida."""

    name = "open_application"
    description = (
        "Abre um programa permitido no Windows, como calculadora, "
        "bloco de notas, Paint, explorador de arquivos ou VS Code."
    )
    requires_approval = False

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "application": {
                "type": "string",
                "description": "Nome do programa que deve ser aberto.",
            }
        },
        "required": ["application"],
        "additionalProperties": False,
    }

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        application_value = arguments.get("application")

        if not isinstance(application_value, str):
            return ToolResult(
                success=False,
                message="O parâmetro 'application' deve ser um texto.",
            )

        application_name = resolve_application(application_value)

        if application_name is None:
            return ToolResult(
                success=False,
                message=f"Programa não permitido ou desconhecido: {application_value}.",
                data={"available_applications": sorted(APPLICATIONS)},
            )

        command = APPLICATIONS[application_name]
        executable = shutil.which(command[0])

        if executable is None:
            return ToolResult(
                success=False,
                message=f"O programa {application_name} não foi encontrado no computador.",
                data={"command": command[0]},
            )

        subprocess.Popen(
            [executable, *command[1:]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )

        return ToolResult(
            success=True,
            message=f"Programa aberto: {application_name}.",
            data={"application": application_name},
        )
