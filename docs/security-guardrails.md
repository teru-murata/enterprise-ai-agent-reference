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

Future production work should add authentication, authorization, least-privilege service roles, structured audit events, retention controls, and security review before deployment.

