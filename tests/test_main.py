"""Testes do módulo principal."""

from assistente_local.main import APP_NAME, APP_VERSION, get_system_status


def test_system_status() -> None:
    status = get_system_status()

    assert status["name"] == APP_NAME
    assert status["version"] == APP_VERSION
    assert status["status"] == "online"
    assert status["tools_loaded"] == 0