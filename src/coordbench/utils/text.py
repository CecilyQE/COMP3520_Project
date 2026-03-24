from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Iterable


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def clean_surface(value: str) -> str:
    value = collapse_whitespace(value)
    value = value.strip(" \t\r\n\"'`[](){}.,;:!?")
    return collapse_whitespace(value)


def ascii_fold(value: str) -> str:
    return (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def make_match_key(value: str) -> str:
    value = clean_surface(value).lower()
    value = ascii_fold(value)
    return re.sub(r"[^a-z0-9]+", "", value)


def prettify_prompt(value: str) -> str:
    value = clean_surface(value).rstrip(".:")
    if not value:
        return value
    return value[0].upper() + value[1:]


def extract_first_answer_line(value: str) -> str:
    lines = [clean_surface(line) for line in value.splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        return ""
    first = lines[0]
    lowered = first.lower()
    for prefix in ("answer:", "答案：", "答案:", "response:"):
        if lowered.startswith(prefix):
            return clean_surface(first.split(":", 1)[-1])
    return first


def choose_representative(surface_forms: Iterable[str]) -> str:
    cleaned = [clean_surface(value) for value in surface_forms if clean_surface(value)]
    if not cleaned:
        return ""
    counts = Counter(cleaned)
    return sorted(counts.items(), key=lambda item: (-item[1], len(item[0]), item[0]))[0][0]
