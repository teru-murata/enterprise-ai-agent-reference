from __future__ import annotations


def citation_from_chunk(chunk: dict[str, object]) -> dict[str, object]:
    return {
        "chunk_id": chunk["chunk_id"],
        "document_id": chunk["document_id"],
        "source_path": chunk["source_path"],
        "title": chunk["title"],
    }


def summarize_chunk_text(text: str, max_length: int = 220) -> str:
    normalized = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[: max_length - 3].rstrip()}..."


def determine_confidence(retrieved_chunks: list[dict[str, object]]) -> str:
    if not retrieved_chunks:
        return "low"

    top_score = int(retrieved_chunks[0].get("score", 0))
    if top_score >= 4:
        return "high"
    if top_score >= 2:
        return "medium"
    return "low"


def compose_grounded_answer(question: str, retrieved_chunks: list[dict[str, object]]) -> dict[str, object]:
    if not retrieved_chunks:
        return {
            "question": question,
            "answer": (
                "Insufficient evidence in the retrieved synthetic context to draft a grounded "
                "answer. Ask for more specific details or add an approved source document."
            ),
            "confidence": "low",
            "citations": [],
            "limitations": [
                "No retrieved chunks were available.",
                "No facts were inferred beyond the provided synthetic corpus.",
            ],
            "requires_human_review": True,
        }

    cited_chunks = retrieved_chunks[:3]
    citations = [citation_from_chunk(chunk) for chunk in cited_chunks]
    evidence_lines = []

    for index, chunk in enumerate(cited_chunks, start=1):
        title = str(chunk["title"])
        snippet = summarize_chunk_text(str(chunk["text"]))
        evidence_lines.append(f"{index}. {title}: {snippet}")

    answer = (
        "Draft generated from retrieved synthetic context. "
        "Relevant retrieved evidence: "
        + " ".join(evidence_lines)
    )

    return {
        "question": question,
        "answer": answer,
        "confidence": determine_confidence(retrieved_chunks),
        "citations": citations,
        "limitations": [
            "This is a deterministic draft from retrieved chunks, not an LLM-generated answer.",
            "It may be incomplete if the keyword retriever missed relevant context.",
            "Human review is required before use in an operational workflow.",
        ],
        "requires_human_review": True,
    }

