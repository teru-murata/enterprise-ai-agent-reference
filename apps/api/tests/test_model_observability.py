from types import SimpleNamespace

from app.observability.costs import estimate_cost_usd
from app.observability.model_calls import (
    create_model_call_record,
    elapsed_ms,
    extract_service_tier,
    extract_usage_from_openai_response,
    start_timer,
)


def test_extract_usage_from_object_like_response() -> None:
    response = SimpleNamespace(
        usage=SimpleNamespace(input_tokens=10, output_tokens=5, total_tokens=15)
    )

    assert extract_usage_from_openai_response(response) == {
        "input_tokens": 10,
        "output_tokens": 5,
        "total_tokens": 15,
    }


def test_extract_usage_from_dict_like_response() -> None:
    response = {"usage": {"prompt_tokens": 7, "completion_tokens": 3}}

    assert extract_usage_from_openai_response(response) == {
        "input_tokens": 7,
        "output_tokens": 3,
        "total_tokens": 10,
    }


def test_missing_usage_returns_null_token_fields() -> None:
    assert extract_usage_from_openai_response({}) == {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }


def test_extract_service_tier_from_response() -> None:
    assert extract_service_tier(SimpleNamespace(service_tier="default")) == "default"
    assert extract_service_tier({"service_tier": "flex"}) == "flex"
    assert extract_service_tier({}) is None


def test_create_model_call_record_excludes_raw_prompt_and_output() -> None:
    record = create_model_call_record(
        provider="openai",
        operation="responses.answer",
        model="test-model",
        started_at_utc="2026-01-01T00:00:00+00:00",
        completed_at_utc="2026-01-01T00:00:01+00:00",
        latency_ms=1000,
        status="succeeded",
        metadata={
            "question_length": 12,
            "raw_prompt": "secret prompt",
            "raw_output": "secret output",
            "api_key": "fake-key",
        },
    )

    assert record["metadata"] == {"question_length": 12}
    assert record["safety"]["raw_prompt_logged"] is False
    assert record["safety"]["raw_output_logged"] is False
    assert "secret prompt" not in str(record)
    assert "fake-key" not in str(record)


def test_latency_is_non_negative() -> None:
    assert elapsed_ms(start_timer()) >= 0


def test_cost_estimate_returns_null_without_config(monkeypatch) -> None:
    monkeypatch.delenv("MODEL_PRICING_CONFIG_JSON", raising=False)

    assert estimate_cost_usd(
        "openai",
        "test-model",
        {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
    ) == {
        "estimated_cost_usd": None,
        "cost_estimation_method": "not_configured",
    }


def test_cost_estimate_computes_with_explicit_config(monkeypatch) -> None:
    monkeypatch.setenv(
        "MODEL_PRICING_CONFIG_JSON",
        '{"openai":{"test-model":{"input_per_1m_tokens_usd":1.0,'
        '"output_per_1m_tokens_usd":2.0}}}',
    )

    assert estimate_cost_usd(
        "openai",
        "test-model",
        {"input_tokens": 1_000_000, "output_tokens": 500_000, "total_tokens": 1_500_000},
    ) == {
        "estimated_cost_usd": 2.0,
        "cost_estimation_method": "configured_per_1m_tokens",
    }
