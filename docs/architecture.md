# Architecture

This project models an enterprise AI agent stack for an internal incident support use case. The current implementation is a minimal skeleton; the architecture below describes the intended production shape.

```text
                           +----------------------+
                           |  React Web Console   |
                           +----------+-----------+
                                      |
                                      v
                           +----------------------+
                           |   FastAPI Backend    |
                           | health, agent APIs   |
                           +----+-----------+-----+
                                |           |
                 +--------------+           +----------------+
                 v                                           v
        +------------------+                         +------------------+
        | Retrieval Layer  |                         | Agent Orchestrator|
        | embeddings, RAG  |                         | plans, tools     |
        +--------+---------+                         +--------+---------+
                 |                                            |
                 v                                            v
        +------------------+                         +------------------+
        | Vector Store     |                         | MCP Policy Server|
        | pgvector planned |                         | policy, tickets  |
        +--------+---------+                         +--------+---------+
                 |                                            |
                 v                                            v
        +------------------+                         +------------------+
        | Synthetic Docs   |                         | Audit Log        |
        | markdown corpus  |                         | events, actions  |
        +------------------+                         +------------------+
```

## Components

The web app provides an operator-facing interface for future chat, retrieved citations, approval prompts, and audit history.

The FastAPI backend exposes service health and metadata today. Future phases add RAG ingestion, retrieval, response generation, workflow state, guardrail checks, and audit logging.

## M1 Placeholder RAG Flow

The current backend includes a local keyword-based retrieval path over synthetic markdown documents:

```text
datasets/sample_docs
        |
        v
 document loader
        |
        v
 deterministic chunker
        |
        v
 keyword retriever
        |
        v
 GET /rag/search?query=...
        |
        v
 ranked JSON results with source metadata
```

The loader finds `datasets/sample_docs` from the repository root, reads markdown files, extracts a title from the first H1, and returns document metadata. The chunker splits each document on blank lines. The retriever scores chunks by case-insensitive query term matches and returns the highest-scoring chunks.

This is a placeholder retrieval layer only. Embeddings, pgvector, hybrid search, access-aware filtering, and model-generated answers are planned for later phases.

## M1.5 Retrieval Eval Flow

The retrieval evaluation path validates the placeholder retriever before answer generation exists:

```text
datasets/golden_eval_set.jsonl
        |
        v
 retrieval eval runner
        |
        v
 document loader -> chunker -> keyword retriever
        |
        v
 hit@1, hit@3, MRR
        |
        v
 CI and local check script
```

The eval fails if hit@3 falls below the current threshold of `1.0`.

## M2 Grounded Answer Flow

The answer composition path creates deterministic drafts from retrieved context:

```text
user question
        |
        v
 keyword retriever
        |
        v
 retrieved chunks
        |
        v
 answer composer
        |
        v
 citations + limitations + confidence
        |
        v
 human review required
```

The composer does not call an LLM and does not infer facts beyond retrieved snippets. If no chunks are retrieved, it returns an insufficient-evidence response.

## M2.5 Answer Eval Flow

Answer-quality evaluation runs the synthetic golden set through retrieval and answer composition:

```text
datasets/golden_eval_set.jsonl
        |
        v
 keyword RAG retrieval
        |
        v
 answer composer
        |
        v
 citation coverage + expected terms + review checks
        |
        v
 CI and local check script
```

This eval path is deterministic and local. It does not use LLM-as-a-judge.

## M3 Guardrail And Audit Flow

API requests now pass through deterministic guardrail checks before retrieval or answer drafting:

```text
user input
        |
        v
 guardrail analysis
        |
        +--> blocked safety response or 403
        |
        v
 keyword retrieval
        |
        v
 answer composition
        |
        v
 audit events
        |
        v
 API response
```

Audit events are generated as response objects only. Persistent audit storage, correlation IDs across services, retention policies, and CloudWatch/SIEM integration are planned for later phases.

## M4 Deterministic Agent Workflow

The incident-support workflow demonstrates agent orchestration without model calls or real tool execution:

```text
user message
        |
        v
 guardrails
        |
        v
 incident classification
        |
        v
 retrieval
        |
        v
 grounded answer draft
        |
        v
 ticket draft
        |
        v
 approval request
        |
        v
 audit events
```

The current ticket and approval steps are local placeholders. Real MCP protocol integration, external tool execution, and persistent audit storage are planned later.

The MCP policy server is currently a plain Python module. It simulates enterprise policy lookup, ticket draft creation, and approval request generation. Phase 2 will wrap these functions in an MCP-compatible server.

The dataset is intentionally synthetic and small. It supports local demos, ingestion scaffolding, and evaluation examples without exposing customer or production data.

The AWS plan targets ECS Fargate, RDS PostgreSQL with pgvector, S3, ALB, Secrets Manager, CloudWatch, GitHub Actions, and Terraform. No AWS resources are created by the current repository.
