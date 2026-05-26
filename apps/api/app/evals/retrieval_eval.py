from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.rag.chunking import split_into_chunks
from app.rag.documents import find_repository_root, load_sample_documents
from app.rag.retrieval import retrieve_keyword_matches


@dataclass(frozen=True)
class RetrievalEvalCase:
    case_id: str
    query: str
    expected_documents: list[str]
    expected_terms: list[str]
    expected_answer_terms: list[str]
    requires_citations: bool
    expects_insufficient_evidence: bool
    category: str
    notes: str


def load_eval_cases(path: Path | None = None) -> list[RetrievalEvalCase]:
    eval_path = path or find_repository_root() / "datasets" / "golden_eval_set.jsonl"
    cases: list[RetrievalEvalCase] = []

    with eval_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            raw_case = json.loads(line)
            try:
                cases.append(
                    RetrievalEvalCase(
                        case_id=raw_case["id"],
                        query=raw_case["query"],
                        expected_documents=list(raw_case["expected_documents"]),
                        expected_terms=list(raw_case.get("expected_terms", [])),
                        expected_answer_terms=list(raw_case.get("expected_answer_terms", [])),
                        requires_citations=bool(raw_case.get("requires_citations", True)),
                        expects_insufficient_evidence=bool(
                            raw_case.get("expects_insufficient_evidence", False)
                        ),
                        category=raw_case["category"],
                        notes=raw_case.get("notes", ""),
                    )
                )
            except KeyError as error:
                missing_field = error.args[0]
                msg = f"Missing required field {missing_field!r} in eval case line {line_number}"
                raise ValueError(msg) from error

    return cases


def result_document_name(result: dict[str, object]) -> str:
    return Path(str(result["source_path"])).name


def reciprocal_rank(expected_documents: list[str], retrieved_documents: list[str]) -> float:
    expected = set(expected_documents)
    for index, document_name in enumerate(retrieved_documents, start=1):
        if document_name in expected:
            return 1.0 / index
    return 0.0


def hit_at_k(expected_documents: list[str], retrieved_documents: list[str], k: int) -> bool:
    expected = set(expected_documents)
    return any(document_name in expected for document_name in retrieved_documents[:k])


def run_retrieval_eval(top_k: int = 3) -> dict[str, object]:
    cases = load_eval_cases()
    documents = load_sample_documents()
    chunks = split_into_chunks(documents)

    per_case: list[dict[str, object]] = []
    answerable_cases = 0
    insufficient_evidence_cases = 0
    hit_at_1_count = 0
    hit_at_3_count = 0
    reciprocal_rank_total = 0.0

    for case in cases:
        results = retrieve_keyword_matches(case.query, chunks, limit=max(top_k, 3))
        retrieved_documents = [result_document_name(result) for result in results]
        is_answerable = bool(case.expected_documents)
        case_hit_at_1 = hit_at_k(case.expected_documents, retrieved_documents, 1) if is_answerable else False
        case_hit_at_3 = hit_at_k(case.expected_documents, retrieved_documents, 3) if is_answerable else False
        case_reciprocal_rank = (
            reciprocal_rank(case.expected_documents, retrieved_documents) if is_answerable else 0.0
        )

        if is_answerable:
            answerable_cases += 1
            hit_at_1_count += int(case_hit_at_1)
            hit_at_3_count += int(case_hit_at_3)
            reciprocal_rank_total += case_reciprocal_rank
        else:
            insufficient_evidence_cases += 1

        per_case.append(
            {
                "id": case.case_id,
                "query": case.query,
                "category": case.category,
                "expected_documents": case.expected_documents,
                "answerable": is_answerable,
                "retrieved_documents": retrieved_documents,
                "hit_at_1": case_hit_at_1,
                "hit_at_3": case_hit_at_3,
                "reciprocal_rank": case_reciprocal_rank,
                "top_results": results,
            }
        )

    total_cases = len(cases)
    if total_cases == 0:
        return {
            "total_cases": 0,
            "answerable_cases": 0,
            "insufficient_evidence_cases": 0,
            "hit_at_1": 0.0,
            "hit_at_3": 0.0,
            "mean_reciprocal_rank": 0.0,
            "per_case": [],
        }

    return {
        "total_cases": total_cases,
        "answerable_cases": answerable_cases,
        "insufficient_evidence_cases": insufficient_evidence_cases,
        "hit_at_1": hit_at_1_count / answerable_cases if answerable_cases else 0.0,
        "hit_at_3": hit_at_3_count / answerable_cases if answerable_cases else 0.0,
        "mean_reciprocal_rank": reciprocal_rank_total / answerable_cases
        if answerable_cases
        else 0.0,
        "per_case": per_case,
    }


def passes_threshold(metrics: dict[str, object], hit_at_3_threshold: float = 1.0) -> bool:
    return float(metrics["hit_at_3"]) >= hit_at_3_threshold
