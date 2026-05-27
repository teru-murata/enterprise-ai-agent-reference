from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agents.incident_support import run_incident_support_workflow
from app.answers.providers import compose_answer, get_answer_provider
from app.audit.events import (
    create_answer_draft_audit_event,
    create_audit_event,
    create_guardrail_audit_event,
    create_retrieval_audit_event,
)
from app.guardrails.input_checks import analyze_user_input
from app.rag.chunking import split_into_chunks
from app.rag.documents import load_sample_documents
from app.rag.modes import RETRIEVAL_MODE_LABELS, parse_retrieval_mode
from app.rag.pgvector_store import search_pgvector_from_database_url
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
    answer_provider: str = "deterministic"


class IncidentSupportRequest(BaseModel):
    message: str
    customer_id: str = "synthetic-customer-001"
    severity_hint: str | None = None
    tool_mode: str = "local"
    answer_provider: str = "deterministic"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return PROJECT_METADATA


@app.get("/rag/search")
def rag_search(query: str, mode: str = "keyword") -> dict[str, object]:
    if not query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")

    try:
        retrieval_mode = parse_retrieval_mode(mode)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

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

    if retrieval_mode == "keyword":
        documents = load_sample_documents()
        chunks = split_into_chunks(documents)
        results = retrieve_keyword_matches(query=query, chunks=chunks)
    else:
        try:
            results = search_pgvector_from_database_url(query=query)
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail=(
                    "pgvector retrieval is unavailable. Start the local PostgreSQL/pgvector "
                    "service and ingest sample documents before using mode=pgvector."
                ),
            ) from error

    retrieval_mode_label = RETRIEVAL_MODE_LABELS[retrieval_mode]
    audit_events = [
        guardrail_event,
        create_retrieval_audit_event(
            subject="rag_search",
            result_count=len(results),
            retrieval_mode=retrieval_mode_label,
        ),
    ]

    return {
        "query": query,
        "retrieval_mode": retrieval_mode_label,
        "count": len(results),
        "results": results,
        "guardrail_result": guardrail_result,
        "audit_events": audit_events,
    }


@app.post("/agent/incident-support")
def incident_support(request: IncidentSupportRequest) -> dict[str, object]:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")

    try:
        return run_incident_support_workflow(request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.post("/answers/draft")
def answer_draft(request: AnswerDraftRequest) -> dict[str, object]:
    question = request.question
    if not question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    try:
        answer_provider = get_answer_provider(request.answer_provider)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

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
            "answer_provider": answer_provider,
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
                        "answer_provider": answer_provider,
                    },
                ),
            ],
        }

    documents = load_sample_documents()
    chunks = split_into_chunks(documents)
    retrieved_chunks = retrieve_keyword_matches(query=question, chunks=chunks)
    try:
        draft = compose_answer(
            question=question,
            retrieved_chunks=retrieved_chunks,
            provider=answer_provider,
        )
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
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
            answer_provider=answer_provider,
            model_call=draft.get("model_call")
            if isinstance(draft.get("model_call"), dict)
            else None,
        ),
    ]

    return {
        "question": draft["question"],
        "retrieval_mode": "keyword-placeholder",
        "answer_provider": answer_provider,
        "answer": draft["answer"],
        "confidence": draft["confidence"],
        "citations": draft["citations"],
        "limitations": draft["limitations"],
        "requires_human_review": draft["requires_human_review"],
        "model_call": draft.get("model_call"),
        "retrieved_count": len(retrieved_chunks),
        "guardrail_result": guardrail_result,
        "audit_events": audit_events,
    }


