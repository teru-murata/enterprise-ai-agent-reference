from __future__ import annotations

from typing import Literal


RetrievalMode = Literal["keyword", "pgvector"]

RETRIEVAL_MODE_LABELS = {
    "keyword": "keyword-placeholder",
    "pgvector": "pgvector-placeholder",
}


def parse_retrieval_mode(mode: str | None = None) -> RetrievalMode:
    normalized = (mode or "keyword").strip().lower()
    if normalized in {"keyword", "keyword-placeholder"}:
        return "keyword"
    if normalized in {"pgvector", "pgvector-placeholder"}:
        return "pgvector"

    msg = "Unsupported retrieval mode. Expected 'keyword' or 'pgvector'."
    raise ValueError(msg)
