from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyResult:
    policy_id: str
    title: str
    summary: str
    requires_approval: bool = False


POLICIES = {
    "incident": PolicyResult(
        policy_id="IR-001",
        title="Incident Response Policy",
        summary="Severity 1 and 2 incidents require triage, commander assignment, and audit logging.",
        requires_approval=False,
    ),
    "access": PolicyResult(
        policy_id="AC-001",
        title="Access Control Policy",
        summary="Sensitive incident artifacts require least-privilege access and manager approval.",
        requires_approval=True,
    ),
    "support": PolicyResult(
        policy_id="CS-001",
        title="Customer Support FAQ",
        summary="Support teams can draft customer-facing updates after incident commander review.",
        requires_approval=True,
    ),
}

POLICY_KEYWORDS = [
    ("access", ("access", "artifact", "artifacts", "logs", "sensitive")),
    ("support", ("support", "customer", "faq", "ticket")),
    ("incident", ("incident", "severity", "escalation", "outage")),
]


def search_policy(query: str) -> dict[str, object]:
    normalized = query.lower()
    for policy_key, keywords in POLICY_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            policy = POLICIES[policy_key]
            return {
                "matched": True,
                "policy_id": policy.policy_id,
                "title": policy.title,
                "summary": policy.summary,
                "requires_approval": policy.requires_approval,
            }

    return {
        "matched": False,
        "policy_id": None,
        "title": None,
        "summary": "No matching synthetic policy found.",
        "requires_approval": False,
    }


def create_ticket_draft(summary: str, severity: str) -> dict[str, str]:
    return {
        "status": "draft",
        "summary": summary,
        "severity": severity,
        "next_step": "Human review required before creating a real ticket.",
    }


def request_approval(action: str, reason: str) -> dict[str, str]:
    return {
        "status": "approval_required",
        "action": action,
        "reason": reason,
        "approval_channel": "synthetic-manager-review",
    }
