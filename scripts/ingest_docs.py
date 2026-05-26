from pathlib import Path


def main() -> None:
    docs_dir = Path(__file__).resolve().parents[1] / "datasets" / "sample_docs"
    documents = sorted(docs_dir.glob("*.md"))

    print(f"Discovered {len(documents)} synthetic documents:")
    for document in documents:
        print(f"- {document.name}")


if __name__ == "__main__":
    main()

