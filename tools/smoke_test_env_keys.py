#!/usr/bin/env python3
"""One-shot chat/completions smoke test per .env API key (no stream, short timeout)."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# override=True: shell may export empty DEEPSEEK_API_KEY etc. and block .env values.
load_dotenv(PROJECT_ROOT / ".env", override=True)

PROMPT = {
    "model": "REPLACE_MODEL",
    "messages": [
        {"role": "user", "content": "Reply with exactly one word: OK"},
    ],
    "max_completion_tokens": 16,
    "temperature": 1,
    "stream": False,
}


def probe(label: str, *, api_key: str, base_url: str, model: str, timeout: int = 60) -> None:
    base = base_url.rstrip("/")
    url = f"{base}/chat/completions"
    payload = {**PROMPT, "model": model}
    key_preview = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 14 else "(short/empty)"
    print(f"\n=== {label} ===", flush=True)
    print(f"  url={url}", flush=True)
    print(f"  model={model}  key={key_preview}", flush=True)
    if not api_key.strip():
        print("  RESULT: SKIP (empty key)", flush=True)
        return
    t0 = time.perf_counter()
    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
        elapsed = time.perf_counter() - t0
        print(f"  HTTP {resp.status_code}  ({elapsed:.2f}s)", flush=True)
        body = resp.text[:500]
        if resp.ok:
            try:
                data = resp.json()
                choice = (data.get("choices") or [{}])[0]
                msg = choice.get("message") or {}
                text = (msg.get("content") or "").strip()
                usage = data.get("usage") or {}
                print(f"  text={text!r}", flush=True)
                print(f"  usage={usage}", flush=True)
                print("  RESULT: OK", flush=True)
            except json.JSONDecodeError:
                print(f"  body={body!r}", flush=True)
                print("  RESULT: OK (non-json body)", flush=True)
        else:
            print(f"  body={body!r}", flush=True)
            print("  RESULT: FAIL", flush=True)
    except requests.RequestException as exc:
        print(f"  RESULT: ERROR {type(exc).__name__}: {exc}", flush=True)


def main() -> int:
    tests = [
        (
            "OPENAI (official)",
            os.getenv("OPENAI_API_KEY", ""),
            os.getenv("OPENAI_BASE_URL", "") or "https://api.openai.com/v1",
            os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        ),
        (
            "GLM (DashScope-style OpenAI compat)",
            os.getenv("GLM_API_KEY", ""),
            os.getenv("GLM_BASE_URL", "") or "https://open.bigmodel.cn/api/paas/v4",
            os.getenv("GLM_MODEL", "glm-4-flash"),
        ),
        (
            "DEEPSEEK",
            os.getenv("DEEPSEEK_API_KEY", ""),
            os.getenv("DEEPSEEK_BASE_URL", "") or "https://api.deepseek.com",
            os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        ),
        (
            "MINIMAX (OpenAI compat)",
            os.getenv("MINIMAX_API_KEY", ""),
            os.getenv("MINIMAX_BASE_URL", "") or "https://api.minimax.io/v1",
            "MiniMax-M2.7-highspeed",
        ),
        (
            "QWEN (DashScope compatible-mode)",
            os.getenv("QWEN_API_KEY", ""),
            os.getenv("QWEN_BASE_URL", "") or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "qwen-plus",
        ),
        (
            "SUM gateway — gpt-4o-mini",
            os.getenv("SUM_API_KEY", ""),
            "https://api.mytokenland.com/v1",
            "gpt-4o-mini",
        ),
        (
            "SUM gateway — gemini-2.5-flash",
            os.getenv("SUM_API_KEY", ""),
            "https://api.mytokenland.com/v1",
            "gemini-2.5-flash",
        ),
        (
            "SUM gateway — MiniMax-M2.7-highspeed",
            os.getenv("SUM_API_KEY", ""),
            "https://api.mytokenland.com/v1",
            "MiniMax-M2.7-highspeed",
        ),
    ]
    print("Smoke test: single non-stream POST /chat/completions per endpoint", flush=True)
    for label, key, base, model in tests:
        probe(label, api_key=key, base_url=base, model=model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
