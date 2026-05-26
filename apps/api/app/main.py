from fastapi import FastAPI, HTTPException

from app.rag.chunking import split_into_chunks
from app.rag.documents import load_sample_documents
from app.rag.retrieval import retrieve_keyword_matches

PROJECT_METADATA = {
    "name": "enterprise-ai-agent-reference",
    "version": "0.1.0",
    "description": "Enterprise AI agent reference stack for incident support.",
}

app = FastAPI(
    title="Enterprise AI Agent Reference API",
    version=PROJECT_METADATA["version"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return PROJECT_METADATA


@app.get("/rag/search")
def rag_search(query: str) -> dict[str, object]:
    if not query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")

    documents = load_sample_documents()
    chunks = split_into_chunks(documents)
    results = retrieve_keyword_matches(query=query, chunks=chunks)

    return {
        "query": query,
        "retrieval_mode": "keyword-placeholder",
        "count": len(results),
        "results": results,
    }

