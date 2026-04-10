from __future__ import annotations

import os
import time

from openai import OpenAI

from coordbench.models import GenerationRequest, GenerationResponse, ProviderConfig
from coordbench.providers.base import BaseProvider


class DeepSeekProvider(BaseProvider):
    def __init__(self, config: ProviderConfig) -> None:
        super().__init__("deepseek", config)
        base_url = config.extra.get("base_url", "https://api.deepseek.com")
        self.client = OpenAI(
            api_key=os.environ[self.config.api_key_env],
            base_url=base_url,
        )

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        started = time.perf_counter()
        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
            "stream": False,
        }
        if request.seed is not None:
            payload["seed"] = request.seed

        seed_supported = request.seed is not None
        seed_used = request.seed if request.seed is not None else None
        try:
            response = self.client.chat.completions.create(**payload)
        except Exception as exc:  # noqa: BLE001
            if request.seed is None or not self._seed_unsupported_exception(exc):
                raise
            payload.pop("seed", None)
            response = self.client.chat.completions.create(**payload)
            seed_supported = False
            seed_used = None
        latency = time.perf_counter() - started
        usage = getattr(response, "usage", None)
        choice = response.choices[0] if getattr(response, "choices", None) else None
        text = choice.message.content if choice and choice.message else ""
        finish_reason = choice.finish_reason if choice else None
        return GenerationResponse(
            provider="deepseek",
            model=request.model,
            text=text or "",
            raw_payload=self._safe_dump(response),
            resolved_model=getattr(response, "model", None) or request.model,
            provider_backend="deepseek_openai_compat",
            finish_reason=finish_reason,
            request_id=getattr(response, "id", None),
            prompt_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
            completion_tokens=getattr(usage, "completion_tokens", None) if usage else None,
            total_tokens=getattr(usage, "total_tokens", None) if usage else None,
            latency_seconds=latency,
            seed_supported=seed_supported,
            seed_used=seed_used,
        )
