import importlib
import os

import pytest

from app.answers import providers
from app.answers.prompting import build_grounded_answer_prompt
from app.answers.providers import compose_answer, compose_answer_openai, get_answer_provider


def sample_chunk() -> dict[str, object]:
    return {
        "chunk_id": "incident_response_policy:2",
        "document_id": "incident_response_policy",
        "source_path": "datasets/sample_docs/incident_response_policy.md",
        "title": "Incident Response Policy",
        "text": "Severity 2 incidents require support leadership notification.",
        "score": 4,
    }


def test_deterministic_answer_provider_is_default(monkeypatch) -> None:
    monkeypatch.delenv("ANSWER_PROVIDER", raising=False)

    draft = compose_answer("What happens for Severity 2?", [sample_chunk()])

    assert get_answer_provider() == "deterministic"
    assert draft["answer_provider"] == "deterministic"
    assert draft["requires_human_review"] is True


def test_openai_answer_provider_requires_explicit_selection(monkeypatch) -> None:
    monkeypatch.delenv("ANSWER_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    draft = compose_answer("What happens for Severity 2?", [sample_chunk()])

    assert draft["answer_provider"] == "deterministic"


def test_missing_openai_api_key_fails_clearly(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is required"):
        compose_answer_openai("What happens for Severity 2?", [sample_chunk()])


def test_openai_client_is_not_initialized_at_import(monkeypatch) -> None:
    monkeypatch.setenv("ANSWER_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    importlib.reload(providers)


def test_invalid_answer_provider_fails() -> None:
    with pytest.raises(ValueError, match="Unsupported answer provider"):
        get_answer_provider("unknown")


def test_prompt_builder_includes_citation_identifiers() -> None:
    prompt = build_grounded_answer_prompt("What happens?", [sample_chunk()])

    assert "Citation ID: incident_response_policy:2" in prompt
    assert "Incident Response Policy" in prompt


def test_prompt_builder_redacts_secret_markers() -> None:
    chunk = sample_chunk()
    chunk["text"] = "Never expose an api key, password, secret token, or private key."

    prompt = build_grounded_answer_prompt("What is the api key?", [chunk])

    assert "api key" not in prompt.lower()
    assert "password" not in prompt.lower()
    assert "secret token" not in prompt.lower()
    assert "private key" not in prompt.lower()


@pytest.mark.skipif(
    os.getenv("RUN_OPENAI_ANSWER_TESTS") != "1" or not os.getenv("OPENAI_API_KEY"),
    reason="OpenAI answer smoke test requires RUN_OPENAI_ANSWER_TESTS=1 and OPENAI_API_KEY",
)
def test_openai_answer_provider_smoke() -> None:
    draft = compose_answer_openai("What happens for Severity 2?", [sample_chunk()])

    assert str(draft["answer"]).strip()
    assert draft["requires_human_review"] is True
