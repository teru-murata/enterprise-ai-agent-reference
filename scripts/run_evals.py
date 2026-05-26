import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_PATH = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_PATH))

from app.evals.answer_eval import passes_answer_thresholds, run_answer_eval  # noqa: E402
from app.evals.retrieval_eval import passes_threshold, run_retrieval_eval  # noqa: E402


def main() -> None:
    retrieval_metrics = run_retrieval_eval()
    answer_metrics = run_answer_eval()

    print("Retrieval evaluation")
    print(f"- total cases: {retrieval_metrics['total_cases']}")
    print(f"- answerable cases: {retrieval_metrics['answerable_cases']}")
    print(f"- insufficient-evidence cases: {retrieval_metrics['insufficient_evidence_cases']}")
    print(f"- hit@1: {float(retrieval_metrics['hit_at_1']):.3f}")
    print(f"- hit@3: {float(retrieval_metrics['hit_at_3']):.3f}")
    print(f"- MRR: {float(retrieval_metrics['mean_reciprocal_rank']):.3f}")
    print()

    print("Answer quality evaluation")
    print(f"- citation coverage: {float(answer_metrics['citation_coverage']):.3f}")
    print(f"- expected term coverage: {float(answer_metrics['expected_term_coverage']):.3f}")
    print(f"- human review rate: {float(answer_metrics['human_review_rate']):.3f}")
    print(
        "- insufficient evidence success rate: "
        f"{float(answer_metrics['insufficient_evidence_success_rate']):.3f}"
    )
    print(f"- groundedness proxy: {float(answer_metrics['groundedness_proxy']):.3f}")
    print()
    print("Retrieval per-case results:")

    for case in retrieval_metrics["per_case"]:
        status = "PASS" if (not case["answerable"] or case["hit_at_3"]) else "FAIL"
        expected = ", ".join(case["expected_documents"])
        retrieved = ", ".join(case["retrieved_documents"]) or "none"
        print(f"- {status} {case['id']} [{case['category']}]")
        print(f"  query: {case['query']}")
        print(f"  expected: {expected}")
        print(f"  retrieved: {retrieved}")
        print(f"  reciprocal_rank: {float(case['reciprocal_rank']):.3f}")

    print()
    print("Answer per-case results:")
    for case in answer_metrics["per_case"]:
        status = "PASS" if case["groundedness_proxy_pass"] else "FAIL"
        print(f"- {status} {case['id']} [{case['category']}]")
        print(f"  citation_pass: {case['citation_pass']}")
        print(f"  expected_term_coverage: {float(case['expected_term_coverage']):.3f}")
        print(f"  requires_human_review: {case['requires_human_review']}")
        print(f"  insufficient_evidence_pass: {case['insufficient_evidence_pass']}")
        print(f"  groundedness_proxy_pass: {case['groundedness_proxy_pass']}")

    if not passes_threshold(retrieval_metrics, hit_at_3_threshold=1.0):
        raise SystemExit("Retrieval eval failed: hit@3 below 1.000 threshold")

    if not passes_answer_thresholds(answer_metrics, expected_term_coverage_threshold=0.5):
        raise SystemExit("Answer eval failed: one or more quality thresholds were not met")


if __name__ == "__main__":
    main()
