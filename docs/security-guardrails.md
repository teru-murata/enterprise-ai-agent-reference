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

Future production work should add authentication, authorization, least-privilege service roles, structured audit events, retention controls, and security review before deployment.
