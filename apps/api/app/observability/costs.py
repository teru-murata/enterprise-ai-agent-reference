from __future__ import annotations

import json
import os


def null_cost(method: str = "not_configured") -> dict[str, object]:
    return {
        "estimated_cost_usd": None,
        "cost_estimation_method": method,
    }


def estimate_cost_usd(provider: str, model: str, usage: dict[str, int | None]) -> dict[str, object]:
    raw_config = os.getenv("MODEL_PRICING_CONFIG_JSON")
    if not raw_config:
        return null_cost()

    try:
        pricing_config = json.loads(raw_config)
    except json.JSONDecodeError:
        return null_cost("invalid_config")

    model_config = pricing_config.get(provider, {}).get(model)
    if not model_config:
        return null_cost("model_not_configured")

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if input_tokens is None or output_tokens is None:
        return null_cost("usage_missing")

    input_rate = float(model_config.get("input_per_1m_tokens_usd", 0.0))
    output_rate = float(model_config.get("output_per_1m_tokens_usd", 0.0))
    estimated_cost = (input_tokens / 1_000_000 * input_rate) + (
        output_tokens / 1_000_000 * output_rate
    )
    return {
        "estimated_cost_usd": round(estimated_cost, 8),
        "cost_estimation_method": "configured_per_1m_tokens",
    }
