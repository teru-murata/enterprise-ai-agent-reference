from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    document_id: str
    source_path: str
    title: str
    text: str


def find_repository_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent

    for candidate in [current, *current.parents]:
        if (candidate / "datasets" / "sample_docs").is_dir():
            return candidate

    msg = "Could not locate repository root containing datasets/sample_docs"
    raise FileNotFoundError(msg)


def extract_title(markdown_text: str, fallback: str) -> str:
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.removeprefix("# ").strip()
    return fallback


def load_sample_documents() -> list[Document]:
    repo_root = find_repository_root()
    docs_dir = repo_root / "datasets" / "sample_docs"
    documents: list[Document] = []

    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        documents.append(
            Document(
                document_id=path.stem,
                source_path=path.relative_to(repo_root).as_posix(),
                title=extract_title(text, path.stem.replace("_", " ").title()),
                text=text,
            )
        )

    return documents

