from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

from coordbench.models import GenerationRequest, GenerationResponse, ProviderConfig

SEED_UNSUPPORTED_MARKERS = (
    "seed",
    "unsupported",
    "unknown parameter",
    "unrecognized request argument",
    "extra inputs are not permitted",
    "not supported",
)


class BaseProvider(ABC):
    def __init__(self, provider_name: str, config: ProviderConfig) -> None:
        self.provider_name = provider_name
        self.config = config
        if self.config.enabled and not self.config.model:
            raise ValueError(f"Provider `{provider_name}` is enabled but no model was configured.")
        if self.config.enabled and self.config.api_key_env and not os.environ.get(self.config.api_key_env):
            raise ValueError(
                f"Provider `{provider_name}` is enabled but env var `{self.config.api_key_env}` is not set."
            )

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError

    def _safe_dump(self, payload: Any) -> dict[str, Any]:
        if hasattr(payload, "model_dump"):
            return payload.model_dump()
        if hasattr(payload, "to_dict"):
            return payload.to_dict()
        if isinstance(payload, dict):
            return payload
        return {"repr": repr(payload)}

    def _seed_unsupported_exception(self, exc: Exception) -> bool:
        lowered = str(exc).strip().lower()
        return all(marker in lowered for marker in SEED_UNSUPPORTED_MARKERS[:1]) and any(
            marker in lowered for marker in SEED_UNSUPPORTED_MARKERS[1:]
        )

    def _seed_unsupported_response(self, response: Any) -> bool:
        status_code = int(getattr(response, "status_code", 0) or 0)
        if status_code < 400:
            return False

        message = ""
        try:
            payload = response.json()
        except Exception:  # noqa: BLE001
            payload = None
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                message = str(error.get("message", "")).strip()
            elif error is not None:
                message = str(error).strip()
            if not message:
                message = str(payload.get("message", "")).strip()
        if not message:
            message = str(getattr(response, "text", "") or "").strip()

        lowered = message.lower()
        return "seed" in lowered and any(
            marker in lowered
            for marker in (
                "unsupported",
                "unknown parameter",
                "unrecognized request argument",
                "extra inputs are not permitted",
                "not supported",
            )
        )
