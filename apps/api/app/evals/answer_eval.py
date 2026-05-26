from __future__ import annotations

from pathlib import Path

from app.answers.composer import compose_grounded_answer
from app.evals.retrieval_eval import RetrievalEvalCase, load_eval_cases
from app.rag.chunking import split_into_chunks
from app.rag.documents import load_sample_documents
from app.rag.retrieval import retrieve_keyword_matches, tokenize


def document_name_from_citation(citation: dict[str, object]) -> str:
    return Path(str(citation["source_path"])).name


def has_expected_citation(citations: list[dict[str, object]], expected_documents: list[str]) -> bool:
    if not expected_documents:
        return not citations
    cited_documents = {document_name_from_citation(citation) for citation in citations}
    return bool(cited_documents.intersection(expected_documents))


def expected_term_coverage(answer: str, expected_terms: list[str]) -> float:
    if not expected_terms:
        return 1.0
    answer_terms = set(tokenize(answer))
    matched_terms = sum(1 for term in expected_terms if term.lower() in answer_terms)
    return matched_terms / len(expected_terms)


def indicates_insufficient_evidence(draft: dict[str, object]) -> bool:
    answer = str(draft["answer"]).lower()
    return (
        "insufficient evidence" in answer
        and draft["confidence"] == "low"
        and draft["citations"] == []
    )


def groundedness_proxy_pass(
    draft: dict[str, object],
    retrieved_chunks: list[dict[str, object]],
    expected_terms: list[str],
) -> bool:
    if not draft["citations"] or not retrieved_chunks:
        return False

    answer_terms = set(tokenize(str(draft["answer"])))
    retrieved_terms = set()
    for chunk in retrieved_chunks:
        retrieved_terms.update(tokenize(str(chunk["text"])))

    connected_terms = answer_terms.intersection(retrieved_terms)
    expected_overlap = {term.lower() for term in expected_terms}.intersection(answer_terms)
    return bool(connected_terms) and bool(expected_overlap)


def evaluate_answer_case(
    case: RetrievalEvalCase,
    retrieved_chunks: list[dict[str, object]],
    draft: dict[str, object],
) -> dict[str, object]:
    answerable = bool(case.expected_documents)
    citations = list(draft["citations"])

    citation_pass = True
    if answerable and case.requires_citations:
        citation_pass = has_expected_citation(citations, case.expected_documents)

    term_coverage = (
        expected_term_coverage(str(draft["answer"]), case.expected_answer_terms)
        if answerable
        else 1.0
    )
    insufficient_evidence_pass = (
        indicates_insufficient_evidence(draft) if case.expects_insufficient_evidence else True
    )
    groundedness_pass = (
        groundedness_proxy_pass(draft, retrieved_chunks, case.expected_answer_terms)
        if answerable
        else insufficient_evidence_pass
    )

    return {
        "id": case.case_id,
        "query": case.query,
        "category": case.category,
        "answerable": answerable,
        "expected_documents": case.expected_documents,
        "expected_answer_terms": case.expected_answer_terms,
        "citation_pass": citation_pass,
        "expected_term_coverage": term_coverage,
        "requires_human_review": bool(draft["requires_human_review"]),
        "insufficient_evidence_pass": insufficient_evidence_pass,
        "groundedness_proxy_pass": groundedness_pass,
        "confidence": draft["confidence"],
        "citation_documents": [document_name_from_citation(citation) for citation in citations],
    }


def run_answer_eval() -> dict[str, object]:
    cases = load_eval_cases()
    documents = load_sample_documents()
    chunks = split_into_chunks(documents)

    per_case: list[dict[str, object]] = []
    citation_passes = 0
    citation_required_cases = 0
    term_coverage_total = 0.0
    answerable_cases = 0
    human_review_count = 0
    insufficient_evidence_cases = 0
    insufficient_evidence_passes = 0
    groundedness_passes = 0

    for case in cases:
        retrieved_chunks = retrieve_keyword_matches(case.query, chunks)
        draft = compose_grounded_answer(case.query, retrieved_chunks)
        case_result = evaluate_answer_case(case, retrieved_chunks, draft)
        per_case.append(case_result)

        human_review_count += int(case_result["requires_human_review"])

        if case_result["answerable"]:
            answerable_cases += 1
            term_coverage_total += float(case_result["expected_term_coverage"])
            groundedness_passes += int(case_result["groundedness_proxy_pass"])
            if case.requires_citations:
                citation_required_cases += 1
                citation_passes += int(case_result["citation_pass"])

        if case.expects_insufficient_evidence:
            insufficient_evidence_cases += 1
            insufficient_evidence_passes += int(case_result["insufficient_evidence_pass"])

    total_cases = len(cases)
    return {
        "total_cases": total_cases,
        "answerable_cases": answerable_cases,
        "insufficient_evidence_cases": insufficient_evidence_cases,
        "citation_coverage": citation_passes / citation_required_cases
        if citation_required_cases
        else 1.0,
        "expected_term_coverage": term_coverage_total / answerable_cases
        if answerable_cases
        else 1.0,
        "human_review_rate": human_review_count / total_cases if total_cases else 0.0,
        "insufficient_evidence_success_rate": (
            insufficient_evidence_passes / insufficient_evidence_cases
            if insufficient_evidence_cases
            else 1.0
        ),
        "groundedness_proxy": groundedness_passes / answerable_cases if answerable_cases else 1.0,
        "per_case": per_case,
    }


def passes_answer_thresholds(
    metrics: dict[str, object],
    expected_term_coverage_threshold: float = 0.5,
) -> bool:
    return (
        float(metrics["human_review_rate"]) == 1.0
        and float(metrics["citation_coverage"]) == 1.0
        and float(metrics["insufficient_evidence_success_rate"]) == 1.0
        and float(metrics["expected_term_coverage"]) >= expected_term_coverage_threshold
    )

