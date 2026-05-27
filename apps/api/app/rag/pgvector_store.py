from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Protocol

from psycopg import Connection

from app.db.connection import connect
from app.rag.chunking import split_into_chunks
from app.rag.documents import find_repository_root, load_sample_documents
from app.rag.embeddings import embed_text

EMBEDDING_DIMENSIONS = 16


class SupportsExecute(Protocol):
    def execute(self, query: str, params: object | None = None) -> object:
        ...


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.6f}" for value in values) + "]"


def schema_path() -> Path:
    return find_repository_root() / "apps" / "api" / "app" / "db" / "schema.sql"


def initialize_schema(connection: Connection) -> None:
    for statement in schema_path().read_text(encoding="utf-8").split(";"):
        if statement.strip():
            connection.execute(statement)
    connection.commit()


def initialize_schema_from_database_url(database_url: str | None = None) -> None:
    with connect(database_url) as connection:
        initialize_schema(connection)


def upsert_document(cursor: SupportsExecute, document: object) -> None:
    cursor.execute(
        """
        INSERT INTO documents (document_id, source_path, title, text)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (document_id) DO UPDATE SET
            source_path = EXCLUDED.source_path,
            title = EXCLUDED.title,
            text = EXCLUDED.text
        """,
        (
            getattr(document, "document_id"),
            getattr(document, "source_path"),
            getattr(document, "title"),
            getattr(document, "text"),
        ),
    )


def validate_embedding_dimensions(embedding: list[float]) -> None:
    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Embedding dimension mismatch. pgvector schema expects {EMBEDDING_DIMENSIONS}, "
            f"received {len(embedding)}."
        )


def upsert_chunk(
    cursor: SupportsExecute,
    chunk: object,
    embedding_provider: str | None = None,
) -> None:
    embedding = embed_text(
        f"{getattr(chunk, 'title')}\n{getattr(chunk, 'text')}",
        provider=embedding_provider,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    validate_embedding_dimensions(embedding)
    cursor.execute(
        """
        INSERT INTO document_chunks (chunk_id, document_id, source_path, title, text, embedding)
        VALUES (%s, %s, %s, %s, %s, %s::vector)
        ON CONFLICT (chunk_id) DO UPDATE SET
            document_id = EXCLUDED.document_id,
            source_path = EXCLUDED.source_path,
            title = EXCLUDED.title,
            text = EXCLUDED.text,
            embedding = EXCLUDED.embedding
        """,
        (
            getattr(chunk, "chunk_id"),
            getattr(chunk, "document_id"),
            getattr(chunk, "source_path"),
            getattr(chunk, "title"),
            getattr(chunk, "text"),
            vector_literal(embedding),
        ),
    )


def ingest_documents_to_pgvector(
    connection: Connection,
    embedding_provider: str | None = None,
) -> dict[str, int]:
    documents = load_sample_documents()
    chunks = split_into_chunks(documents)

    with connection.cursor() as cursor:
        for document in documents:
            upsert_document(cursor, document)
        for chunk in chunks:
            upsert_chunk(cursor, chunk, embedding_provider=embedding_provider)
    connection.commit()

    return {"documents": len(documents), "chunks": len(chunks)}


def ingest_documents_to_pgvector_from_database_url(
    database_url: str | None = None,
    embedding_provider: str | None = None,
) -> dict[str, int]:
    with connect(database_url) as connection:
        initialize_schema(connection)
        return ingest_documents_to_pgvector(connection, embedding_provider=embedding_provider)


def search_pgvector(
    connection: Connection,
    query: str,
    limit: int = 5,
    embedding_provider: str | None = None,
) -> list[dict[str, object]]:
    embedding = embed_text(query, provider=embedding_provider, dimensions=EMBEDDING_DIMENSIONS)
    validate_embedding_dimensions(embedding)
    query_embedding = vector_literal(embedding)
    rows = connection.execute(
        """
        SELECT
            chunk_id,
            document_id,
            source_path,
            title,
            text,
            1 - (embedding <=> %s::vector) AS score
        FROM document_chunks
        ORDER BY embedding <=> %s::vector, chunk_id
        LIMIT %s
        """,
        (query_embedding, query_embedding, limit),
    ).fetchall()

    results: list[dict[str, object]] = []
    for row in rows:
        result = {
            "chunk_id": row[0],
            "document_id": row[1],
            "source_path": row[2],
            "title": row[3],
            "text": row[4],
            "score": float(row[5]),
        }
        results.append(result)

    return results


def search_pgvector_from_database_url(
    query: str,
    limit: int = 5,
    database_url: str | None = None,
    embedding_provider: str | None = None,
) -> list[dict[str, object]]:
    with connect(database_url) as connection:
        return search_pgvector(
            connection=connection,
            query=query,
            limit=limit,
            embedding_provider=embedding_provider,
        )


def chunk_to_result(chunk: object, score: float) -> dict[str, object]:
    result = asdict(chunk)
    result["score"] = score
    return result
