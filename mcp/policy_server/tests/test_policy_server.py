from server import create_ticket_draft, request_approval, search_policy


def test_search_policy_matches_incident_policy() -> None:
    result = search_policy("What is the incident escalation process?")

    assert result["matched"] is True
    assert result["policy_id"] == "IR-001"


def test_search_policy_flags_access_approval() -> None:
    result = search_policy("Can I access sensitive incident artifacts?")

    assert result["matched"] is True
    assert result["requires_approval"] is True


def test_create_ticket_draft_does_not_create_real_ticket() -> None:
    result = create_ticket_draft("Authentication errors above threshold", "sev2")

    assert result["status"] == "draft"
    assert "Human review required" in result["next_step"]


def test_request_approval_returns_approval_request() -> None:
    result = request_approval("create_ticket", "External system change")

    assert result["status"] == "approval_required"
    assert result["approval_channel"] == "synthetic-manager-review"

