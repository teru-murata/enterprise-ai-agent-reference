# Security and Guardrails

This project is synthetic-only. It must not contain production documents, real customer data, real employee data, secrets, API keys, account IDs, or live credentials.

## Planned Guardrails

- Synthetic-only data: development and tests use fictional documents and golden examples.
- PII handling: future ingestion should classify, redact, or block sensitive personal data before indexing.
- Access control: retrieval should filter documents by user identity, group, purpose, and policy labels.
- Approval before tool execution: external or state-changing actions must produce an approval request before execution.
- Prompt injection checks: retrieved documents and user inputs should be scanned for instructions that attempt to override system policy.
- Audit logs: retrievals, policy checks, approval requests, tool calls, and generated outputs should be logged with correlation IDs.

## Current Safety Boundary

The current MCP policy server functions return local dictionaries only. They do not call external services, create tickets, change cloud infrastructure, or access real systems.

The current answer composer creates deterministic drafts from retrieved synthetic context only. All answer drafts require human review, no tool execution is performed by answer composition, and an insufficient-evidence response is returned when no supporting context is retrieved.

The current answer-quality eval includes an insufficient-evidence case as an anti-hallucination guardrail. It also checks that every draft keeps `requires_human_review` enabled.

## Current M3 Guardrail Categories

The local API uses deterministic heuristic checks for:

- Prompt injection: phrases such as requests to ignore instructions, reveal system prompts, show hidden instructions, bypass policy, or expose developer messages.
- Credential and secret extraction: phrases involving API keys, passwords, secret tokens, or private keys.
- Unsafe tool execution intent: phrases asking to execute without approval, delete records, disable audit, or skip human review.
- Insufficient evidence handling: answer drafts return an insufficient-evidence response when retrieval finds no supporting chunks.
- Human review enforcement: every answer draft and safety response keeps `requires_human_review: true`.

## Limitations

These guardrails are heuristic scaffolds only. They are not a replacement for enterprise authentication, authorization, DLP, IAM, SIEM integration, policy engines, legal review, or full GRC controls.

## M4 Action Safety

The deterministic incident-support workflow keeps action safety explicit:

- No autonomous execution is allowed.
- Ticket creation is draft-only.
- Approval is mandatory for every workflow.
- Guardrail-blocked messages do not trigger retrieval, normal answer drafting, or normal ticket drafting.
- Audit events are emitted for guardrail checks, classification, retrieval, answer drafting, ticket drafting, and approval requests.

## M5 MCP Safety Constraints

The MCP policy/action server is local and stdio-only in this phase:

- No real side effects are allowed.
- Ticket creation is draft-only.
- Approval remains mandatory.
- Synthetic customer context is the only customer context returned.
- Tools must not read or return secrets.
- Streamable HTTP is deferred until authentication, authorization, and origin validation are designed.

## M6 MCP Bridge Safety

The MCP client bridge preserves the same action boundary:

- Guardrails run before any tool use.
- Guardrail-blocked input does not call local or MCP tools.
- Tool actions remain synthetic and draft-only.
- Approval remains mandatory.
- Normal CI uses deterministic local mode.
- Stdio MCP validation is explicit and does not call external APIs.

## M6.5 Workflow Safety Metrics

Workflow evals now check safety behavior directly:

- Guardrail-blocked inputs must not call customer-context, ticket-draft, or approval-request tools.
- Approval enforcement must remain enabled across answer drafts, ticket drafts, approval requests, and blocked safety responses.
- Draft action safety requires ticket outputs to remain `draft` and approval outputs to remain `pending`.
- Audit completeness checks that guardrail, classification, retrieval, answer draft, customer-context, ticket-draft, and approval-request events are emitted where expected.
- Synthetic data safety checks returned tool/context payloads for synthetic-only classification and obvious secret markers.

## M7 Local Database Boundary

The local PostgreSQL + pgvector service stores synthetic sample documents and deterministic placeholder embeddings only. It is not connected to AWS, production systems, external model APIs, or real customer data.

Local development defaults are intentionally obvious and non-production. Real `DATABASE_URL` values, `.env` files, passwords, database dumps, and Terraform state must not be committed.

The pgvector GitHub Actions workflow uses local test credentials only and a service container scoped to the workflow job. `DATABASE_URL` must be provided by the environment and must not be committed to source control.

## M8 OpenAI API Key Boundary

The OpenAI embedding provider is explicit and API-key gated:

- No API keys are stored in the repository.
- `OPENAI_API_KEY` is read from the environment only.
- API keys are not logged or included in errors.
- Raw embeddings are not printed by validation scripts.
- Only synthetic sample text is sent to the embedding API.
- No real customer data, production documents, or secrets may be sent to OpenAI.
- No text generation or autonomous action execution is added in this phase.

## M8.5 Model-call Safety Boundary

OpenAI answer generation is guarded by the same safety controls:

- Guardrails run before model calls.
- Guardrail-blocked inputs do not call OpenAI.
- `OPENAI_API_KEY` is read from the environment only.
- API keys and raw prompts are not logged by default.
- Retrieved context is synthetic-only in this repository.
- Citations are assigned from retrieved chunks by application code.
- All model-generated drafts require human review.
- No real tool execution or autonomous action is added.

## M8.6 Observability Logging Safety

Model-call observability must stay metadata-only:

- API keys are never logged.
- Raw prompts are not logged.
- Raw model outputs are not logged.
- Raw embeddings are not logged.
- Full user input is not stored in audit metadata.
- Cost estimates are null unless explicit pricing config is provided.

Future production work should add authentication, authorization, least-privilege service roles, structured audit events, retention controls, and security review before deployment.
