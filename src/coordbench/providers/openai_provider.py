from __future__ import annotations

import os
import time

from openai import OpenAI

from coordbench.models import GenerationRequest, GenerationResponse, ProviderConfig
from coordbench.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, config: ProviderConfig) -> None:
        super().__init__("openai", config)
        self.client = OpenAI(api_key=os.environ[self.config.api_key_env])

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        started = time.perf_counter()
        response = self.client.responses.create(
            model=request.model,
            input=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens,
        )
        latency = time.perf_counter() - started
        usage = getattr(response, "usage", None)
        request_id = getattr(response, "_request_id", None) or getattr(response, "id", None)
        return GenerationResponse(
            provider="openai",
            model=request.model,
            text=getattr(response, "output_text", "") or "",
            raw_payload=self._safe_dump(response),
            resolved_model=getattr(response, "model", None) or request.model,
            provider_backend="openai_responses",
            finish_reason=None,
            request_id=request_id,
            prompt_tokens=getattr(usage, "input_tokens", None) if usage else None,
            completion_tokens=getattr(usage, "output_tokens", None) if usage else None,
            total_tokens=getattr(usage, "total_tokens", None) if usage else None,
            latency_seconds=latency,
        )
