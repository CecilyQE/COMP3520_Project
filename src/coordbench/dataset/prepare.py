from __future__ import annotations

import csv
import io
import logging
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from coordbench.dataset.osf import latest_source_snapshot
from coordbench.paths import prepared_root
from coordbench.prompts import translate_item
from coordbench.utils.files import ensure_dir, read_json, write_json
from coordbench.utils.text import choose_representative, clean_surface, make_match_key, prettify_prompt

LOGGER = logging.getLogger(__name__)


def _read_csv_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    return rows[0], rows[1:]


def _docx_lines(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", errors="replace")
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    lines = [clean_surface(line) for line in xml.splitlines()]
    return [line for line in lines if line]


def parse_alignment_item_table(path: Path) -> dict[int, str]:
    lines = _docx_lines(path)
    mapping: dict[int, str] = {}
    for index, line in enumerate(lines[:-1]):
        if line.isdigit():
            number = int(line)
            next_line = prettify_prompt(lines[index + 1].rstrip("."))
            if 1 <= number <= 30 and next_line.lower().startswith("name"):
                mapping[number] = next_line
    return mapping


PROMPT_KEY_OVERRIDES = {
    "nameasportplayer": "Name a sport player (any sport)",
    "nameasportplayeranysport": "Name a sport player (any sport)",
    "nameadish": "Name a typical dish",
    "nameaflower": "Name a typical flower",
    "nameatvbroadcastorganisation": "Name a television broadcasting organisation",
    "nameatvbroadcastorganization": "Name a television broadcasting organisation",
}


def _normalize_population(value: str) -> str:
    lowered = clean_surface(value).lower().replace(" ", "_")
    aliases = {
        "british": "british",
        "global": "global",
        "south_african": "south_african",
        "southafrican": "south_african",
        "chile": "chilean",
        "chilean": "chilean",
    }
    return aliases.get(lowered, lowered)


def _extract_prompt_from_raw(value: str, item_table: dict[int, str], item_number: int) -> str:
    raw_key = make_match_key(value)

    def canonical_prompt(prompt: str) -> str:
        prompt_key = make_match_key(prompt)
        if prompt_key in PROMPT_KEY_OVERRIDES:
            return PROMPT_KEY_OVERRIDES[prompt_key]
        return prettify_prompt(prompt.rstrip(".:"))

    alias_lookup: dict[str, str] = {}
    for prompt in item_table.values():
        canonical = canonical_prompt(prompt)
        canonical_key = make_match_key(canonical)
        alias_lookup[canonical_key] = canonical
        alias_lookup.setdefault(make_match_key(re.sub(r"\([^)]*\)", "", canonical)), canonical)
    alias_lookup.update(PROMPT_KEY_OVERRIDES)

    if "namea" in raw_key:
        slug = raw_key[raw_key.rfind("namea") :]
        if slug in alias_lookup:
            return alias_lookup[slug]

        candidates = [
            canonical
            for alias_key, canonical in alias_lookup.items()
            if alias_key and (alias_key in slug or slug in alias_key)
        ]
        if candidates:
            return max(candidates, key=lambda prompt: len(make_match_key(prompt)))

    candidates = [
        canonical_prompt(prompt)
        for prompt in item_table.values()
        if make_match_key(prompt) in raw_key or raw_key.endswith(make_match_key(prompt))
    ]
    if candidates:
        return max(candidates, key=lambda prompt: len(make_match_key(prompt)))
    fallback = item_table.get(item_number)
    if fallback:
        return canonical_prompt(fallback)
    match = re.search(r"(name.+)$", clean_surface(value), flags=re.IGNORECASE)
    if match:
        fallback_text = prettify_prompt(match.group(1).rstrip(".:"))
        return alias_lookup.get(make_match_key(fallback_text), fallback_text)
    return f"Item {item_number}"


def _human_canonical_map(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = frame.groupby(["panel_id", "item_id", "answer_key"], dropna=False)
    for (panel_id, item_id, answer_key), group in grouped:
        canonical_answer = choose_representative(group["response_clean"].tolist())
        count = int(group.shape[0])
        rows.append(
            {
                "panel_id": panel_id,
                "item_id": item_id,
                "answer_key": answer_key,
                "canonical_answer": canonical_answer,
                "count": count,
            }
        )
    result = pd.DataFrame(rows)
    totals = result.groupby(["panel_id", "item_id"])["count"].transform("sum")
    result["probability"] = result["count"] / totals
    return result.sort_values(["panel_id", "item_id", "count"], ascending=[True, True, False])


def _study1_rows(source_dir: Path, item_table: dict[int, str]) -> list[dict[str, Any]]:
    path = source_dir / "datasets" / "Study1.csv"
    header, rows = _read_csv_rows(path)
    prompt_row = rows[0]
    data_rows = rows[1:]
    header_index = {name: idx for idx, name in enumerate(header)}
    output_rows: list[dict[str, Any]] = []

    for respondent_offset, row in enumerate(data_rows, start=1):
        condition = clean_surface(row[header_index["condition "]])
        if condition not in {"British", "Global"}:
            continue
        respondent_group = _normalize_population(condition)
        participant_id = clean_surface(row[header_index["n"]]) or f"study1_{respondent_offset}"
        for item_number in range(1, 31):
            column = f"op{item_number}"
            answer = clean_surface(row[header_index[column]])
            if not answer:
                continue
            raw_prompt = prompt_row[header_index[column]]
            item_text_en = _extract_prompt_from_raw(raw_prompt, item_table, item_number)
            output_rows.append(
                {
                    "study_id": "study1",
                    "panel_id": f"study1_{respondent_group}_within",
                    "respondent_group": respondent_group,
                    "target_group": respondent_group,
                    "relation": "within",
                    "item_id": f"study1_item_{item_number:02d}",
                    "item_number": item_number,
                    "item_text_en": item_text_en,
                    "item_text_zh": translate_item(item_text_en),
                    "participant_id": participant_id,
                    "response_original": answer,
                    "response_clean": clean_surface(answer),
                    "answer_key": make_match_key(answer),
                    "source_file": "Study1.csv",
                    "source_column": column,
                }
            )
    return output_rows


def _study2_rows(source_dir: Path, item_table: dict[int, str]) -> list[dict[str, Any]]:
    header, rows = _read_csv_rows(source_dir / "datasets" / "Study2.csv")
    prompt_row = rows[0]
    data_rows = rows[2:]
    header_index = {name: idx for idx, name in enumerate(header)}
    output_rows: list[dict[str, Any]] = []

    for respondent_offset, row in enumerate(data_rows, start=1):
        country = _normalize_population(row[header_index["country_cat"]])
        if country not in {"british", "south_african"}:
            continue
        participant_id = clean_surface(row[header_index["ResponseId"]]) or f"study2_{respondent_offset}"
        if country == "british":
            panel_specs = {
                "within": ("british", [f"item_{i}_uk" for i in range(1, 16)]),
                "between": ("south_african", [f"item_{i}_sa" for i in range(1, 16)]),
            }
        else:
            panel_specs = {
                "within": ("south_african", [f"item_{i}_sa" for i in range(1, 16)]),
                "between": ("british", [f"item_{i}_uk" for i in range(1, 16)]),
            }

        for relation, (target_group, columns) in panel_specs.items():
            for item_number, column in enumerate(columns, start=1):
                answer = clean_surface(row[header_index[column]])
                if not answer:
                    continue
                raw_prompt = prompt_row[header_index[column]]
                item_text_en = _extract_prompt_from_raw(raw_prompt, item_table, item_number)
                output_rows.append(
                    {
                        "study_id": "study2",
                        "panel_id": f"study2_{country}_{relation}",
                        "respondent_group": country,
                        "target_group": target_group,
                        "relation": relation,
                        "item_id": f"study2_item_{item_number:02d}",
                        "item_number": item_number,
                        "item_text_en": item_text_en,
                        "item_text_zh": translate_item(item_text_en),
                        "participant_id": participant_id,
                        "response_original": answer,
                        "response_clean": clean_surface(answer),
                        "answer_key": make_match_key(answer),
                        "source_file": "Study2.csv",
                        "source_column": column,
                    }
                )
    return output_rows


def _study3_rows(source_dir: Path, item_table: dict[int, str]) -> list[dict[str, Any]]:
    header, rows = _read_csv_rows(source_dir / "datasets" / "Study3.csv")
    prompt_row = rows[0]
    data_rows = rows[2:]
    header_index = {name: idx for idx, name in enumerate(header)}
    output_rows: list[dict[str, Any]] = []

    for respondent_offset, row in enumerate(data_rows, start=1):
        country = _normalize_population(row[header_index["Country"]])
        if country not in {"chilean", "south_african"}:
            continue
        participant_id = clean_surface(row[header_index["ResponseId"]]) or f"study3_{respondent_offset}"
        panel_specs = {
            "within": (country, [f"item_{i}" for i in range(1, 16)]),
            "between": ("global", [f"item_{i}_glo" for i in range(1, 16)]),
        }
        for relation, (target_group, columns) in panel_specs.items():
            for item_number, column in enumerate(columns, start=1):
                answer = clean_surface(row[header_index[column]])
                if not answer:
                    continue
                raw_prompt = prompt_row[header_index[column]]
                item_text_en = _extract_prompt_from_raw(raw_prompt, item_table, item_number)
                output_rows.append(
                    {
                        "study_id": "study3",
                        "panel_id": f"study3_{country}_{relation}",
                        "respondent_group": country,
                        "target_group": target_group,
                        "relation": relation,
                        "item_id": f"study3_item_{item_number:02d}",
                        "item_number": item_number,
                        "item_text_en": item_text_en,
                        "item_text_zh": translate_item(item_text_en),
                        "participant_id": participant_id,
                        "response_original": answer,
                        "response_clean": clean_surface(answer),
                        "answer_key": make_match_key(answer),
                        "source_file": "Study3.csv",
                        "source_column": column,
                    }
                )
    return output_rows


def prepare_human_panels(
    source_snapshot_dir: Path | None = None,
    output_root: Path | None = None,
) -> Path:
    source_snapshot_dir = source_snapshot_dir or latest_source_snapshot()
    if source_snapshot_dir is None:
        raise FileNotFoundError("No source snapshot found. Run `coordbench fetch-source-data` first.")
    source_manifest = read_json(source_snapshot_dir / "source_manifest.json")
    source_snapshot_id = str(source_manifest["snapshot_id"])

    output_root = output_root or prepared_root()
    prepared_dir = ensure_dir(output_root / source_snapshot_id)
    item_table = parse_alignment_item_table(source_snapshot_dir / "materials" / "Table_of_Alignment_Items.docx")

    rows = (
        _study1_rows(source_snapshot_dir, item_table)
        + _study2_rows(source_snapshot_dir, item_table)
        + _study3_rows(source_snapshot_dir, item_table)
    )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("Prepared participant response table is empty.")

    frame = frame.sort_values(["panel_id", "participant_id", "item_number"]).reset_index(drop=True)
    frame.to_csv(prepared_dir / "participant_responses.csv", index=False)

    human_distributions = _human_canonical_map(frame)
    human_distributions.to_csv(prepared_dir / "human_distributions.csv", index=False)

    panel_items = (
        frame[
            [
                "panel_id",
                "study_id",
                "respondent_group",
                "target_group",
                "relation",
                "item_id",
                "item_number",
                "item_text_en",
                "item_text_zh",
            ]
        ]
        .drop_duplicates()
        .sort_values(["panel_id", "item_number"])
    )
    panel_items.to_csv(prepared_dir / "panel_items.csv", index=False)

    manifest = {
        "source_snapshot_id": source_snapshot_id,
        "prepared_snapshot_id": source_snapshot_id,
        "participant_rows": int(frame.shape[0]),
        "panels": sorted(frame["panel_id"].unique().tolist()),
        "default_panel_id": "study2_british_within",
    }
    write_json(prepared_dir / "benchmark_manifest.json", manifest)
    ensure_dir(output_root).joinpath("LATEST.txt").write_text(source_snapshot_id, encoding="utf-8")
    LOGGER.info("Prepared benchmark data into %s", prepared_dir)
    return prepared_dir
