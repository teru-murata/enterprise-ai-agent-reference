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
