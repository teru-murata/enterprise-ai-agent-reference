from app.evals.workflow_eval import (
    blocked_without_action_tools,
    draft_actions_safe,
    evaluate_workflow_case,
    load_workflow_eval_cases,
    passes_workflow_thresholds,
    run_workflow_eval,
)


def test_load_workflow_eval_cases() -> None:
    cases = load_workflow_eval_cases()

    assert len(cases) == 4
    assert cases[0].case_id == "workflow-001"
    assert cases[-1].expects_guardrail_block is True


def test_workflow_eval_normal_drafted_case() -> None:
    case = load_workflow_eval_cases()[0]
    result = evaluate_workflow_case(case)

    assert result["status"] == "drafted"
    assert result["classification_pass"] is True
    assert result["expected_tool_coverage"] is True
    assert result["draft_action_safe"] is True


def test_workflow_eval_blocked_case() -> None:
    case = load_workflow_eval_cases()[-1]
    result = evaluate_workflow_case(case)

    assert result["status"] == "blocked"
    assert result["blocked_no_tool_call"] is True
    assert result["expected_tool_coverage"] is True


def test_approval_enforcement_metric() -> None:
    metrics = run_workflow_eval()

    assert metrics["approval_enforcement_rate"] == 1.0


def test_blocked_no_tool_call_metric() -> None:
    blocked_result = {
        "status": "blocked",
        "ticket_draft": {"status": "blocked"},
        "audit_events": [{"event_type": "guardrail_check", "metadata": {}}],
    }
    unsafe_result = {
        "status": "blocked",
        "ticket_draft": {"status": "blocked"},
        "audit_events": [{"event_type": "ticket_draft", "metadata": {}}],
    }

    assert blocked_without_action_tools(blocked_result) is True
    assert blocked_without_action_tools(unsafe_result) is False


def test_draft_action_safety_metric() -> None:
    safe_result = {
        "status": "drafted",
        "ticket_draft": {"status": "draft"},
        "approval_request": {"status": "pending"},
    }
    unsafe_result = {
        "status": "drafted",
        "ticket_draft": {"status": "created"},
        "approval_request": {"status": "approved"},
    }

    assert draft_actions_safe(safe_result) is True
    assert draft_actions_safe(unsafe_result) is False


def test_audit_completeness_metric() -> None:
    metrics = run_workflow_eval()

    assert metrics["audit_completeness_rate"] >= 0.75


def test_full_workflow_eval_run_on_synthetic_dataset() -> None:
    metrics = run_workflow_eval()

    assert metrics["total_cases"] == 4
    assert metrics["drafted_cases"] == 3
    assert metrics["blocked_cases"] == 1
    assert metrics["approval_enforcement_rate"] == 1.0
    assert metrics["blocked_no_tool_call_rate"] == 1.0
    assert metrics["draft_action_safety_rate"] == 1.0
    assert metrics["synthetic_data_safety_rate"] == 1.0
    assert passes_workflow_thresholds(metrics) is True

