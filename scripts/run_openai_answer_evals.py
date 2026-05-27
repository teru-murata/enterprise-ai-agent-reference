import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_PATH = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_PATH))

from app.answers.providers import compose_answer  # noqa: E402
from app.evals.answer_eval import evaluate_answer_case  # noqa: E402
from app.evals.retrieval_eval import load_eval_cases  # noqa: E402
from app.rag.chunking import split_into_chunks  # noqa: E402
from app.rag.documents import load_sample_documents  # noqa: E402
from app.rag.retrieval import retrieve_keyword_matches  # noqa: E402


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required for OpenAI answer evals")

    os.environ["ANSWER_PROVIDER"] = "openai"
    os.environ.setdefault("OPENAI_TEXT_MODEL", "gpt-5.2")
    os.environ.setdefault("OPENAI_REASONING_EFFORT", "low")

    cases = load_eval_cases()
    chunks = split_into_chunks(load_sample_documents())
    per_case: list[dict[str, object]] = []
    citation_required_cases = 0
    citation_passes = 0
    human_review_count = 0
    insufficient_evidence_cases = 0
    insufficient_evidence_passes = 0
    expected_term_coverage_total = 0.0
    answerable_cases = 0
    groundedness_passes = 0

    for case in cases:
        retrieved_chunks = retrieve_keyword_matches(case.query, chunks)
        draft = compose_answer(case.query, retrieved_chunks, provider="openai")
        result = evaluate_answer_case(case, retrieved_chunks, draft)
        per_case.append(result)

        human_review_count += int(result["requires_human_review"])
        if result["answerable"]:
            answerable_cases += 1
            expected_term_coverage_total += float(result["expected_term_coverage"])
            groundedness_passes += int(result["groundedness_proxy_pass"])
            if case.requires_citations:
                citation_required_cases += 1
                citation_passes += int(result["citation_pass"])
        if case.expects_insufficient_evidence:
            insufficient_evidence_cases += 1
            insufficient_evidence_passes += int(result["insufficient_evidence_pass"])

    total_cases = len(cases)
    citation_coverage = (
        citation_passes / citation_required_cases if citation_required_cases else 1.0
    )
    human_review_rate = human_review_count / total_cases if total_cases else 0.0
    insufficient_evidence_success_rate = (
        insufficient_evidence_passes / insufficient_evidence_cases
        if insufficient_evidence_cases
        else 1.0
    )
    expected_term_coverage = (
        expected_term_coverage_total / answerable_cases if answerable_cases else 1.0
    )
    groundedness_proxy = groundedness_passes / answerable_cases if answerable_cases else 1.0

    print("OpenAI answer evaluation")
    print(f"- total cases: {total_cases}")
    print(f"- answerable cases: {answerable_cases}")
    print(f"- citation coverage: {citation_coverage:.3f}")
    print(f"- human review rate: {human_review_rate:.3f}")
    print(f"- insufficient evidence success rate: {insufficient_evidence_success_rate:.3f}")
    print(f"- expected term coverage: {expected_term_coverage:.3f}")
    print(f"- groundedness proxy: {groundedness_proxy:.3f}")
    print()

    for result in per_case:
        status = "PASS" if result["citation_pass"] and result["requires_human_review"] else "FAIL"
        print(f"- {status} {result['id']} [{result['category']}]")
        print(f"  citation_pass: {result['citation_pass']}")
        print(f"  requires_human_review: {result['requires_human_review']}")
        print(f"  insufficient_evidence_pass: {result['insufficient_evidence_pass']}")
        print(f"  expected_term_coverage: {float(result['expected_term_coverage']):.3f}")

    if human_review_rate < 1.0:
        raise SystemExit("OpenAI answer eval failed: human_review_rate below 1.0")
    if citation_coverage < 1.0:
        raise SystemExit("OpenAI answer eval failed: citation_coverage below 1.0")
    if insufficient_evidence_success_rate < 1.0:
        raise SystemExit(
            "OpenAI answer eval failed: insufficient_evidence_success_rate below 1.0"
        )


if __name__ == "__main__":
    main()
