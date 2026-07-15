"""Assistente Local."""

__version__ = "0.2.0"
"""Sistema de ferramentas do assistente."""

from assistente_local.tools.base import BaseTool, ToolResult
from assistente_local.tools.bootstrap import build_default_registry
from assistente_local.tools.registry import ToolRegistry

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "ToolResult",
    "build_default_registry",
]
