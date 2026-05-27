# Repository Instructions for Coding Agents

## Project Goal

Build a minimal but realistic enterprise AI agent reference stack for internal incident support. The project should demonstrate RAG, controlled agent workflows, an MCP policy server direction, automated evals, guardrails, audit logging, and AWS deployment planning.

## Repository Layout

- `apps/api/`: FastAPI backend for health, metadata, and future agent APIs.
- `apps/web/`: React + TypeScript frontend skeleton.
- `mcp/policy_server/`: FastMCP stdio policy/action server with synthetic, approval-gated tools.
- `datasets/`: Synthetic markdown documents and golden eval cases.
- `scripts/`: Placeholder ingestion and eval runners.
- `docs/`: Architecture, scenario, eval, security, and AWS planning notes.
- `infra/terraform/`: Commented Terraform scaffold for future AWS deployment.

## Rules

- Do not add RAG, agent orchestration, OpenAI API calls, MCP protocol support, or AWS deployment features until M0.5 validation is green.
- Do not hardcode secrets, API keys, tokens, account IDs, or real ARNs.
- Do not use real customer data, employee data, incident data, or production documents.
- Do not create real AWS resources from this repository.
- Do not add broad IAM permissions such as unrestricted `*` actions or resources.
- Keep the initial implementation simple, explicit, and easy to review.
- Prefer synthetic fixtures and deterministic tests.
- Avoid network calls in tests and local scripts unless explicitly approved.
- Treat tool execution as approval-gated when it could change external state.
- Answer composition must not invent facts beyond retrieved context.
- Generated answers that use retrieved context must include citations.
- Human review remains required for answer drafts until a later phase explicitly changes this.
- Do not bypass guardrails.
- Do not remove the human review requirement.
- Do not include raw secrets or full user input in audit metadata.
- Agent workflows must not bypass guardrails.
- Agent workflows must not perform real external actions.
- Agent workflows must preserve mandatory human approval.
- MCP tools must not execute real external side effects.
- MCP tools must not bypass approval.
- MCP tools must not return secrets.
- Protocol and server changes must keep tests deterministic.
- Do not make normal CI depend on flaky MCP subprocess tests.
- MCP bridge changes must preserve local deterministic mode.
- Any MCP tool action must remain draft-only and approval-gated.
- Workflow evals must run after changes to agents, guardrails, audit, MCP bridge, or tool logic.
- Do not weaken workflow eval thresholds without documenting why.
- Blocked guardrail cases must not call action tools.
- Tool and action outputs must remain draft-only or pending and approval-gated.
- Do not commit database credentials, `.env` files, database dumps, or Terraform state.
- Do not make normal CI depend on Docker, PostgreSQL, or pgvector.
- pgvector integration tests must be gated behind an explicit environment variable or validation script.
- Do not replace deterministic keyword evals without preserving existing thresholds.
- Pgvector tests must use `RUN_PGVECTOR_TESTS=1`.
- Do not commit `DATABASE_URL`, `.env` files, database dumps, or local database state.
- Keep keyword evals as the default retrieval baseline.
- Do not call OpenAI APIs in normal tests, normal CI, app startup, or default evals.
- Do not require `OPENAI_API_KEY` for app startup.
- Do not print API keys or raw embeddings.
- Do not send real customer data, production documents, or secrets to OpenAI.
- OpenAI embedding tests must be gated with `RUN_OPENAI_EMBEDDING_TESTS=1` or explicit scripts.
- The deterministic embedding provider remains the default.
- Do not call OpenAI answer generation in normal tests, normal CI, app startup, or default evals.
- OpenAI answer tests must be gated with `RUN_OPENAI_ANSWER_TESTS=1` or explicit scripts.
- Do not print raw prompts by default.
- Deterministic answer composition remains the default.
- Guardrail-blocked inputs must not call OpenAI.
- Model-generated answers must keep `requires_human_review: true`.
- Do not hardcode live model pricing.
- Cost estimates must be null unless explicit pricing config is provided.
- Model-call observability must preserve safe metadata only.
- Do not log raw prompts, outputs, embeddings, full user input, or API keys.

## Backend Commands

```bash
cd apps/api
python -m pip install -e ".[dev]"
python -m pytest
uvicorn app.main:app --reload
ruff check .
```

## Frontend Commands

```bash
cd apps/web
npm install
npm run typecheck
npm run build
```

## MCP Commands

```bash
cd mcp/policy_server
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
```

## Required Validation Commands

After changes, run the focused commands for touched areas and then the full local validation when dependencies are installed.

Run evals after any RAG, retrieval, chunking, document loading, answer composition, guardrail, audit, agent workflow, MCP bridge, tool logic, pgvector logic, or eval logic change:

```bash
python scripts/run_evals.py
```

Run pgvector evals only when `DATABASE_URL` is available:

```bash
python scripts/run_pgvector_evals.py
```

Run OpenAI embedding validation only when explicitly requested and `OPENAI_API_KEY` is available:

```bash
python scripts/run_openai_pgvector_evals.py
```

Run OpenAI answer validation only when explicitly requested and `OPENAI_API_KEY` is available:

```bash
python scripts/run_openai_answer_evals.py
```

Do not weaken eval thresholds without documenting why in the same change.

```powershell
.\scripts\check.ps1
```

```bash
./scripts/check.sh
```

The full validation runs backend tests, MCP tests, frontend typecheck, frontend build, and deterministic retrieval eval scripts. Do not hide failing checks with unconditional success.

## Infra Commands

```bash
cd infra/terraform/envs/dev
terraform init
terraform validate
```

Infrastructure is a planning scaffold only. Do not apply Terraform unless the project is explicitly changed to support real deployment.

## Review Guidelines

- Confirm new behavior is covered by focused tests where practical.
- Check that synthetic data remains synthetic and non-sensitive.
- Verify that new tool-like actions include approval, auditability, or a clear safety boundary.
- Review IAM examples for least privilege and placeholders.
- Keep docs aligned with implementation phase and limitations.

## Done Criteria

- Code is minimal, readable, and scoped to the requested behavior.
- Tests pass for touched Python packages.
- Frontend typecheck/build succeeds when dependencies are installed.
- Full local validation passes for M0.5 before feature work continues.
- Docs describe current implementation and future production direction accurately.
- No real secrets, broad IAM permissions, real customer data, or real cloud resources are introduced.
