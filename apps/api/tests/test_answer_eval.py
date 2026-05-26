from app.evals.answer_eval import (
    evaluate_answer_case,
    expected_term_coverage,
    has_expected_citation,
    indicates_insufficient_evidence,
    passes_answer_thresholds,
    run_answer_eval,
)
from app.evals.retrieval_eval import RetrievalEvalCase, load_eval_cases


def test_load_answer_eval_cases() -> None:
    cases = load_eval_cases()

    assert len(cases) == 4
    assert cases[0].expected_answer_terms
    assert cases[-1].expects_insufficient_evidence is True


def test_citation_coverage_pass_fail() -> None:
    citations = [
        {
            "chunk_id": "incident_response_policy:1",
            "document_id": "incident_response_policy",
            "source_path": "datasets/sample_docs/incident_response_policy.md",
            "title": "Incident Response Policy",
        }
    ]

    assert has_expected_citation(citations, ["incident_response_policy.md"]) is True
    assert has_expected_citation(citations, ["access_control_policy.md"]) is False


def test_expected_term_coverage_calculation() -> None:
    answer = "Severity 2 incident guidance requires support leadership notification."

    assert expected_term_coverage(answer, ["severity", "incident", "leadership"]) == 1.0
    assert expected_term_coverage(answer, ["severity", "missing"]) == 0.5
    assert expected_term_coverage(answer, []) == 1.0


def test_human_review_enforcement_in_case_result() -> None:
    case = RetrievalEvalCase(
        case_id="unit",
        query="incident",
        expected_documents=["incident_response_policy.md"],
        expected_terms=["incident"],
        expected_answer_terms=["incident"],
        requires_citations=True,
        expects_insufficient_evidence=False,
        category="unit",
        notes="unit",
    )
    draft = {
        "answer": "Draft generated from retrieved synthetic context. incident",
        "confidence": "medium",
        "citations": [
            {
                "chunk_id": "incident_response_policy:1",
                "document_id": "incident_response_policy",
                "source_path": "datasets/sample_docs/incident_response_policy.md",
                "title": "Incident Response Policy",
            }
        ],
        "requires_human_review": True,
    }
    result = evaluate_answer_case(case, [{"text": "incident"}], draft)

    assert result["requires_human_review"] is True


def test_insufficient_evidence_case_handling() -> None:
    draft = {
        "answer": "Insufficient evidence in the retrieved synthetic context.",
        "confidence": "low",
        "citations": [],
        "requires_human_review": True,
    }

    assert indicates_insufficient_evidence(draft) is True


def test_full_answer_eval_run_on_synthetic_dataset() -> None:
    metrics = run_answer_eval()

    assert metrics["total_cases"] == 4
    assert metrics["answerable_cases"] == 3
    assert metrics["insufficient_evidence_cases"] == 1
    assert metrics["human_review_rate"] == 1.0
    assert metrics["citation_coverage"] == 1.0
    assert metrics["insufficient_evidence_success_rate"] == 1.0
    assert metrics["expected_term_coverage"] >= 0.5


def test_answer_threshold_behavior() -> None:
    passing_metrics = {
        "human_review_rate": 1.0,
        "citation_coverage": 1.0,
        "insufficient_evidence_success_rate": 1.0,
        "expected_term_coverage": 0.75,
    }
    failing_metrics = {**passing_metrics, "expected_term_coverage": 0.25}

    assert passes_answer_thresholds(passing_metrics) is True
    assert passes_answer_thresholds(failing_metrics) is False

