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

`datasets/golden_eval_set.jsonl` contains four synthetic examples:

- A grounded incident response question.
- An approval-required ticket/action flow.
- An access-control-sensitive query.
- An insufficient-evidence query.

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

## M2 Answer Composition Status

M2 adds deterministic answer composition from retrieved chunks. This is not answer-quality evaluation yet. The current eval pipeline still gates retrieval quality only.

Future answer evaluation should check:

- answer correctness against expected policy behavior.
- groundedness against retrieved snippets.
- citation quality and citation coverage.
- policy compliance for sensitive or approval-required actions.
- LLM-as-a-judge only after deterministic checks are in place.

## M2.5 Deterministic Answer Evaluation

M2.5 adds deterministic answer-quality evaluation for the current answer composer. It still avoids OpenAI APIs, embeddings, external services, and LLM-as-a-judge.

The evaluation now has three layers:

- Retrieval evaluation: verifies that expected source documents appear in keyword retrieval results.
- Deterministic answer evaluation: verifies citations, expected term coverage, human review enforcement, insufficient-evidence handling, and a groundedness proxy.
- Future LLM-as-a-judge evaluation: planned for later, after deterministic checks are stable.

Answer evaluation is added before agent workflow and model calls because it creates a baseline quality gate for citations and anti-hallucination behavior. Once tool use and model-generated answers are introduced, regressions can be compared against this deterministic baseline.

The current answer-quality metrics are:

- citation coverage: answerable cases pass when citations include an expected source document.
- expected term coverage: average fraction of expected answer terms present in answer drafts.
- human review rate: fraction of drafts with `requires_human_review: true`.
- insufficient evidence success rate: unanswerable cases pass when the draft indicates insufficient evidence, confidence is low, and no unrelated citations are included.
- groundedness proxy: answerable cases pass when the answer has citations and overlaps with retrieved context terms.

The groundedness proxy is not a full factuality metric. It only checks deterministic overlap with retrieved context.

## M3 Guardrail And Audit Validation

The retrieval and answer-quality eval thresholds must continue to pass after guardrail and audit integration. Guardrails should not weaken citation coverage, human review enforcement, insufficient-evidence behavior, or retrieval hit rates for answerable cases.

Future guardrail eval dimensions can include precision and recall for prompt-injection detection, secret-extraction detection, unsafe tool-intent detection, false-positive rate on safe queries, and audit metadata completeness.
