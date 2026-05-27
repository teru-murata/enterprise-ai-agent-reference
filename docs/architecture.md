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

## M5 MCP Policy/Action Server

The policy/action server uses the official MCP Python SDK and exposes local stdio tools:

```text
Incident-support agent
        |
        v
 future MCP client bridge
        |
        v
 MCP stdio server
        |
        +--> search_policy
        +--> create_ticket_draft
        +--> request_approval
        +--> get_customer_context
```

M5 implements the MCP server side only. The M4 agent still calls local deterministic helpers. M6 is expected to add a client bridge from the agent workflow to the MCP stdio server.

The MCP policy server is now an official FastMCP stdio server for synthetic policy lookup, ticket draft creation, approval requests, and synthetic customer context. The incident-support agent will call it through an MCP client bridge in a later phase.

## M6 MCP Client Bridge

The incident-support workflow can route tool-like actions through an MCP bridge:

```text
incident-support agent
        |
        v
 MCP client bridge
        |
        +--> local deterministic mode
        |
        +--> stdio MCP mode
                |
                v
        MCP policy/action server
                |
                +--> create_ticket_draft
                +--> request_approval
                +--> get_customer_context
```

Local mode is the default for normal CI. Stdio mode is available through `tool_mode: "mcp-stdio"` and explicit validation scripts.

## M6.5 Workflow Eval Flow

Workflow and tool-call safety evals exercise the incident-support workflow with synthetic cases:

```text
datasets/workflow_eval_set.jsonl
        |
        v
 incident-support workflow
        |
        v
 local MCP bridge mode
        |
        v
 classification + draft tools + audit events
        |
        v
 workflow metrics
        |
        v
 CI and local check script
```

The eval path checks classification, approval enforcement, blocked no-tool-call behavior, draft-only action safety, audit completeness, expected tool coverage, and synthetic-only returned data. It does not require MCP stdio mode, model calls, external tools, or persistent audit storage.

## M7 Local pgvector Retrieval Flow

The optional pgvector path demonstrates vector database architecture while keeping normal CI keyword-based:

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
 deterministic placeholder embeddings
        |
        v
 PostgreSQL + pgvector
        |
        v
 GET /rag/search?mode=pgvector
```

Future production retrieval can replace placeholder embeddings with real embedding models:

```text
real embedding model -> pgvector -> answer composer / agent workflow
```

The current pgvector integration is local development only. It does not run in normal CI, does not call external model APIs, and stores only synthetic sample documents.

## M7.5 pgvector CI Validation Flow

The pgvector integration workflow validates the database path separately from normal CI:

```text
GitHub Actions
        |
        v
 pgvector service container
        |
        v
 schema initialization
        |
        v
 synthetic document ingestion
        |
        v
 pgvector search
        |
        v
 gated pgvector retrieval evals
```

This workflow is explicit and path-filtered. Normal CI remains keyword-only and does not require Docker or a live database.

## M8 Embedding Provider Flow

The embedding layer now has two provider paths:

```text
sample_docs
        |
        v
 chunker
        |
        v
 embedding provider
        +--> deterministic provider, default, local only
        |
        +--> OpenAI provider, explicit, API-key gated
        |
        v
 PostgreSQL + pgvector
        |
        v
 pgvector retriever
```

The deterministic provider remains the default for normal CI, local evals, and app startup. The OpenAI provider is embeddings-only and is used only when explicitly selected by environment or script.

## M8.5 Answer Provider Flow

Answer drafting now has deterministic and explicit OpenAI provider paths:

```text
user question
        |
        v
 guardrails
        |
        v
 retriever
        |
        v
 answer provider
        +--> deterministic composer, default
        |
        +--> OpenAI Responses provider, explicit, API-key gated
        |
        v
 citations from retrieved chunks
        |
        v
 human review required
```

OpenAI answer generation is only available after guardrails pass and retrieval has produced context. The application owns citations and review requirements; the model does not perform tool execution or create final operational answers.

The dataset is intentionally synthetic and small. It supports local demos, ingestion scaffolding, and evaluation examples without exposing customer or production data.

The AWS plan targets ECS Fargate, RDS PostgreSQL with pgvector, S3, ALB, Secrets Manager, CloudWatch, GitHub Actions, and Terraform. No AWS resources are created by the current repository.
