# Enterprise AI Agent Reference Stack

This repository is a production-oriented reference stack for an enterprise AI agent proof of concept. It is designed to be credible for technical discussions around AI FDE, Solution Architect, and LLM application engineering roles.

The stack covers:

- Retrieval-augmented generation (RAG) over enterprise documents
- Agent workflows with controlled tool use
- A future MCP tool server integration
- Automated evaluation pipelines
- Guardrails and audit logging
- AWS deployment planning

The demo scenario is an internal incident support agent that helps employees answer incident response questions, draft support tickets, and identify actions that require human approval.

All data is synthetic. The project intentionally avoids real secrets, real customer data, real AWS resources, and live model/API dependencies. The initial implementation is minimal by design so the architecture can evolve safely.

## Repository Layout

```text
apps/api/             FastAPI service skeleton
apps/web/             Vite React + TypeScript frontend skeleton
mcp/policy_server/    Policy lookup and action-draft functions
datasets/             Synthetic source docs and golden eval set
docs/                 Architecture, eval, security, and AWS planning docs
scripts/              Local ingestion and evaluation placeholders
infra/terraform/      AWS Terraform deployment skeleton
```

## Local Development

Prerequisites:

- Python 3.11+
- Node.js 20+
- npm

Windows PowerShell setup:

```powershell
cd enterprise-ai-agent-reference

cd apps/api
python -m pip install -e ".[dev]"

cd ..\..\mcp\policy_server
python -m pip install -e ".[dev]"

cd ..\..\apps\web
npm install
```

Backend tests:

```bash
cd apps/api
python -m pip install -e ".[dev]"
python -m pytest
uvicorn app.main:app --reload
```

MCP policy server tests:

```bash
cd mcp/policy_server
python -m pip install -e ".[dev]"
python -m pytest
```

Frontend install and build:

```bash
cd apps/web
npm install
npm run typecheck
npm run build
```

Full local validation:

```powershell
.\scripts\check.ps1
```

```bash
./scripts/check.sh
```

Scripts:

```bash
python scripts/ingest_docs.py
python scripts/run_evals.py
```

Terraform planning scaffold:

```bash
cd infra/terraform/envs/dev
terraform init
terraform validate
```

Terraform is for planning and manual review. Do not run `terraform apply` unless explicitly requested and after reviewing docs/aws-deployment.md.

## M1 Placeholder RAG

The backend includes a minimal local RAG foundation for the synthetic markdown corpus:

```text
datasets/sample_docs -> document loader -> deterministic chunker -> keyword retriever -> GET /rag/search
```

Example:

```bash
cd apps/api
uvicorn app.main:app --reload
```

```bash
curl "http://127.0.0.1:8000/rag/search?query=severity%20incident%20commander"
```

Retrieval is currently keyword-based and deterministic. It does not use embeddings, OpenAI APIs, pgvector, LangChain, LlamaIndex, or external services. Embedding-based retrieval and pgvector storage are planned for a later phase.

## M1.5 Retrieval Evaluation

`scripts/run_evals.py` runs deterministic retrieval evaluation against `datasets/golden_eval_set.jsonl`. The eval checks whether the keyword retriever returns the expected synthetic source documents for known queries.

Current metrics:

- hit@1: fraction of cases where an expected document is the first retrieved result.
- hit@3: fraction of cases where an expected document appears in the top three retrieved results.
- MRR: mean reciprocal rank of the first expected document in the retrieved results.

The script fails with a non-zero exit code if hit@3 is below `1.0`.

```bash
python scripts/run_evals.py
```

This is retrieval evaluation only. It deliberately runs before LLM-based answer evaluation so retrieval quality can be validated without model calls, embeddings, external APIs, or non-deterministic judges.

## M2 Grounded Answer Composition

The backend includes a deterministic answer draft endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/answers/draft" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"How should a Severity 2 incident be handled?\"}"
```

The endpoint retrieves synthetic markdown chunks with the keyword retriever, then composes a concise draft from those retrieved snippets. Model calls are disabled. The draft includes citations, limitations, confidence, retrieval mode, retrieved count, and `requires_human_review: true`.

Every answer is explicitly a draft generated from retrieved context. It must not be treated as an autonomous final answer, and it requires human review before use in any operational workflow.

## M2.5 Answer Quality Evaluation

`scripts/run_evals.py` now runs deterministic answer-quality checks after retrieval evaluation. These are heuristic checks for the current placeholder answer composer, not LLM-as-a-judge.

Current answer metrics:

- citation coverage: answerable cases pass when citations include an expected source document.
- expected term coverage: fraction of expected answer terms found in the draft answer.
- human review rate: fraction of drafts that require human review.
- insufficient evidence success rate: unanswerable cases pass when the draft says evidence is insufficient, has low confidence, and has no unrelated citations.
- groundedness proxy: answerable cases pass when the draft has citations and overlaps with retrieved context terms.

The current thresholds require retrieval hit@3, citation coverage, human review rate, and insufficient-evidence success rate to be `1.0`; expected term coverage must be at least `0.5`.

LLM-as-a-judge, factuality grading, and model-based answer evaluation are planned for a later phase and are not active.

## M3 Guardrails and Audit Events

The API now runs deterministic heuristic guardrail checks before retrieval and answer drafting. The current checks flag prompt-injection phrases, credential or secret extraction attempts, and unsafe tool-execution intent.

Current behavior:

- `GET /rag/search` returns `403` for high-risk blocked queries.
- `POST /answers/draft` returns a deterministic safety response for high-risk questions, with no retrieval and no normal answer composition.
- Successful retrieval and answer responses include `guardrail_result` and `audit_events`.
- Audit events are returned in responses but are not persisted yet.
- No real tool execution occurs.

Audit metadata is intentionally limited to safe fields such as input length, result count, risk level, flags, retrieval mode, citation count, and human-review status. It does not include full user input or secrets.

## M4 Deterministic Agent Workflow

The backend includes a deterministic incident-support workflow endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/agent/incident-support" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Severity 2 incident degradation affecting support workflows\",\"customer_id\":\"synthetic-customer-001\",\"severity_hint\":\"medium\"}"
```

The workflow orchestrates guardrail analysis, deterministic incident classification, keyword RAG retrieval, grounded answer drafting, synthetic ticket draft creation, synthetic approval request creation, and audit-event emission.

All actions are draft-only and require human approval. The workflow does not call models, execute real tools, create real tickets, contact external systems, or persist audit events.

## M5 MCP Policy/Action Server

The `mcp/policy_server` package now includes an official MCP Python SDK server using `FastMCP`. It runs locally over stdio and exposes deterministic synthetic tools:

- `search_policy`: searches in-memory synthetic policy data.
- `create_ticket_draft`: creates a synthetic draft ticket payload only.
- `request_approval`: creates a synthetic pending approval request.
- `get_customer_context`: returns synthetic customer context only.

All action-like tools are approval-gated and return `requires_human_review: true`. No tool performs real external side effects, reads secrets, returns credentials, creates real tickets, or persists state.

Run locally:

```bash
cd mcp/policy_server
python -m pip install -e ".[dev]"
python -m server
```

The incident-support agent still uses local deterministic functions in M4. A future M6 phase will add an MCP client bridge from the agent workflow to this stdio server. Streamable HTTP transport is intentionally deferred until authentication, authorization, and origin validation are designed.

## M6 MCP Client Bridge

The API includes an MCP client bridge for agent tool calls with two modes:

- `local`: default deterministic mode used by normal tests, CI, and the incident-support workflow.
- `mcp-stdio`: explicit mode that launches the local MCP policy/action server over stdio and calls its tools with the official MCP SDK.

`POST /agent/incident-support` accepts an optional `tool_mode` field:

```json
{
  "message": "Severity 2 incident degradation affecting support workflows.",
  "customer_id": "synthetic-customer-001",
  "severity_hint": "medium",
  "tool_mode": "local"
}
```

Normal CI uses `local` mode so tests remain deterministic and do not depend on subprocess lifecycle behavior. Explicit stdio validation can be run locally:

```powershell
.\scripts\check_mcp_stdio.ps1
```

```bash
./scripts/check_mcp_stdio.sh
```

Both modes keep tool actions synthetic, draft-only, and approval-gated. No real external side effects occur.

## M6.5 Workflow and Tool-call Safety Evaluation

`scripts/run_evals.py` now also runs deterministic workflow and tool-call safety checks against `datasets/workflow_eval_set.jsonl`. These evals run the incident-support workflow in `local` tool mode so normal CI remains deterministic and does not depend on MCP stdio subprocess behavior.

Current workflow metrics:

- classification accuracy: expected incident intent classification.
- severity accuracy: expected severity classification.
- approval enforcement rate: answer, ticket, and approval outputs require human review.
- blocked no-tool-call rate: guardrail-blocked inputs do not call action tools.
- draft action safety rate: tickets remain `draft` and approvals remain `pending`.
- audit completeness rate: expected audit event types are emitted.
- expected tool coverage: expected synthetic draft tools are represented in safe audit metadata.
- synthetic data safety rate: returned customer/tool context remains synthetic and does not include secret markers.

MCP stdio validation remains explicit and separate:

```powershell
.\scripts\check_mcp_stdio.ps1
```

No workflow eval calls OpenAI APIs, real external systems, AWS services, or real ticketing tools.

## M7 PostgreSQL + pgvector Local Retrieval

The backend now includes optional local PostgreSQL + pgvector retrieval support. Keyword retrieval remains the default for normal CI, evals, answer drafting, and agent workflows.

Retrieval modes:

- `GET /rag/search?query=incident&mode=keyword`: default deterministic in-memory keyword retrieval.
- `GET /rag/search?query=incident&mode=pgvector`: explicit local pgvector retrieval.

The pgvector path uses deterministic placeholder embeddings from `apps/api/app/rag/embeddings.py`. These vectors are hash/token based and exist only to demonstrate vector DB architecture. No OpenAI API, external embedding service, model call, or real customer data is used.

Local Docker Compose can start the pgvector-capable database:

```bash
docker compose up -d postgres
```

Explicit pgvector validation:

```powershell
.\scripts\check_pgvector.ps1
```

```bash
./scripts/check_pgvector.sh
```

The local defaults are development-only (`app` / `app` / `enterprise_ai_agent`). Do not commit `.env` files or real `DATABASE_URL` values.

## M7.5 pgvector CI and Gated Evals

pgvector integration now has a separate GitHub Actions workflow: `.github/workflows/pgvector-integration.yml`. It uses a pgvector PostgreSQL service container, initializes the schema, ingests synthetic documents, runs gated pgvector tests, and executes pgvector retrieval evals.

Normal CI remains Docker-free and keyword-based. The pgvector workflow is triggered manually or when pgvector-related paths change.

`scripts/check_pgvector.ps1` and `scripts/check_pgvector.sh` now use `DATABASE_URL` directly when it is set. If `DATABASE_URL` is not set, they attempt local Docker Compose startup for development.

Gated pgvector evals:

```bash
DATABASE_URL=postgresql://app:app@localhost:5432/enterprise_ai_agent python scripts/run_pgvector_evals.py
```

The pgvector eval currently checks answerable cases from `datasets/golden_eval_set.jsonl` and requires hit@3 of at least `0.75`. The threshold is lower than keyword retrieval because placeholder embeddings are intentionally crude.

## M8 OpenAI SDK Embedding Provider

The backend now has an optional OpenAI SDK embedding provider for pgvector ingestion and retrieval. Deterministic embeddings remain the default for local development, normal CI, app startup, and standard evals.

Embedding providers:

- `deterministic`: default, local, no external API calls.
- `openai`: explicit, uses the official OpenAI Python SDK for embeddings only.

Environment variables:

- `EMBEDDING_PROVIDER=deterministic | openai`
- `OPENAI_API_KEY`: required only for `EMBEDDING_PROVIDER=openai`
- `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
- `OPENAI_EMBEDDING_DIMENSIONS=16` for this demo schema
- `DATABASE_URL`: required for pgvector evals

Explicit OpenAI embedding smoke validation:

```powershell
.\scripts\check_openai_embeddings.ps1
```

```bash
./scripts/check_openai_embeddings.sh
```

Explicit OpenAI pgvector eval:

```bash
DATABASE_URL=postgresql://app:app@localhost:5432/enterprise_ai_agent \
EMBEDDING_PROVIDER=openai \
OPENAI_API_KEY=... \
python scripts/run_openai_pgvector_evals.py
```

Retrieval comparison report:

```bash
python scripts/compare_retrieval_modes.py
python scripts/compare_retrieval_modes.py --include-openai
```

M8 does not add text generation, Responses API usage, autonomous tool execution, or real customer data. OpenAI calls are explicit, API-key gated, and excluded from normal CI.

## M8.5 OpenAI Responses Answer Provider

The answer layer now supports an optional OpenAI Responses API provider for grounded answer drafts. Deterministic answer composition remains the default for normal CI, local development, app startup, and standard evals.

Answer providers:

- `deterministic`: default, local, no external API calls.
- `openai`: explicit, uses OpenAI Responses API after guardrails and retrieval.

Environment variables:

- `ANSWER_PROVIDER=deterministic | openai`
- `OPENAI_API_KEY`: required only for `ANSWER_PROVIDER=openai`
- `OPENAI_TEXT_MODEL=gpt-5.2`
- `OPENAI_REASONING_EFFORT=low`

Explicit OpenAI answer smoke validation:

```powershell
.\scripts\check_openai_answer_generation.ps1
```

```bash
./scripts/check_openai_answer_generation.sh
```

Explicit OpenAI answer eval:

```bash
OPENAI_API_KEY=... ANSWER_PROVIDER=openai python scripts/run_openai_answer_evals.py
```

Guardrails run before any OpenAI answer call. Guardrail-blocked inputs do not call OpenAI. Citations are derived from retrieved chunks by the application, and every generated draft keeps `requires_human_review: true`.

## M8.6 Model-call Observability

Optional OpenAI model calls now return safe observability metadata:

- `latency_ms`
- token usage when returned by the provider
- provider, operation, model, and service tier metadata
- response/request identifiers when available
- cost-estimate placeholders

Current OpenAI pricing is not hardcoded. Cost estimates are `null` unless `MODEL_PRICING_CONFIG_JSON` is explicitly provided.

Example pricing config shape:

```json
{
  "openai": {
    "some-model-name": {
      "input_per_1m_tokens_usd": 0.0,
      "output_per_1m_tokens_usd": 0.0
    }
  }
}
```

Model-call metadata excludes raw prompts, raw outputs, raw embeddings, API keys, and full user input. It is intended for audit and operational observability scaffolding only.

## M9 AWS Deployment Skeleton

The repository now includes an AWS deployment skeleton for a production-oriented enterprise AI agent stack. It covers ECS Fargate, ECR, RDS PostgreSQL with pgvector, S3 synthetic documents, Secrets Manager, CloudWatch, ALB ingress, GitHub Actions OIDC, and Terraform modules.

Key files:

- `infra/terraform/README.md`
- `infra/terraform/envs/dev/`
- `infra/terraform/modules/`
- `.github/workflows/aws-deploy.yml`
- `docs/aws-deployment.md`

The deploy workflow is `workflow_dispatch` only. It builds and pushes the API image, runs Terraform init and plan, and applies only when the manual `apply` input is explicitly set to `true`.

Required GitHub repository or environment variables:

- `AWS_ROLE_ARN`
- `AWS_REGION`
- `ECR_REPOSITORY`

No AWS resources are created by default. Normal CI remains AWS-free, API-key-free, and deterministic.
