from __future__ import annotations

import os
from typing import Literal

from app.answers.composer import citation_from_chunk, compose_grounded_answer
from app.answers.prompting import build_grounded_answer_prompt
from app.observability.model_calls import (
    create_model_call_record,
    create_skipped_model_call_record,
    elapsed_ms,
    extract_request_id,
    extract_response_id,
    extract_service_tier,
    extract_usage_from_openai_response,
    now_utc_iso,
    start_timer,
)


AnswerProvider = Literal["deterministic", "openai"]
DEFAULT_OPENAI_TEXT_MODEL = "gpt-5.2"
DEFAULT_OPENAI_REASONING_EFFORT = "low"


def get_answer_provider(provider: str | None = None) -> AnswerProvider:
    selected = (provider or os.getenv("ANSWER_PROVIDER", "deterministic")).strip().lower()
    if selected == "deterministic":
        return "deterministic"
    if selected == "openai":
        return "openai"

    msg = "Unsupported answer provider. Expected 'deterministic' or 'openai'."
    raise ValueError(msg)


def compose_answer_deterministic(
    question: str,
    retrieved_chunks: list[dict[str, object]],
) -> dict[str, object]:
    draft = compose_grounded_answer(question, retrieved_chunks)
    draft["answer_provider"] = "deterministic"
    draft["model_call"] = create_skipped_model_call_record(
        provider="local",
        operation="answers.deterministic",
        model="deterministic-composer",
        metadata={
            "answer_provider": "deterministic",
            "question_length": len(question),
            "retrieved_count": len(retrieved_chunks),
            "citation_count": len(draft["citations"]),
        },
    )
    return draft


def extract_response_text(response: object) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str):
        return output_text.strip()
    return ""


def compose_answer_openai(
    question: str,
    retrieved_chunks: list[dict[str, object]],
) -> dict[str, object]:
    if not retrieved_chunks:
        draft = compose_answer_deterministic(question, retrieved_chunks)
        draft["answer_provider"] = "openai"
        draft["limitations"].append("OpenAI was not called because no retrieved context was available.")
        draft["model_call"] = create_skipped_model_call_record(
            provider="openai",
            operation="responses.answer",
            model=os.getenv("OPENAI_TEXT_MODEL", DEFAULT_OPENAI_TEXT_MODEL),
            metadata={
                "answer_provider": "openai",
                "question_length": len(question),
                "retrieved_count": 0,
                "citation_count": 0,
            },
        )
        return draft

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required when ANSWER_PROVIDER=openai")

    model = os.getenv("OPENAI_TEXT_MODEL", DEFAULT_OPENAI_TEXT_MODEL)
    reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT", DEFAULT_OPENAI_REASONING_EFFORT)
    prompt = build_grounded_answer_prompt(question, retrieved_chunks)

    from openai import OpenAI

    client = OpenAI()
    started_at = start_timer()
    started_at_utc = now_utc_iso()
    try:
        response = client.responses.create(
            model=model,
            input=prompt,
            reasoning={"effort": reasoning_effort},
        )
        status = "succeeded"
    except Exception:
        completed_at_utc = now_utc_iso()
        model_call = create_model_call_record(
            provider="openai",
            operation="responses.answer",
            model=model,
            started_at_utc=started_at_utc,
            completed_at_utc=completed_at_utc,
            latency_ms=elapsed_ms(started_at),
            status="failed",
            metadata={
                "answer_provider": "openai",
                "question_length": len(question),
                "retrieved_count": len(retrieved_chunks),
            },
        )
        raise RuntimeError(
            "OpenAI answer generation failed; no raw prompt or output was logged. "
            f"model_call_id={model_call['call_id']}"
        ) from None
    completed_at_utc = now_utc_iso()
    usage = extract_usage_from_openai_response(response)
    citations = [citation_from_chunk(chunk) for chunk in retrieved_chunks[:3]]
    model_call = create_model_call_record(
        provider="openai",
        operation="responses.answer",
        model=model,
        started_at_utc=started_at_utc,
        completed_at_utc=completed_at_utc,
        latency_ms=elapsed_ms(started_at),
        status=status,
        usage=usage,
        service_tier=extract_service_tier(response),
        metadata={
            "answer_provider": "openai",
            "question_length": len(question),
            "retrieved_count": len(retrieved_chunks),
            "citation_count": len(citations),
            "response_id": extract_response_id(response),
            "request_id": extract_request_id(response),
            "service_tier": extract_service_tier(response),
        },
    )
    answer_text = extract_response_text(response)
    if not answer_text:
        answer_text = (
            "Insufficient evidence in the retrieved synthetic context to draft a grounded answer."
        )

    limitations = [
        "This draft was generated by the OpenAI Responses API from retrieved synthetic context.",
        "Citations are assigned from retrieved chunks by the application, not invented by the model.",
        "Human review is required before use in an operational workflow.",
    ]
    if "insufficient evidence" in answer_text.lower():
        limitations.append("The model indicated the retrieved context may be insufficient.")
    if usage["total_tokens"] is None:
        limitations.append("Token usage was not returned by the provider response.")
    if model_call["estimated_cost_usd"] is None:
        limitations.append("Cost estimate is not configured.")

    return {
        "question": question,
        "answer": answer_text,
        "confidence": "medium" if citations else "low",
        "citations": citations,
        "limitations": limitations,
        "requires_human_review": True,
        "answer_provider": "openai",
        "model_call": model_call,
    }


def compose_answer(
    question: str,
    retrieved_chunks: list[dict[str, object]],
    provider: str | None = None,
) -> dict[str, object]:
    selected_provider = get_answer_provider(provider)
    if selected_provider == "deterministic":
        return compose_answer_deterministic(question, retrieved_chunks)
    return compose_answer_openai(question, retrieved_chunks)
