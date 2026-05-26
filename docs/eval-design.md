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

Each case includes:

- `id`: stable case identifier.
- `query`: synthetic user query.
- `expected_documents`: source document filenames that should appear in retrieval results.
- `expected_terms`: terms that explain why the query should match the expected documents.
- `category`: scenario category.
- `notes`: short reviewer note.

## M1.5 Retrieval Evaluation

`scripts/run_evals.py` now runs deterministic retrieval evaluation over the placeholder keyword retriever.

The evaluation computes:

- hit@1: whether any expected document appears in the first retrieved result.
- hit@3: whether any expected document appears in the top three retrieved results.
- MRR: mean reciprocal rank for the first expected document.

The current quality gate requires hit@3 to be `1.0`. This is intentionally strict because the corpus and eval set are small, synthetic, and deterministic.

Retrieval quality is evaluated before answer generation quality because bad retrieval makes grounded answer evaluation misleading. If the expected source document is missing from context, answer correctness, groundedness, and citation quality failures may be retrieval failures rather than generation failures.

Future phases can add answer correctness checks, model-graded groundedness, citation validation, policy compliance assertions, latency tracking, and cost reporting.
