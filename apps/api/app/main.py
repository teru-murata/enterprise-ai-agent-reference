from fastapi import FastAPI

PROJECT_METADATA = {
    "name": "enterprise-ai-agent-reference",
    "version": "0.1.0",
    "description": "Enterprise AI agent reference stack for incident support.",
}

app = FastAPI(
    title="Enterprise AI Agent Reference API",
    version=PROJECT_METADATA["version"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return PROJECT_METADATA

