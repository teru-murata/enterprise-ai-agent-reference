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

Future production work should add authentication, authorization, least-privilege service roles, structured audit events, retention controls, and security review before deployment.
