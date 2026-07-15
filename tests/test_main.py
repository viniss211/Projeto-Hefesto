"""Testes do módulo principal."""

from assistente_local import __version__
from assistente_local.main import APP_NAME, get_system_status
from assistente_local.tools import build_default_registry


def test_system_status() -> None:
    registry = build_default_registry()
    status = get_system_status(registry)

    assert status["name"] == APP_NAME
    assert status["version"] == __version__
    assert status["status"] == "online"
    assert status["tools_loaded"] == 2
