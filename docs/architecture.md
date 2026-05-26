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

The MCP policy server is currently a plain Python module. It simulates enterprise policy lookup, ticket draft creation, and approval request generation. Phase 2 will wrap these functions in an MCP-compatible server.

The dataset is intentionally synthetic and small. It supports local demos, ingestion scaffolding, and evaluation examples without exposing customer or production data.

The AWS plan targets ECS Fargate, RDS PostgreSQL with pgvector, S3, ALB, Secrets Manager, CloudWatch, GitHub Actions, and Terraform. No AWS resources are created by the current repository.
