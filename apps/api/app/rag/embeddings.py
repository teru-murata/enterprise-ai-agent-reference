from __future__ import annotations

import hashlib
import math
import re


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
        direction = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += direction

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector

    return [round(value / norm, 6) for value in vector]
