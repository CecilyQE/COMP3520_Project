from __future__ import annotations

from coordbench.utils.text import clean_surface, extract_first_answer_line

SERVICE_ERROR_MARKERS = (
    "request load is too high",
    "request load too high",
    "model is overloaded",
    "service unavailable",
    "temporarily unavailable",
    "please try again later",
    "try again later",
    "too many requests",
    "rate limit",
    "quota exceeded",
    "upstream error",
    "\u8bf7\u6c42\u8d1f\u8f7d\u8fc7\u9ad8",
    "\u8bf7\u7a0d\u540e\u518d\u8bd5",
    "\u670d\u52a1\u4e0d\u53ef\u7528",
    "\u9650\u6d41",
)


def looks_like_service_error(text: str) -> bool:
    normalized = clean_surface(text).lower()
    if not normalized:
        return False
    return any(marker in normalized for marker in SERVICE_ERROR_MARKERS)


def response_validation_error(
    *,
    text: str,
    finish_reason: str | None = None,
    error: str | None = None,
) -> str | None:
    if str(error or "").strip():
        return str(error).strip()

    if not clean_surface(text):
        return "empty response text"

    if looks_like_service_error(text):
        return "provider returned a service error message instead of an answer"

    answer = extract_first_answer_line(text)
    if answer:
        return None

    lowered_finish_reason = str(finish_reason or "").strip().lower()
    if lowered_finish_reason in {"length", "max_tokens"}:
        return "response was truncated before a final answer was produced"
    return "response does not contain a usable final answer"
