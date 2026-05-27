import importlib
import os

import pytest

from app.rag import embeddings
from app.rag.embeddings import (
    DEFAULT_EMBEDDING_DIMENSIONS,
    embed_text,
    embed_text_deterministic,
    embed_text_openai,
    get_embedding_dimensions,
    get_embedding_provider,
)


def test_deterministic_provider_is_default(monkeypatch) -> None:
    monkeypatch.delenv("EMBEDDING_PROVIDER", raising=False)

    assert get_embedding_provider() == "deterministic"
    assert embed_text("incident escalation") == embed_text_deterministic("incident escalation")


def test_openai_provider_requires_explicit_selection(monkeypatch) -> None:
    monkeypatch.delenv("EMBEDDING_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    embedding = embed_text("incident escalation")

    assert len(embedding) == DEFAULT_EMBEDDING_DIMENSIONS


def test_missing_openai_api_key_fails_clearly(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is required"):
        embed_text("incident escalation", provider="openai")


def test_embedding_dimensions_are_consistent(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_EMBEDDING_DIMENSIONS", "16")

    assert get_embedding_dimensions() == 16
    assert len(embed_text_deterministic("incident escalation", dimensions=16)) == 16


def test_invalid_embedding_provider_fails() -> None:
    with pytest.raises(ValueError, match="Unsupported embedding provider"):
        get_embedding_provider("unknown")


def test_openai_client_is_not_initialized_at_import(monkeypatch) -> None:
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    importlib.reload(embeddings)


@pytest.mark.skipif(
    os.getenv("RUN_OPENAI_EMBEDDING_TESTS") != "1" or not os.getenv("OPENAI_API_KEY"),
    reason="OpenAI embedding smoke test requires RUN_OPENAI_EMBEDDING_TESTS=1 and OPENAI_API_KEY",
)
def test_openai_embedding_provider_smoke() -> None:
    embedding = embed_text_openai("synthetic incident support policy", dimensions=16)

    assert len(embedding) == 16
