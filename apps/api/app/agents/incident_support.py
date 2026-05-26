from __future__ import annotations

from uuid import uuid4

from app.answers.composer import compose_grounded_answer
from app.audit.events import (
    create_answer_draft_audit_event,
    create_audit_event,
    create_guardrail_audit_event,
    create_retrieval_audit_event,
)
from app.guardrails.input_checks import analyze_user_input
from app.mcp_bridge.client import (
    create_ticket_draft,
    get_customer_context,
    request_approval,
    validate_tool_mode,
)
from app.rag.chunking import split_into_chunks
from app.rag.documents import load_sample_documents
from app.rag.retrieval import retrieve_keyword_matches


def classify_incident(message: str, severity_hint: str | None = None) -> dict[str, object]:
    normalized = message.lower()

    if any(term in normalized for term in ("access", "authentication logs", "sensitive", "artifact")):
        intent = "access-control-sensitive"
    elif any(term in normalized for term in ("ticket", "customer", "support")):
        intent = "support-ticket-draft"
    elif any(term in normalized for term in ("incident", "outage", "severity", "degradation")):
        intent = "incident-guidance"
    else:
        intent = "general-incident-support"

    severity = severity_hint if severity_hint in {"low", "medium", "high"} else "medium"
    if any(term in normalized for term in ("severity 1", "sev1", "outage", "critical")):
        severity = "high"
    elif any(term in normalized for term in ("severity 2", "sev2", "degradation")):
        severity = "medium"
    elif any(term in normalized for term in ("severity 3", "sev3", "workaround")):
        severity = "low"

    return {
        "intent": intent,
        "severity": severity,
        "requires_approval": True,
    }


def create_local_ticket_draft(summary: str, severity: str) -> dict[str, str]:
    return create_ticket_draft(summary, severity, tool_mode="local")  # type: ignore[return-value]


def create_local_approval_request(action: str, reason: str) -> dict[str, str]:
    return request_approval(action, reason, tool_mode="local")  # type: ignore[return-value]


def blocked_answer(message: str) -> dict[str, object]:
    return {
        "question": message,
        "answer": "Safety response: the message was blocked by deterministic guardrail checks.",
        "confidence": "low",
        "citations": [],
        "limitations": [
            "Guardrail checks flagged high-risk input.",
            "No retrieval, answer drafting, ticket drafting, or approval workflow was performed.",
        ],
        "requires_human_review": True,
    }


def run_incident_support_workflow(request: dict[str, object]) -> dict[str, object]:
    message = str(request.get("message", ""))
    tool_mode = validate_tool_mode(str(request.get("tool_mode", "local")))
    severity_hint = request.get("severity_hint")
    severity_hint_value = str(severity_hint) if severity_hint is not None else None
    workflow_id = str(uuid4())
    workflow_type = "incident-support"

    guardrail_result = analyze_user_input(message)
    audit_events = [
        create_guardrail_audit_event(
            subject=workflow_type,
            guardrail_result=guardrail_result,
            text_length=len(message),
        )
    ]

    if not guardrail_result["allowed"]:
        classification = {
            "intent": "blocked",
            "severity": severity_hint_value or "unknown",
            "requires_approval": True,
        }
        audit_events.append(
            create_audit_event(
                event_type="agent_workflow",
                status="blocked",
                subject=workflow_type,
                metadata={
                    "workflow_type": workflow_type,
                    "tool_mode": tool_mode,
                    "risk_level": guardrail_result["risk_level"],
                    "flags": guardrail_result["flags"],
                    "requires_human_review": True,
                },
            )
        )
        return {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "status": "blocked",
            "classification": classification,
            "guardrail_result": guardrail_result,
            "answer_draft": blocked_answer(message),
            "ticket_draft": {
                "status": "blocked",
                "summary": "No ticket draft created because guardrails blocked the request.",
                "severity": classification["severity"],
                "next_step": "Human review required before any follow-up action.",
            },
            "approval_request": {
                "status": "pending",
                "action": "review_blocked_workflow",
                "reason": "Guardrail checks blocked the incident-support workflow.",
                "requires_human_review": True,
            },
            "audit_events": audit_events,
            "limitations": [
                "Guardrail-blocked workflow.",
                "No retrieval or normal answer composition was performed.",
                "No real tools were executed.",
            ],
        }

    classification = classify_incident(message, severity_hint_value)
    audit_events.append(
        create_audit_event(
            event_type="incident_classification",
            status="completed",
            subject=workflow_type,
            metadata={
                "workflow_type": workflow_type,
                "tool_mode": tool_mode,
                "classification_intent": classification["intent"],
                "classification_severity": classification["severity"],
                "requires_human_review": classification["requires_approval"],
            },
        )
    )

    documents = load_sample_documents()
    chunks = split_into_chunks(documents)
    retrieved_chunks = retrieve_keyword_matches(message, chunks)
    audit_events.append(
        create_retrieval_audit_event(
            subject=workflow_type,
            result_count=len(retrieved_chunks),
            retrieval_mode="keyword-placeholder",
        )
    )

    answer_draft = compose_grounded_answer(message, retrieved_chunks)
    audit_events.append(
        create_answer_draft_audit_event(
            subject=workflow_type,
            retrieved_count=len(retrieved_chunks),
            citation_count=len(answer_draft["citations"]),
            requires_human_review=bool(answer_draft["requires_human_review"]),
        )
    )

    customer_context = get_customer_context(str(request.get("customer_id")), tool_mode=tool_mode)
    audit_events.append(
        create_audit_event(
            event_type="customer_context",
            status="completed",
            subject=workflow_type,
            metadata={
                "workflow_type": workflow_type,
                "tool_mode": tool_mode,
            },
        )
    )

    ticket_draft = create_ticket_draft(
        summary=f"{classification['intent']} workflow draft for {request.get('customer_id')}",
        severity=str(classification["severity"]),
        tool_mode=tool_mode,
    )
    audit_events.append(
        create_audit_event(
            event_type="ticket_draft",
            status="drafted",
            subject=workflow_type,
            metadata={
                "workflow_type": workflow_type,
                "tool_mode": tool_mode,
                "ticket_status": ticket_draft["status"],
                "classification_severity": classification["severity"],
                "requires_human_review": True,
            },
        )
    )

    approval_request = request_approval(
        action="review_incident_support_draft",
        reason="All incident-support workflow outputs require approval before external action.",
        tool_mode=tool_mode,
    )
    audit_events.append(
        create_audit_event(
            event_type="approval_request",
            status="approval_required",
            subject=workflow_type,
            metadata={
                "workflow_type": workflow_type,
                "tool_mode": tool_mode,
                "approval_status": approval_request["status"],
                "requires_human_review": True,
            },
        )
    )

    return {
        "workflow_id": workflow_id,
        "workflow_type": workflow_type,
        "status": "drafted",
        "classification": classification,
        "guardrail_result": guardrail_result,
        "answer_draft": answer_draft,
        "customer_context": customer_context,
        "ticket_draft": ticket_draft,
        "approval_request": approval_request,
        "audit_events": audit_events,
        "limitations": [
            "Deterministic workflow scaffold only.",
            "Ticket creation is draft-only.",
            "Approval is mandatory before any real action.",
            "No real tools or model calls were executed.",
        ],
    }

