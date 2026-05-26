import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_PATH = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_PATH))

from app.evals.retrieval_eval import passes_threshold, run_retrieval_eval  # noqa: E402


def main() -> None:
    metrics = run_retrieval_eval()

    print("Retrieval evaluation summary")
    print(f"- total cases: {metrics['total_cases']}")
    print(f"- hit@1: {float(metrics['hit_at_1']):.3f}")
    print(f"- hit@3: {float(metrics['hit_at_3']):.3f}")
    print(f"- MRR: {float(metrics['mean_reciprocal_rank']):.3f}")
    print()
    print("Answer-quality evaluation: planned, not active in M2.")
    print()
    print("Per-case results:")

    for case in metrics["per_case"]:
        status = "PASS" if case["hit_at_3"] else "FAIL"
        expected = ", ".join(case["expected_documents"])
        retrieved = ", ".join(case["retrieved_documents"]) or "none"
        print(f"- {status} {case['id']} [{case['category']}]")
        print(f"  query: {case['query']}")
        print(f"  expected: {expected}")
        print(f"  retrieved: {retrieved}")
        print(f"  reciprocal_rank: {float(case['reciprocal_rank']):.3f}")

    if not passes_threshold(metrics, hit_at_3_threshold=1.0):
        raise SystemExit("Retrieval eval failed: hit@3 below 1.000 threshold")


if __name__ == "__main__":
    main()
