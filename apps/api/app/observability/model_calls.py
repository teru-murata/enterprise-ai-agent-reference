from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter
from uuid import uuid4

from app.observability.costs import estimate_cost_usd


NULL_USAGE = {
    "input_tokens": None,
    "output_tokens": None,
    "total_tokens": None,
}

SAFE_METADATA_KEYS = {
    "answer_provider",
    "citation_count",
    "embedding_provider",
    "operation",
    "question_length",
    "request_id",
    "response_id",
    "retrieved_count",
    "service_tier",
}


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_utc_iso() -> str:
    return now_utc().isoformat()


def start_timer() -> float:
    return perf_counter()


def elapsed_ms(started_at: float) -> int:
    return max(0, round((perf_counter() - started_at) * 1000))


def read_attr_or_key(source: object, name: str) -> object | None:
    if isinstance(source, dict):
        return source.get(name)
    return getattr(source, name, None)


def extract_usage_from_openai_response(response: object) -> dict[str, int | None]:
    usage = read_attr_or_key(response, "usage")
    if usage is None:
        return dict(NULL_USAGE)

    input_tokens = read_attr_or_key(usage, "input_tokens")
    output_tokens = read_attr_or_key(usage, "output_tokens")
    total_tokens = read_attr_or_key(usage, "total_tokens")

    if input_tokens is None:
        input_tokens = read_attr_or_key(usage, "prompt_tokens")
    if output_tokens is None:
        output_tokens = read_attr_or_key(usage, "completion_tokens")
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = int(input_tokens) + int(output_tokens)

    return {
        "input_tokens": int(input_tokens) if input_tokens is not None else None,
        "output_tokens": int(output_tokens) if output_tokens is not None else None,
        "total_tokens": int(total_tokens) if total_tokens is not None else None,
    }


def extract_service_tier(response: object) -> str | None:
    service_tier = read_attr_or_key(response, "service_tier")
    return str(service_tier) if service_tier is not None else None


def extract_response_id(response: object) -> str | None:
    response_id = read_attr_or_key(response, "id")
    return str(response_id) if response_id is not None else None


def extract_request_id(response: object) -> str | None:
    request_id = read_attr_or_key(response, "_request_id") or read_attr_or_key(
        response, "request_id"
    )
    return str(request_id) if request_id is not None else None


def sanitize_metadata(metadata: dict[str, object] | None = None) -> dict[str, object]:
    if not metadata:
        return {}
    return {key: value for key, value in metadata.items() if key in SAFE_METADATA_KEYS}


def create_model_call_record(
    provider: str,
    operation: str,
    model: str,
    started_at_utc: str,
    completed_at_utc: str,
    latency_ms: int,
    status: str,
    usage: dict[str, int | None] | None = None,
    service_tier: str | None = None,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    safe_usage = usage or dict(NULL_USAGE)
    cost = estimate_cost_usd(provider=provider, model=model, usage=safe_usage)
    return {
        "call_id": str(uuid4()),
        "provider": provider,
        "operation": operation,
        "model": model,
        "started_at_utc": started_at_utc,
        "completed_at_utc": completed_at_utc,
        "latency_ms": max(0, int(latency_ms)),
        "status": status,
        "usage": safe_usage,
        "service_tier": service_tier,
        "estimated_cost_usd": cost["estimated_cost_usd"],
        "cost_estimation_method": cost["cost_estimation_method"],
        "safety": {
            "synthetic_data_only": True,
            "raw_prompt_logged": False,
            "raw_output_logged": False,
        },
        "metadata": sanitize_metadata(metadata),
    }


def create_skipped_model_call_record(
    provider: str,
    operation: str,
    model: str,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    timestamp = now_utc_iso()
    return create_model_call_record(
        provider=provider,
        operation=operation,
        model=model,
        started_at_utc=timestamp,
        completed_at_utc=timestamp,
        latency_ms=0,
        status="skipped",
        usage=dict(NULL_USAGE),
        metadata=metadata,
    )
