"""Testes das ferramentas de aplicações."""

from unittest.mock import patch

from assistente_local.tools.applications import (
    ListApplicationsTool,
    OpenApplicationTool,
    resolve_application,
)


def test_resolve_application_aliases() -> None:
    assert resolve_application("Calculadora") == "calculadora"
    assert resolve_application("bloco de notas") == "bloco_de_notas"
    assert resolve_application("VS Code") == "vscode"
    assert resolve_application("programa inexistente") is None


def test_list_applications() -> None:
    tool = ListApplicationsTool()

    result = tool.execute({})

    assert result.success is True
    assert "calculadora" in result.data["applications"]
    assert "vscode" in result.data["applications"]


@patch("assistente_local.tools.applications.subprocess.Popen")
@patch("assistente_local.tools.applications.shutil.which")
def test_open_calculator(mock_which, mock_popen) -> None:
    mock_which.return_value = r"C:\Windows\System32\calc.exe"

    tool = OpenApplicationTool()
    result = tool.execute({"application": "calculadora"})

    assert result.success is True
    assert result.data["application"] == "calculadora"

    mock_popen.assert_called_once()


def test_reject_unknown_application() -> None:
    tool = OpenApplicationTool()

    result = tool.execute({"application": "programa perigoso"})

    assert result.success is False
    assert "available_applications" in result.data
