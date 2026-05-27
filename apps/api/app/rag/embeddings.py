from __future__ import annotations

import hashlib
import math
import os
import re
from typing import Literal

from app.observability.model_calls import (
    create_model_call_record,
    elapsed_ms,
    extract_request_id,
    extract_response_id,
    extract_service_tier,
    extract_usage_from_openai_response,
    now_utc_iso,
    start_timer,
)


EmbeddingProvider = Literal["deterministic", "openai"]
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_EMBEDDING_DIMENSIONS = 16


def tokenize_for_embedding(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def embed_text_deterministic(text: str, dimensions: int = 16) -> list[float]:
    """Create a deterministic placeholder embedding without external model calls."""

    if dimensions <= 0:
        raise ValueError("dimensions must be positive")

    vector = [0.0 for _ in range(dimensions)]
    for token in tokenize_for_embedding(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector

    return [round(value / norm, 6) for value in vector]


def get_embedding_provider(provider: str | None = None) -> EmbeddingProvider:
    selected = (provider or os.getenv("EMBEDDING_PROVIDER", "deterministic")).strip().lower()
    if selected == "deterministic":
        return "deterministic"
    if selected == "openai":
        return "openai"

    msg = "Unsupported embedding provider. Expected 'deterministic' or 'openai'."
    raise ValueError(msg)


def get_embedding_dimensions(dimensions: int | None = None) -> int:
    if dimensions is not None:
        selected_dimensions = dimensions
    else:
        raw_dimensions = os.getenv("OPENAI_EMBEDDING_DIMENSIONS")
        selected_dimensions = (
            int(raw_dimensions) if raw_dimensions else DEFAULT_EMBEDDING_DIMENSIONS
        )

    if selected_dimensions <= 0:
        raise ValueError("embedding dimensions must be positive")
    return selected_dimensions


def embed_text_openai(
    text: str,
    dimensions: int | None = None,
    model: str | None = None,
) -> list[float]:
    result = embed_text_openai_with_metadata(text=text, dimensions=dimensions, model=model)
    return list(result["embedding"])


def embed_text_openai_with_metadata(
    text: str,
    dimensions: int | None = None,
    model: str | None = None,
) -> dict[str, object]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")

    selected_model = model or os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_OPENAI_EMBEDDING_MODEL)
    selected_dimensions = get_embedding_dimensions(dimensions)

    from openai import OpenAI

    client = OpenAI()
    started_at = start_timer()
    started_at_utc = now_utc_iso()
    response = client.embeddings.create(
        model=selected_model,
        input=text,
        dimensions=selected_dimensions,
    )
    completed_at_utc = now_utc_iso()
    embedding = response.data[0].embedding
    if len(embedding) != selected_dimensions:
        raise RuntimeError(
            "OpenAI embedding dimension mismatch. "
            f"Expected {selected_dimensions}, received {len(embedding)}."
        )
    model_call = create_model_call_record(
        provider="openai",
        operation="embeddings.create",
        model=selected_model,
        started_at_utc=started_at_utc,
        completed_at_utc=completed_at_utc,
        latency_ms=elapsed_ms(started_at),
        status="succeeded",
        usage=extract_usage_from_openai_response(response),
        service_tier=extract_service_tier(response),
        metadata={
            "embedding_provider": "openai",
            "operation": "embeddings.create",
            "response_id": extract_response_id(response),
            "request_id": extract_request_id(response),
            "service_tier": extract_service_tier(response),
        },
    )
    return {
        "embedding": [float(value) for value in embedding],
        "model_call": model_call,
    }


def embed_text(
    text: str,
    provider: str | None = None,
    dimensions: int | None = None,
) -> list[float]:
    selected_provider = get_embedding_provider(provider)
    selected_dimensions = get_embedding_dimensions(dimensions)

    if selected_provider == "deterministic":
        return embed_text_deterministic(text, dimensions=selected_dimensions)

    return embed_text_openai(text, dimensions=selected_dimensions)


def embed_text_with_metadata(
    text: str,
    provider: str | None = None,
    dimensions: int | None = None,
) -> dict[str, object]:
    selected_provider = get_embedding_provider(provider)
    selected_dimensions = get_embedding_dimensions(dimensions)

    if selected_provider == "deterministic":
        return {
            "embedding": embed_text_deterministic(text, dimensions=selected_dimensions),
            "model_call": None,
        }

    return embed_text_openai_with_metadata(text, dimensions=selected_dimensions)
