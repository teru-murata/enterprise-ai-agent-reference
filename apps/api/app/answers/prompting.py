from __future__ import annotations

from app.answers.composer import summarize_chunk_text

SENSITIVE_MARKERS = ("api key", "password", "secret token", "private key")


def redact_sensitive_markers(text: str) -> str:
    redacted = text
    for marker in SENSITIVE_MARKERS:
        redacted = redacted.replace(marker, "[REDACTED]")
        redacted = redacted.replace(marker.title(), "[REDACTED]")
        redacted = redacted.replace(marker.upper(), "[REDACTED]")
    return redacted


def build_grounded_answer_prompt(
    question: str,
    retrieved_chunks: list[dict[str, object]],
    max_chunks: int = 3,
) -> str:
    context_blocks = []
    for chunk in retrieved_chunks[:max_chunks]:
        citation_id = str(chunk["chunk_id"])
        title = redact_sensitive_markers(str(chunk["title"]))
        source_path = redact_sensitive_markers(str(chunk["source_path"]))
        text = redact_sensitive_markers(summarize_chunk_text(str(chunk["text"]), max_length=700))
        context_blocks.append(
            "\n".join(
                [
                    f"Citation ID: {citation_id}",
                    f"Title: {title}",
                    f"Source: {source_path}",
                    f"Context: {text}",
                ]
            )
        )

    context = "\n\n".join(context_blocks) or "No retrieved context was provided."
    return "\n".join(
        [
            "You are drafting an internal incident-support answer from synthetic retrieved context.",
            "Answer only from the provided context.",
            "Do not invent facts, policies, systems, people, secrets, or customer data.",
            "If the context is insufficient, say that evidence is insufficient.",
            "Keep the answer concise.",
            "Every draft requires human review before operational use.",
            "Use the provided citation identifiers when referring to evidence.",
            "",
            f"Question: {redact_sensitive_markers(question)}",
            "",
            "Retrieved context:",
            context,
        ]
    )
