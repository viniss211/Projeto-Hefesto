"""Remoção de dados sensíveis antes de registrar logs."""

from typing import Any

SENSITIVE_PARTS = {
    "api_key",
    "apikey",
    "authorization",
    "password",
    "senha",
    "secret",
    "token",
}


def is_sensitive_key(key: str) -> bool:
    """Identifica nomes que provavelmente contêm segredos."""

    normalized = key.lower()

    return any(
        sensitive_part in normalized
        for sensitive_part in SENSITIVE_PARTS
    )


def redact_sensitive_values(value: Any) -> Any:
    """Substitui informações sensíveis por um marcador."""

    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED]"
                if is_sensitive_key(str(key))
                else redact_sensitive_values(item)
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            redact_sensitive_values(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return tuple(
            redact_sensitive_values(item)
            for item in value
        )

    return value