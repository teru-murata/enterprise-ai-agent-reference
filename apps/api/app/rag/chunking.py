from __future__ import annotations

from dataclasses import dataclass

from app.rag.documents import Document


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    source_path: str
    title: str
    text: str


def split_into_chunks(documents: list[Document]) -> list[Chunk]:
    chunks: list[Chunk] = []

    for document in documents:
        sections = [section.strip() for section in document.text.split("\n\n") if section.strip()]
        for index, section in enumerate(sections, start=1):
            chunks.append(
                Chunk(
                    chunk_id=f"{document.document_id}:{index}",
                    document_id=document.document_id,
                    source_path=document.source_path,
                    title=document.title,
                    text=section,
                )
            )

    return chunks

