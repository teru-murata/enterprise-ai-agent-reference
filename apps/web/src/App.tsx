import "./style.css";

export function App() {
  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Internal incident support agent</p>
          <h1>Enterprise AI Agent Reference Stack</h1>
          <p className="summary">
            A synthetic enterprise PoC for RAG, agent workflows, MCP tools, evals,
            guardrails, audit logging, and AWS deployment planning.
          </p>
        </div>
        <span className="status">Not connected yet</span>
      </section>

      <section className="chat-panel" aria-label="Agent chat placeholder">
        <div className="message assistant">
          <strong>Agent</strong>
          <p>Ask about incident response, support policy, or access controls.</p>
        </div>
        <div className="input-row">
          <input placeholder="Chat is a placeholder in this phase" disabled />
          <button disabled>Send</button>
        </div>
      </section>
    </main>
  );
}

