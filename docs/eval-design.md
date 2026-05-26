# Evaluation Design

The evaluation pipeline is planned around deterministic synthetic examples first, then progressively richer offline and human review workflows.

## Planned Dimensions

- Retrieval hit rate: whether the expected source document appears in retrieved context.
- Groundedness: whether generated answers are supported by retrieved passages.
- Answer correctness: whether the answer matches the expected policy outcome.
- Citation quality: whether citations identify the right document and section.
- Policy compliance: whether the agent follows enterprise policy constraints.
- Action safety: whether external or state-changing actions require approval.
- Latency: request time across retrieval, generation, tools, and guardrails.
- Cost: token, model, infrastructure, and tool execution cost estimates.

## Current Eval Set

`datasets/golden_eval_set.jsonl` contains three synthetic examples:

- A grounded incident response question.
- An approval-required ticket/action flow.
- An access-control-sensitive query.

`scripts/run_evals.py` currently reads the cases and prints the planned checks. Future phases can add retrieval assertions, model-graded groundedness, rule-based safety checks, and CI reporting.

