import os

import pytest

from app.mcp_bridge.client import (
    create_ticket_draft,
    get_customer_context,
    request_approval,
    search_policy,
)


def test_local_bridge_search_policy() -> None:
    result = search_policy("incident escalation", tool_mode="local")

    assert result["requires_human_review"] is True
    assert result["matches"][0]["policy_id"] == "IR-001"


def test_local_bridge_create_ticket_draft() -> None:
    result = create_ticket_draft("Synthetic incident summary", "medium", tool_mode="local")

    assert result["status"] == "draft"
    assert result["requires_human_review"] is True
    assert str(result["ticket_draft_id"]).startswith("ticket-draft-")


def test_local_bridge_request_approval() -> None:
    result = request_approval("review_ticket", "Draft-only action", tool_mode="local")

    assert result["status"] == "pending"
    assert result["requires_human_review"] is True


def test_local_bridge_get_customer_context() -> None:
    result = get_customer_context("synthetic-customer-001", tool_mode="local")

    assert result["customer_id"] == "synthetic-customer-001"
    assert result["data_classification"] == "synthetic"
    assert "api key" not in str(result).lower()


def test_local_bridge_action_outputs_preserve_human_review() -> None:
    ticket = create_ticket_draft("Synthetic incident summary", "medium", tool_mode="local")
    approval = request_approval("review_ticket", "Draft-only action", tool_mode="local")

    assert ticket["requires_human_review"] is True
    assert approval["requires_human_review"] is True


@pytest.mark.skipif(
    os.environ.get("RUN_MCP_STDIO_TESTS") != "1",
    reason="Explicit MCP stdio integration test; set RUN_MCP_STDIO_TESTS=1 to run.",
)
def test_mcp_stdio_bridge_calls_policy_server_tools() -> None:
    ticket = create_ticket_draft("Synthetic incident summary", "medium", tool_mode="mcp-stdio")
    approval = request_approval("review_ticket", "Draft-only action", tool_mode="mcp-stdio")

    assert ticket["status"] == "draft"
    assert ticket["requires_human_review"] is True
    assert approval["status"] == "pending"
    assert approval["requires_human_review"] is True
