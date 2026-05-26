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
infra/terraform/      Commented AWS infrastructure planning scaffold
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

The Terraform files are placeholders only. They do not create real AWS resources yet.
