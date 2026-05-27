import importlib
import os

import pytest

from app.db.connection import connect
from app.rag.documents import find_repository_root
from app.rag.embeddings import embed_text_deterministic
from app.rag.pgvector_store import (
    EMBEDDING_DIMENSIONS,
    initialize_schema,
    ingest_documents_to_pgvector,
    search_pgvector,
    vector_literal,
)


def test_deterministic_embedding_is_stable() -> None:
    first = embed_text_deterministic("incident escalation approval")
    second = embed_text_deterministic("incident escalation approval")

    assert first == second


def test_deterministic_embedding_dimension_is_correct() -> None:
    embedding = embed_text_deterministic("incident escalation approval", dimensions=16)

    assert len(embedding) == 16
    assert all(isinstance(value, float) for value in embedding)


def test_vector_literal_formats_pgvector_value() -> None:
    literal = vector_literal([0.5, -0.25])

    assert literal == "[0.500000,-0.250000]"


def test_schema_file_exists_and_contains_vector_column() -> None:
    schema = (
        find_repository_root()
        / "apps"
        / "api"
        / "app"
        / "db"
        / "schema.sql"
    ).read_text(encoding="utf-8")

    assert "CREATE EXTENSION IF NOT EXISTS vector" in schema
    assert f"embedding vector({EMBEDDING_DIMENSIONS})" in schema
    assert "document_chunks" in schema


def test_pgvector_module_does_not_connect_at_import(monkeypatch) -> None:
    import app.db.connection as connection_module
    import app.rag.pgvector_store as pgvector_store

    def fail_connect(*args, **kwargs):
        raise AssertionError("import should not connect to PostgreSQL")

    monkeypatch.setattr(connection_module.psycopg, "connect", fail_connect)
    importlib.reload(pgvector_store)


@pytest.mark.skipif(
    os.getenv("RUN_PGVECTOR_TESTS") != "1",
    reason="pgvector integration tests require RUN_PGVECTOR_TESTS=1 and a live database",
)
def test_pgvector_integration_ingest_and_search() -> None:
    with connect() as connection:
        initialize_schema(connection)
        counts = ingest_documents_to_pgvector(connection)
        results = search_pgvector(connection, "incident escalation approval", limit=3)

    assert counts["documents"] == 3
    assert counts["chunks"] > 0
    assert results
    assert results[0]["source_path"].startswith("datasets/sample_docs/")
