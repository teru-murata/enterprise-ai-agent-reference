from app.evals.retrieval_eval import (
    hit_at_k,
    load_eval_cases,
    passes_threshold,
    reciprocal_rank,
    run_retrieval_eval,
)


def test_load_eval_cases() -> None:
    cases = load_eval_cases()

    assert len(cases) == 3
    assert cases[0].case_id == "eval-001"
    assert cases[0].expected_documents == ["incident_response_policy.md"]


def test_hit_at_k() -> None:
    expected_documents = ["incident_response_policy.md"]
    retrieved_documents = ["customer_support_faq.md", "incident_response_policy.md"]

    assert hit_at_k(expected_documents, retrieved_documents, 1) is False
    assert hit_at_k(expected_documents, retrieved_documents, 2) is True


def test_reciprocal_rank() -> None:
    expected_documents = ["access_control_policy.md"]
    retrieved_documents = [
        "customer_support_faq.md",
        "incident_response_policy.md",
        "access_control_policy.md",
    ]

    assert reciprocal_rank(expected_documents, retrieved_documents) == 1 / 3
    assert reciprocal_rank(expected_documents, ["customer_support_faq.md"]) == 0.0


def test_run_retrieval_eval_on_synthetic_dataset() -> None:
    metrics = run_retrieval_eval()

    assert metrics["total_cases"] == 3
    assert metrics["hit_at_3"] == 1.0
    assert metrics["mean_reciprocal_rank"] > 0
    assert len(metrics["per_case"]) == 3


def test_threshold_pass_fail_behavior() -> None:
    assert passes_threshold({"hit_at_3": 1.0}) is True
    assert passes_threshold({"hit_at_3": 0.67}) is False

