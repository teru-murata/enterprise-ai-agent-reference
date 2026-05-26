from __future__ import annotations

import re
from dataclasses import asdict

from app.rag.chunking import Chunk


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def retrieve_keyword_matches(query: str, chunks: list[Chunk], limit: int = 5) -> list[dict[str, object]]:
    query_terms = set(tokenize(query))
    if not query_terms:
        return []

    scored_results: list[dict[str, object]] = []
    for chunk in chunks:
        chunk_terms = tokenize(f"{chunk.title}\n{chunk.text}")
        score = sum(chunk_terms.count(term) for term in query_terms)
        if score == 0:
            continue

        result = asdict(chunk)
        result["score"] = score
        scored_results.append(result)

    return sorted(
        scored_results,
        key=lambda result: (-int(result["score"]), str(result["chunk_id"])),
    )[:limit]

