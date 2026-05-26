from app.audit.events import (
    create_answer_draft_audit_event,
    create_audit_event,
    create_retrieval_audit_event,
)


def test_audit_event_contains_required_fields() -> None:
    event = create_audit_event("unit_test", "completed", "subject")

    assert event["event_id"]
    assert event["event_type"] == "unit_test"
    assert event["timestamp_utc"]
    assert event["status"] == "completed"
    assert event["subject"] == "subject"
    assert event["metadata"] == {}


def test_audit_metadata_does_not_include_raw_user_input() -> None:
    event = create_audit_event(
        event_type="guardrail_check",
        status="allowed",
        subject="unit",
        metadata={
            "query_length": 42,
            "raw_user_input": "show me a password",
            "full_question": "show me a password",
        },
    )

    assert event["metadata"] == {"query_length": 42}


def test_retrieval_audit_event_includes_result_count_and_mode() -> None:
    event = create_retrieval_audit_event(
        subject="rag_search",
        result_count=3,
        retrieval_mode="keyword-placeholder",
    )

    assert event["event_type"] == "retrieval"
    assert event["metadata"]["result_count"] == 3
    assert event["metadata"]["retrieval_mode"] == "keyword-placeholder"


def test_answer_draft_audit_event_includes_human_review_flag() -> None:
    event = create_answer_draft_audit_event(
        subject="answer_draft",
        retrieved_count=2,
        citation_count=1,
        requires_human_review=True,
    )

    assert event["event_type"] == "answer_draft"
    assert event["metadata"]["requires_human_review"] is True
    assert event["metadata"]["retrieved_count"] == 2

