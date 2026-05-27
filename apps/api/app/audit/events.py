from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


SAFE_METADATA_KEYS = {
    "approval_status",
    "classification_intent",
    "classification_severity",
    "query_length",
    "question_length",
    "result_count",
    "risk_level",
    "flags",
    "retrieval_mode",
    "requires_human_review",
    "citation_count",
    "retrieved_count",
    "ticket_status",
    "tool_name",
    "tool_mode",
    "workflow_type",
}


def sanitize_metadata(metadata: dict[str, object] | None = None) -> dict[str, object]:
    if not metadata:
        return {}
    return {key: value for key, value in metadata.items() if key in SAFE_METADATA_KEYS}


def create_audit_event(
    event_type: str,
    status: str,
    subject: str,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "status": status,
        "subject": subject,
        "metadata": sanitize_metadata(metadata),
    }


def create_guardrail_audit_event(
    subject: str,
    guardrail_result: dict[str, object],
    text_length: int,
) -> dict[str, object]:
    return create_audit_event(
        event_type="guardrail_check",
        status="allowed" if guardrail_result["allowed"] else "blocked",
        subject=subject,
        metadata={
            "query_length": text_length,
            "question_length": text_length,
            "risk_level": guardrail_result["risk_level"],
            "flags": guardrail_result["flags"],
        },
    )


def create_retrieval_audit_event(
    subject: str,
    result_count: int,
    retrieval_mode: str,
) -> dict[str, object]:
    return create_audit_event(
        event_type="retrieval",
        status="completed",
        subject=subject,
        metadata={
            "result_count": result_count,
            "retrieval_mode": retrieval_mode,
        },
    )


def create_answer_draft_audit_event(
    subject: str,
    retrieved_count: int,
    citation_count: int,
    requires_human_review: bool,
) -> dict[str, object]:
    return create_audit_event(
        event_type="answer_draft",
        status="completed",
        subject=subject,
        metadata={
            "retrieved_count": retrieved_count,
            "citation_count": citation_count,
            "requires_human_review": requires_human_review,
        },
    )

