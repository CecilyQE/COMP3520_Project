from coordbench.models import GenerationRequest, ProviderConfig
from coordbench.providers.openai_provider import OpenAIProvider


class _FakeJsonResponse:
    status_code = 200
    headers = {"content-type": "application/json", "x-request-id": "req_json"}
    text = '{"id":"chatcmpl_test"}'

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "id": "chatcmpl_test",
            "model": "gpt-5.4",
            "choices": [
                {
                    "message": {"content": "London"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15},
        }

    def iter_lines(self):
        return iter(())


class _FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, headers, json, stream, timeout):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "stream": stream,
                "timeout": timeout,
            }
        )
        return _FakeJsonResponse()


def test_openai_provider_accepts_non_sse_json_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    config = ProviderConfig(
        enabled=True,
        model="gpt-5.4",
        api_key_env="OPENAI_API_KEY",
        timeout_seconds=30,
    )
    provider = OpenAIProvider(config)
    provider.session = _FakeSession()
    request = GenerationRequest(
        provider="openai",
        model="gpt-5.4",
        panel_id="study2_british_within",
        item_id="study2_item_01",
        item_text_en="Name a city",
        item_text_zh="city zh",
        prompt_language="en",
        answer_language="English",
        round_index=1,
        sample_index=0,
        system_prompt="Return one answer only.",
        user_prompt="Category: Name a city",
        temperature=1.0,
        max_output_tokens=24,
        seed=123,
    )

    response = provider.generate(request)

    assert response.text == "London"
    assert response.finish_reason == "stop"
    assert response.provider_backend == "openai_chat_completions_json"
    assert response.seed_supported is True
    assert response.seed_used == 123
    assert provider.session.calls[0]["json"]["seed"] == 123


class _UnsupportedSeedResponse:
    status_code = 400
    headers = {"content-type": "application/json"}
    text = '{"error":{"message":"Unsupported parameter: seed"}}'

    def raise_for_status(self):
        raise RuntimeError("should retry without seed before raise_for_status")

    def json(self):
        return {"error": {"message": "Unsupported parameter: seed"}}


class _FallbackSession:
    def __init__(self):
        self.calls = []

    def post(self, url, headers, json, stream, timeout):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "stream": stream,
                "timeout": timeout,
            }
        )
        if len(self.calls) == 1:
            return _UnsupportedSeedResponse()
        return _FakeJsonResponse()


def test_openai_provider_retries_without_seed_when_endpoint_rejects_it(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    config = ProviderConfig(
        enabled=True,
        model="gpt-5.4",
        api_key_env="OPENAI_API_KEY",
        timeout_seconds=30,
    )
    provider = OpenAIProvider(config)
    provider.session = _FallbackSession()
    request = GenerationRequest(
        provider="openai",
        model="gpt-5.4",
        panel_id="study2_british_within",
        item_id="study2_item_01",
        item_text_en="Name a city",
        item_text_zh="city zh",
        prompt_language="en",
        answer_language="English",
        round_index=1,
        sample_index=0,
        system_prompt="Return one answer only.",
        user_prompt="Category: Name a city",
        temperature=1.0,
        max_output_tokens=24,
        seed=321,
    )

    response = provider.generate(request)

    assert response.text == "London"
    assert response.seed_supported is False
    assert response.seed_used is None
    assert provider.session.calls[0]["json"]["seed"] == 321
    assert "seed" not in provider.session.calls[1]["json"]
