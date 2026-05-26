import importlib

from server import create_ticket_draft, get_customer_context, request_approval, search_policy


SECRET_PATTERNS = ("api key", "password", "secret token", "private key")


def payload_text(payload: dict[str, object]) -> str:
    return str(payload).lower()


def test_search_policy_returns_deterministic_synthetic_results() -> None:
    result = search_policy("What is the incident escalation process?")

    assert result["query"] == "What is the incident escalation process?"
    assert result["requires_human_review"] is True
    assert result["matches"][0]["policy_id"] == "IR-001"


def test_create_ticket_draft_returns_draft_status() -> None:
    result = create_ticket_draft("Authentication errors above threshold", "sev2")

    assert str(result["ticket_draft_id"]).startswith("ticket-draft-")
    assert result["status"] == "draft"
    assert result["requires_human_review"] is True


def test_request_approval_returns_pending_status() -> None:
    result = request_approval("create_ticket", "External system change")

    assert str(result["approval_request_id"]).startswith("approval-request-")
    assert result["status"] == "pending"
    assert result["requires_human_review"] is True


def test_get_customer_context_returns_synthetic_only_context() -> None:
    result = get_customer_context("synthetic-customer-001")

    assert result["customer_id"] == "synthetic-customer-001"
    assert result["tier"] == "enterprise"
    assert result["data_classification"] == "synthetic"


def test_action_like_tools_require_human_review() -> None:
    ticket = create_ticket_draft("Synthetic summary", "medium")
    approval = request_approval("review_ticket", "Draft-only action")

    assert ticket["requires_human_review"] is True
    assert approval["requires_human_review"] is True


def test_tools_do_not_return_real_secret_markers() -> None:
    payloads = [
        search_policy("incident"),
        create_ticket_draft("Synthetic summary", "medium"),
        request_approval("review_ticket", "Draft-only action"),
        get_customer_context("synthetic-customer-001"),
    ]

    for payload in payloads:
        text = payload_text(payload)
        assert all(pattern not in text for pattern in SECRET_PATTERNS)


def test_importing_server_does_not_start_blocking_loop() -> None:
    module = importlib.import_module("server")

    assert hasattr(module, "mcp")

