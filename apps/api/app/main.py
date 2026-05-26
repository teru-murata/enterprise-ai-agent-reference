from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.answers.composer import compose_grounded_answer
from app.audit.events import (
    create_answer_draft_audit_event,
    create_audit_event,
    create_guardrail_audit_event,
    create_retrieval_audit_event,
)
from app.guardrails.input_checks import analyze_user_input
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

    guardrail_result = analyze_user_input(query)
    guardrail_event = create_guardrail_audit_event(
        subject="rag_search",
        guardrail_result=guardrail_result,
        text_length=len(query),
    )
    if not guardrail_result["allowed"]:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Query blocked by deterministic guardrail checks.",
                "guardrail_result": guardrail_result,
                "audit_events": [guardrail_event],
            },
        )

    documents = load_sample_documents()
    chunks = split_into_chunks(documents)
    results = retrieve_keyword_matches(query=query, chunks=chunks)
    audit_events = [
        guardrail_event,
        create_retrieval_audit_event(
            subject="rag_search",
            result_count=len(results),
            retrieval_mode="keyword-placeholder",
        ),
    ]

    return {
        "query": query,
        "retrieval_mode": "keyword-placeholder",
        "count": len(results),
        "results": results,
        "guardrail_result": guardrail_result,
        "audit_events": audit_events,
    }


@app.post("/answers/draft")
def answer_draft(request: AnswerDraftRequest) -> dict[str, object]:
    question = request.question
    if not question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    guardrail_result = analyze_user_input(question)
    guardrail_event = create_guardrail_audit_event(
        subject="answer_draft",
        guardrail_result=guardrail_result,
        text_length=len(question),
    )
    if not guardrail_result["allowed"]:
        return {
            "question": question,
            "retrieval_mode": "keyword-placeholder",
            "answer": "Safety response: the question was blocked by deterministic guardrail checks.",
            "confidence": "low",
            "citations": [],
            "limitations": [
                "Guardrail checks flagged high-risk input.",
                "No retrieval or normal answer composition was performed.",
                "Human review is required before any follow-up action.",
            ],
            "requires_human_review": True,
            "retrieved_count": 0,
            "guardrail_result": guardrail_result,
            "audit_events": [
                guardrail_event,
                create_audit_event(
                    event_type="answer_draft",
                    status="blocked",
                    subject="answer_draft",
                    metadata={
                        "question_length": len(question),
                        "risk_level": guardrail_result["risk_level"],
                        "flags": guardrail_result["flags"],
                        "requires_human_review": True,
                    },
                ),
            ],
        }

    documents = load_sample_documents()
    chunks = split_into_chunks(documents)
    retrieved_chunks = retrieve_keyword_matches(query=question, chunks=chunks)
    draft = compose_grounded_answer(question=question, retrieved_chunks=retrieved_chunks)
    audit_events = [
        guardrail_event,
        create_retrieval_audit_event(
            subject="answer_draft",
            result_count=len(retrieved_chunks),
            retrieval_mode="keyword-placeholder",
        ),
        create_answer_draft_audit_event(
            subject="answer_draft",
            retrieved_count=len(retrieved_chunks),
            citation_count=len(draft["citations"]),
            requires_human_review=bool(draft["requires_human_review"]),
        ),
    ]

    return {
        "question": draft["question"],
        "retrieval_mode": "keyword-placeholder",
        "answer": draft["answer"],
        "confidence": draft["confidence"],
        "citations": draft["citations"],
        "limitations": draft["limitations"],
        "requires_human_review": draft["requires_human_review"],
        "retrieved_count": len(retrieved_chunks),
        "guardrail_result": guardrail_result,
        "audit_events": audit_events,
    }


