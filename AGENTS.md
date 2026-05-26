# Repository Instructions for Coding Agents

## Project Goal

Build a minimal but realistic enterprise AI agent reference stack for internal incident support. The project should demonstrate RAG, controlled agent workflows, an MCP policy server direction, automated evals, guardrails, audit logging, and AWS deployment planning.

## Repository Layout

- `apps/api/`: FastAPI backend for health, metadata, and future agent APIs.
- `apps/web/`: React + TypeScript frontend skeleton.
- `mcp/policy_server/`: Plain Python policy lookup and workflow helper functions. MCP protocol support is a later phase.
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

Run evals after any RAG, retrieval, chunking, document loading, answer composition, or eval logic change:

```bash
python scripts/run_evals.py
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
