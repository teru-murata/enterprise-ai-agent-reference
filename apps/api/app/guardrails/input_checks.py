from __future__ import annotations


GUARDRAIL_PATTERNS = {
    "prompt_injection": [
        "ignore previous instructions",
        "reveal system prompt",
        "show hidden instructions",
        "bypass policy",
        "developer message",
    ],
    "secret_extraction": [
        "api key",
        "password",
        "secret token",
        "private key",
    ],
    "unsafe_tool_execution": [
        "execute without approval",
        "delete records",
        "disable audit",
        "skip human review",
    ],
}

HIGH_RISK_FLAGS = {"prompt_injection", "secret_extraction", "unsafe_tool_execution"}


def analyze_user_input(text: str) -> dict[str, object]:
    normalized = text.lower()
    flags: list[str] = []
    messages: list[str] = []

    for category, patterns in GUARDRAIL_PATTERNS.items():
        matched_patterns = [pattern for pattern in patterns if pattern in normalized]
        if matched_patterns:
            flags.append(category)
            messages.append(f"Detected {category.replace('_', ' ')} pattern.")

    if any(flag in HIGH_RISK_FLAGS for flag in flags):
        risk_level = "high"
    elif flags:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "allowed": risk_level != "high",
        "risk_level": risk_level,
        "flags": flags,
        "messages": messages,
    }

