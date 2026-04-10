from coordbench.models import GenerationRequest, ProviderConfig
from coordbench.providers.deepseek_provider import DeepSeekProvider


class _FakeUsage:
    prompt_tokens = 12
    completion_tokens = 3
    total_tokens = 15


class _FakeMessage:
    content = "London"


class _FakeChoice:
    message = _FakeMessage()
    finish_reason = "stop"


class _FakeResponse:
    model = "deepseek-chat"
    id = "deepseek_resp_123"
    usage = _FakeUsage()
    choices = [_FakeChoice()]

    def model_dump(self):
        return {
            "model": self.model,
            "id": self.id,
            "choices": [{"message": {"content": "London"}, "finish_reason": "stop"}],
        }


class _FakeCompletions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeResponse()


class _FakeChat:
    def __init__(self):
        self.completions = _FakeCompletions()


class _FakeClient:
    def __init__(self):
        self.chat = _FakeChat()


def test_deepseek_provider_passes_seed(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret")
    config = ProviderConfig(
        enabled=True,
        model="deepseek-chat",
        api_key_env="DEEPSEEK_API_KEY",
        timeout_seconds=30,
    )
    provider = DeepSeekProvider(config)
    provider.client = _FakeClient()
    request = GenerationRequest(
        provider="deepseek",
        model="deepseek-chat",
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
        seed=789,
    )

    response = provider.generate(request)

    assert response.text == "London"
    assert response.seed_supported is True
    assert response.seed_used == 789
    assert provider.client.chat.completions.calls[0]["seed"] == 789
