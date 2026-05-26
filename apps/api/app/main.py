from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.answers.composer import compose_grounded_answer
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


class AnswerDraftRequest(BaseModel):
    question: str


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


@app.post("/answers/draft")
def answer_draft(request: AnswerDraftRequest) -> dict[str, object]:
    question = request.question
    if not question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    documents = load_sample_documents()
    chunks = split_into_chunks(documents)
    retrieved_chunks = retrieve_keyword_matches(query=question, chunks=chunks)
    draft = compose_grounded_answer(question=question, retrieved_chunks=retrieved_chunks)

    return {
        "question": draft["question"],
        "retrieval_mode": "keyword-placeholder",
        "answer": draft["answer"],
        "confidence": draft["confidence"],
        "citations": draft["citations"],
        "limitations": draft["limitations"],
        "requires_human_review": draft["requires_human_review"],
        "retrieved_count": len(retrieved_chunks),
    }


