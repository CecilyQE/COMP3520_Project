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
        import requests
        import json
        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
            "stream": True
        }
        res = requests.post(
            os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ[self.config.api_key_env]}",
                "Content-Type": "application/json"
            },
            json=payload,
            stream=True,
            timeout=120
        )
        res.raise_for_status()
        
        full_text = ""
        for line in res.iter_lines():
            if not line:
                continue
            if not line.startswith(b"data:"):
                continue
            if line.strip() == b"data: [DONE]":
                break
            try:
                chunk = json.loads(line.decode("utf-8", errors="ignore")[5:])
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    full_text += delta.get("content", "")
            except Exception:
                pass
                
        latency = time.perf_counter() - started
        return GenerationResponse(
            provider="openai",
            model=request.model,
            text=full_text,
            raw_payload="streaming",
            resolved_model=request.model,
            provider_backend="requests_atomgit_stream",
            finish_reason=None,
            request_id=None,
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            latency_seconds=latency,
        )
