import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_PATH = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_PATH))

from app.evals.answer_eval import passes_answer_thresholds, run_answer_eval  # noqa: E402
from app.evals.retrieval_eval import passes_threshold, run_retrieval_eval  # noqa: E402
from app.evals.workflow_eval import passes_workflow_thresholds, run_workflow_eval  # noqa: E402


def main() -> None:
    retrieval_metrics = run_retrieval_eval()
    answer_metrics = run_answer_eval()
    workflow_metrics = run_workflow_eval()

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

    print("Workflow and tool-call safety evaluation")
    print(f"- total cases: {workflow_metrics['total_cases']}")
    print(f"- drafted cases: {workflow_metrics['drafted_cases']}")
    print(f"- blocked cases: {workflow_metrics['blocked_cases']}")
    print(f"- classification accuracy: {float(workflow_metrics['classification_accuracy']):.3f}")
    print(f"- severity accuracy: {float(workflow_metrics['severity_accuracy']):.3f}")
    print(
        "- approval enforcement rate: "
        f"{float(workflow_metrics['approval_enforcement_rate']):.3f}"
    )
    print(
        "- blocked no-tool-call rate: "
        f"{float(workflow_metrics['blocked_no_tool_call_rate']):.3f}"
    )
    print(
        "- draft action safety rate: "
        f"{float(workflow_metrics['draft_action_safety_rate']):.3f}"
    )
    print(
        "- audit completeness rate: "
        f"{float(workflow_metrics['audit_completeness_rate']):.3f}"
    )
    print(f"- expected tool coverage: {float(workflow_metrics['expected_tool_coverage']):.3f}")
    print(
        "- synthetic data safety rate: "
        f"{float(workflow_metrics['synthetic_data_safety_rate']):.3f}"
    )
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

    print()
    print("Workflow per-case results:")
    for case in workflow_metrics["per_case"]:
        status = "PASS" if case["status_pass"] and case["audit_complete"] else "FAIL"
        print(f"- {status} {case['id']}")
        print(f"  status: {case['status']} expected: {case['expected_status']}")
        print(f"  classification_pass: {case['classification_pass']}")
        print(f"  severity_pass: {case['severity_pass']}")
        print(f"  approval_enforced: {case['approval_enforced']}")
        print(f"  blocked_no_tool_call: {case['blocked_no_tool_call']}")
        print(f"  draft_action_safe: {case['draft_action_safe']}")
        print(f"  audit_complete: {case['audit_complete']}")
        print(f"  expected_tool_coverage: {case['expected_tool_coverage']}")
        print(f"  synthetic_data_safe: {case['synthetic_data_safe']}")

    if not passes_threshold(retrieval_metrics, hit_at_3_threshold=1.0):
        raise SystemExit("Retrieval eval failed: hit@3 below 1.000 threshold")

    if not passes_answer_thresholds(answer_metrics, expected_term_coverage_threshold=0.5):
        raise SystemExit("Answer eval failed: one or more quality thresholds were not met")

    if not passes_workflow_thresholds(workflow_metrics):
        raise SystemExit("Workflow eval failed: one or more safety thresholds were not met")


if __name__ == "__main__":
    main()
