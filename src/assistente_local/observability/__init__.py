"""Observabilidade e logs do Hefesto."""

from assistente_local.observability.logging_setup import (
    setup_logging,
)
from assistente_local.observability.redaction import (
    redact_sensitive_values,
)

__all__ = [
    "redact_sensitive_values",
    "setup_logging",
]