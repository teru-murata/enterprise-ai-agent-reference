# Demo Scenario

The demo agent is an internal incident support assistant for a fictional enterprise.

Employees use the assistant to ask questions such as:

- What should I do when a customer-facing service has elevated error rates?
- Can you draft an incident ticket for a suspected authentication outage?
- Who is allowed to access incident artifacts that contain sensitive customer metadata?

The intended behavior is not unconstrained chat. The assistant should retrieve grounded answers from approved internal policy documents, cite the relevant source documents, and refuse or escalate when a request involves sensitive access or operational action.

Example workflow:

1. A support engineer reports a possible severity 2 incident.
2. The agent retrieves incident response guidance from the synthetic policy documents.
3. The agent summarizes the next steps and drafts a ticket.
4. Before executing any external action, the agent requests explicit human approval.
5. The system records retrieval, decision, and action metadata in an audit log.

The current repository implements only the service skeleton, synthetic data, policy helper functions, and placeholder scripts. Model calls, live tools, real ticket creation, and production identity integration are future phases.

