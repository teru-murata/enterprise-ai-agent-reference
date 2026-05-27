from __future__ import annotations

import asyncio
import json
import sys
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from app.rag.documents import find_repository_root


ToolMode = Literal["local", "mcp-stdio"]
SUPPORTED_TOOL_MODES = {"local", "mcp-stdio"}

POLICY_MATCHES = {
    "incident": {
        "policy_id": "IR-001",
        "title": "Incident Response Policy",
        "summary": "Severity 1 and 2 incidents require triage, commander assignment, and audit logging.",
        "requires_human_review": True,
    },
    "access": {
        "policy_id": "AC-001",
        "title": "Access Control Policy",
        "summary": "Sensitive incident artifacts require least-privilege access and manager approval.",
        "requires_human_review": True,
    },
    "support": {
        "policy_id": "CS-001",
        "title": "Customer Support FAQ",
        "summary": "Support teams can draft customer-facing updates after incident commander review.",
        "requires_human_review": True,
    },
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


def validate_tool_mode(tool_mode: str) -> ToolMode:
    if tool_mode not in SUPPORTED_TOOL_MODES:
        msg = f"Unsupported tool_mode {tool_mode!r}. Expected 'local' or 'mcp-stdio'."
        raise ValueError(msg)
    return tool_mode  # type: ignore[return-value]


def deterministic_id(prefix: str, *parts: str) -> str:
    seed = ":".join(parts)
    return f"{prefix}-{uuid5(NAMESPACE_URL, seed)}"


def search_policy_local(query: str) -> dict[str, object]:
    normalized = query.lower()
    matches: list[dict[str, object]] = []
    for policy_key, keywords in POLICY_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            matches.append(POLICY_MATCHES[policy_key])

    return {
        "query": query,
        "matches": matches,
        "requires_human_review": True,
    }


def create_ticket_draft_local(summary: str, severity: str) -> dict[str, object]:
    return {
        "ticket_draft_id": deterministic_id("ticket-draft", summary, severity),
        "summary": summary,
        "severity": severity,
        "status": "draft",
        "requires_human_review": True,
    }


def request_approval_local(action: str, reason: str) -> dict[str, object]:
    return {
        "approval_request_id": deterministic_id("approval-request", action, reason),
        "action": action,
        "reason": reason,
        "status": "pending",
        "requires_human_review": True,
    }


def get_customer_context_local(customer_id: str) -> dict[str, object]:
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


async def call_mcp_stdio_tool(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    repo_root = find_repository_root()
    server_dir = repo_root / "mcp" / "policy_server"
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "server"],
        cwd=str(server_dir),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)

    if result.isError:
        msg = f"MCP tool {tool_name!r} returned an error."
        raise RuntimeError(msg)

    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured

    if result.content:
        text = getattr(result.content[0], "text", None)
        if text:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed

    msg = f"MCP tool {tool_name!r} did not return a structured dictionary payload."
    raise RuntimeError(msg)


def call_tool(tool_name: str, arguments: dict[str, object], tool_mode: str = "local") -> dict[str, object]:
    mode = validate_tool_mode(tool_mode)
    if mode == "local":
        if tool_name == "search_policy":
            return search_policy_local(str(arguments["query"]))
        if tool_name == "create_ticket_draft":
            return create_ticket_draft_local(str(arguments["summary"]), str(arguments["severity"]))
        if tool_name == "request_approval":
            return request_approval_local(str(arguments["action"]), str(arguments["reason"]))
        if tool_name == "get_customer_context":
            return get_customer_context_local(str(arguments["customer_id"]))
        msg = f"Unsupported local tool {tool_name!r}."
        raise ValueError(msg)

    try:
        return asyncio.run(call_mcp_stdio_tool(tool_name, arguments))
    except Exception as error:
        msg = f"MCP stdio tool call failed for {tool_name}: {error}"
        raise RuntimeError(msg) from error


def search_policy(query: str, tool_mode: str = "local") -> dict[str, object]:
    return call_tool("search_policy", {"query": query}, tool_mode)


def create_ticket_draft(summary: str, severity: str, tool_mode: str = "local") -> dict[str, object]:
    return call_tool(
        "create_ticket_draft",
        {"summary": summary, "severity": severity},
        tool_mode,
    )


def request_approval(action: str, reason: str, tool_mode: str = "local") -> dict[str, object]:
    return call_tool("request_approval", {"action": action, "reason": reason}, tool_mode)


def get_customer_context(customer_id: str, tool_mode: str = "local") -> dict[str, object]:
    return call_tool("get_customer_context", {"customer_id": customer_id}, tool_mode)
