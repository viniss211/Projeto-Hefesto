"""Testes do registro de ferramentas."""

import pytest

from assistente_local.tools import BaseTool, ToolRegistry, ToolResult


class ExampleTool(BaseTool):
    """Ferramenta falsa usada somente nos testes."""

    name = "example_tool"
    description = "Ferramenta de teste."
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        return ToolResult(
            success=True,
            message="Ferramenta executada.",
            data={"arguments": arguments},
        )


class ApprovalTool(ExampleTool):
    """Ferramenta falsa que exige aprovação."""

    name = "approval_tool"
    requires_approval = True


def test_register_and_execute_tool() -> None:
    registry = ToolRegistry()
    registry.register(ExampleTool())

    result = registry.execute("example_tool", {"value": 10})

    assert result.success is True
    assert result.data["arguments"] == {"value": 10}


def test_reject_duplicate_tool() -> None:
    registry = ToolRegistry()
    registry.register(ExampleTool())

    with pytest.raises(ValueError):
        registry.register(ExampleTool())


def test_unknown_tool() -> None:
    registry = ToolRegistry()

    result = registry.execute("unknown_tool")

    assert result.success is False
    assert result.data["available_tools"] == []


def test_tool_requires_approval() -> None:
    registry = ToolRegistry()
    registry.register(ApprovalTool())

    blocked_result = registry.execute("approval_tool")

    assert blocked_result.success is False
    assert blocked_result.data["approval_required"] is True

    approved_result = registry.execute(
        "approval_tool",
        approved=True,
    )

    assert approved_result.success is True
