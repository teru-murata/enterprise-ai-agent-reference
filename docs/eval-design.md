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

## M4 Workflow Evaluation Direction

Current evals continue to cover retrieval quality and deterministic answer quality. The incident-support workflow is covered by unit and API tests in this phase.

Future workflow evals should measure:

- correct incident classification.
- approval enforcement.
- safe blocked behavior for guardrail-triggering inputs.
- audit event completeness.
- draft-only behavior for ticket and tool-like actions.

## Future MCP Tool-Call Evaluation

M5 adds an official MCP SDK server, but protocol-level and agent-to-MCP evals are planned later. Future MCP evaluation should cover:

- correct tool selection.
- approval enforcement for action-like tools.
- safe blocked behavior when guardrails trigger.
- no side-effect execution.
- synthetic-only customer context.

M6 adds a local/default MCP bridge path plus an explicit stdio integration path. Future workflow and tool-call evals should also verify that blocked input avoids tool calls and that audit events fully capture bridge mode, tool intent, and approval state.

## M6.5 Workflow And Tool-call Safety Evaluation

M6.5 adds deterministic workflow and tool-call safety evaluation before any model calls or real integrations are introduced. The workflow eval set lives in `datasets/workflow_eval_set.jsonl` and uses synthetic incident-support cases only.

The evaluation layers are now:

- Retrieval evaluation: verifies expected source documents are returned by keyword retrieval.
- Deterministic answer evaluation: verifies citation coverage, expected answer terms, insufficient-evidence handling, groundedness proxy, and human review.
- Workflow and tool-call safety evaluation: verifies classification, severity, approval enforcement, blocked no-tool-call behavior, draft-only action status, audit completeness, expected synthetic tool coverage, and synthetic-only returned context.
- Future LLM-as-a-judge evaluation: planned later for non-deterministic qualitative answer and workflow review.

Workflow evals use `tool_mode="local"` by default. MCP stdio validation remains an explicit separate script so normal CI does not depend on subprocess lifecycle behavior.

Workflow evaluation is added before model calls or real integrations because it locks down the safety contract first: blocked inputs must not trigger action tools, action outputs must remain draft-only or pending, approval must remain mandatory, and audit events must capture workflow steps with safe metadata.

## M7 pgvector Evaluation Status

Current deterministic evals still use keyword retrieval by default. This keeps CI independent of Docker, PostgreSQL, pgvector extensions, and local database state.

The M7 pgvector path is validated explicitly with `scripts/check_pgvector.ps1` or `scripts/check_pgvector.sh`. Future phases can add gated pgvector retrieval evals that compare:

- keyword vs pgvector retrieval hit rates on the synthetic golden set.
- expected document coverage for vector search.
- ingestion completeness.
- latency for local vector search.
- behavior when the vector database is unavailable.

Any future pgvector eval must remain gated unless CI is intentionally updated to provide a stable database service.

## M7.5 Gated pgvector Retrieval Evals

`scripts/run_pgvector_evals.py` adds explicit pgvector retrieval evaluation. It requires `DATABASE_URL`, initializes the schema, ingests synthetic sample documents, and evaluates answerable cases from `datasets/golden_eval_set.jsonl`.

Current pgvector metrics:

- hit@1.
- hit@3.
- mean reciprocal rank.

The current pgvector gate requires hit@3 of at least `0.75`. Keyword retrieval remains the default deterministic baseline at hit@3 `1.0`; pgvector evals are separate because they depend on PostgreSQL, the pgvector extension, and placeholder embeddings.

The GitHub Actions pgvector integration workflow provides the stable service-container path for this gated evaluation. Local Docker is optional and not required for normal CI.

## M8 OpenAI Embedding Retrieval Evals

M8 adds optional OpenAI embedding retrieval evaluation through `scripts/run_openai_pgvector_evals.py`. The script requires both `DATABASE_URL` and `OPENAI_API_KEY`, initializes the local pgvector schema, ingests synthetic documents using OpenAI embeddings, and reports hit@1, hit@3, and MRR for answerable cases.

Normal evals remain deterministic:

- `scripts/run_evals.py` uses keyword retrieval and remains the baseline quality gate.
- `scripts/run_pgvector_evals.py` uses deterministic placeholder embeddings and requires `DATABASE_URL`.
- `scripts/run_openai_pgvector_evals.py` uses OpenAI embeddings and requires explicit API-key configuration.

`scripts/compare_retrieval_modes.py` provides reporting across keyword, deterministic pgvector, and optionally OpenAI pgvector modes. It is not a quality gate and marks unavailable optional modes as skipped.

## M8.5 OpenAI Answer Evals

M8.5 adds optional OpenAI answer evaluation through `scripts/run_openai_answer_evals.py`. The script requires `OPENAI_API_KEY`, uses keyword retrieval over synthetic documents, generates answer drafts with the OpenAI Responses API, and evaluates them with the existing deterministic answer-quality checks.

Normal answer evals remain deterministic and API-key free. Optional OpenAI answer evals currently gate:

- human review rate at `1.0`.
- citation coverage at `1.0`.
- insufficient-evidence success rate at `1.0`.

Expected term coverage and groundedness proxy are reported because model answers may paraphrase retrieved context.
