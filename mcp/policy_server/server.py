from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid5, NAMESPACE_URL

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Enterprise Policy Action Server")


@dataclass(frozen=True)
class PolicyResult:
    policy_id: str
    title: str
    summary: str
    requires_approval: bool = True


POLICIES = {
    "incident": PolicyResult(
        policy_id="IR-001",
        title="Incident Response Policy",
        summary="Severity 1 and 2 incidents require triage, commander assignment, and audit logging.",
        requires_approval=True,
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

SYNTHETIC_CUSTOMERS = {
    "synthetic-customer-001": {
        "tier": "enterprise",
        "support_notes": [
            "Synthetic account used for incident-support workflow demos.",
            "No real customer data is stored or returned.",
        ],
        "data_classification": "synthetic",
    },
    "synthetic-customer-002": {
        "tier": "standard",
        "support_notes": [
            "Synthetic account for lower-priority support examples.",
            "No real customer data is stored or returned.",
        ],
        "data_classification": "synthetic",
    },
}


def deterministic_id(prefix: str, *parts: str) -> str:
    seed = ":".join(parts)
    return f"{prefix}-{uuid5(NAMESPACE_URL, seed)}"


@mcp.tool()
def search_policy(query: str) -> dict[str, object]:
    """Search deterministic synthetic enterprise policy data."""
    normalized = query.lower()
    matches: list[dict[str, object]] = []

    for policy_key, keywords in POLICY_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            policy = POLICIES[policy_key]
            matches.append(
                {
                    "policy_id": policy.policy_id,
                    "title": policy.title,
                    "summary": policy.summary,
                    "requires_human_review": True,
                }
            )

    return {
        "query": query,
        "matches": matches,
        "requires_human_review": True,
    }


@mcp.tool()
def create_ticket_draft(summary: str, severity: str) -> dict[str, object]:
    """Create a synthetic ticket draft without external side effects."""
    return {
        "ticket_draft_id": deterministic_id("ticket-draft", summary, severity),
        "summary": summary,
        "severity": severity,
        "status": "draft",
        "requires_human_review": True,
    }


@mcp.tool()
def request_approval(action: str, reason: str) -> dict[str, object]:
    """Create a synthetic approval request without external side effects."""
    return {
        "approval_request_id": deterministic_id("approval-request", action, reason),
        "action": action,
        "reason": reason,
        "status": "pending",
        "requires_human_review": True,
    }


@mcp.tool()
def get_customer_context(customer_id: str) -> dict[str, object]:
    """Return synthetic customer context only."""
    context = SYNTHETIC_CUSTOMERS.get(
        customer_id,
        {
            "tier": "unknown",
            "support_notes": [
                "Synthetic fallback context.",
                "No real customer data is stored or returned.",
            ],
            "data_classification": "synthetic",
        },
    )
    return {
        "customer_id": customer_id,
        "tier": context["tier"],
        "support_notes": context["support_notes"],
        "data_classification": "synthetic",
    }


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
