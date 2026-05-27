#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON:-python}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERBOSE_ANSWER="0"
if [[ "${1:-}" == "--verbose" ]]; then
  VERBOSE_ANSWER="1"
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is required for OpenAI answer generation validation." >&2
  exit 1
fi

export ANSWER_PROVIDER="openai"
export OPENAI_TEXT_MODEL="${OPENAI_TEXT_MODEL:-gpt-5.2}"
export OPENAI_REASONING_EFFORT="${OPENAI_REASONING_EFFORT:-low}"
export OPENAI_ANSWER_VERBOSE="${VERBOSE_ANSWER}"

cd "${REPO_ROOT}"
"${PYTHON_BIN}" - <<'PY'
import os
import sys
from pathlib import Path

repo_root = Path.cwd()
sys.path.insert(0, str(repo_root / "apps" / "api"))

from app.answers.providers import compose_answer

retrieved_chunks = [
    {
        "chunk_id": "incident_response_policy:2",
        "document_id": "incident_response_policy",
        "source_path": "datasets/sample_docs/incident_response_policy.md",
        "title": "Incident Response Policy",
        "text": "Severity 2 incidents require support leadership notification and incident commander review.",
        "score": 4,
    }
]
draft = compose_answer(
    "How should a Severity 2 incident be handled?",
    retrieved_chunks,
    provider="openai",
)
print("provider: openai")
print(f"model: {os.getenv('OPENAI_TEXT_MODEL', 'gpt-5.2')}")
print(f"answer length: {len(str(draft['answer']))}")
print(f"citation count: {len(draft['citations'])}")
print(f"requires_human_review: {draft['requires_human_review']}")
if os.getenv("OPENAI_ANSWER_VERBOSE") == "1":
    print(f"answer: {draft['answer']}")
PY
