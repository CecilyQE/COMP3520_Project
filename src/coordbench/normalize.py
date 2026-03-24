from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from rapidfuzz import fuzz, process

from coordbench.config import load_config
from coordbench.run_state import dedupe_request_records, prepared_snapshot_dir_for_run, resolve_run_dir
from coordbench.utils.files import read_json, read_jsonl, write_json
from coordbench.utils.text import clean_surface, extract_first_answer_line, make_match_key

LOGGER = logging.getLogger(__name__)


def _load_aliases(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["panel_id", "item_id", "surface_form", "canonical_answer", "notes"])
    aliases = pd.read_csv(path)
    aliases["surface_key"] = aliases["surface_form"].astype(str).map(make_match_key)
    return aliases


def normalize_run(config_path: str | Path, run_id: str | Path) -> Path:
    config = load_config(config_path)
    run_dir = resolve_run_dir(config.outputs.run_root, run_id)
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    prepared_dir = prepared_snapshot_dir_for_run(run_dir)

    raw_rows = read_jsonl(run_dir / "raw_generations.jsonl")
    if not raw_rows:
        raise RuntimeError("No raw generations found for normalization.")
    deduped_rows = dedupe_request_records(raw_rows)
    if len(deduped_rows) != len(raw_rows):
        LOGGER.info("Deduped raw generations for %s from %s rows to %s rows", run_dir, len(raw_rows), len(deduped_rows))

    frame = pd.DataFrame(deduped_rows)
    frame["parsed_answer"] = frame["response_text"].astype(str).map(extract_first_answer_line)
    frame["response_clean"] = frame["parsed_answer"].map(clean_surface)
    frame["answer_key"] = frame["response_clean"].map(make_match_key)

    aliases = _load_aliases(config.normalization.alias_path)
    human = pd.read_csv(prepared_dir / "human_distributions.csv")
    human_lookup: dict[tuple[str, str, str], str] = {
        (row.panel_id, row.item_id, row.answer_key): row.canonical_answer for row in human.itertuples()
    }
    human_candidates: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for (panel_id, item_id), group in human.groupby(["panel_id", "item_id"]):
        human_candidates[(panel_id, item_id)] = [
            (row.answer_key, row.canonical_answer) for row in group.itertuples()
        ]

    normalized_rows: list[dict[str, Any]] = []
    unresolved_rows: list[dict[str, Any]] = []
    for row in frame.to_dict(orient="records"):
        panel_id = row["panel_id"]
        item_id = row["item_id"]
        answer_key = row["answer_key"]
        canonical_answer = ""
        status = "invalid"

        if answer_key:
            alias_matches = aliases[
                ((aliases["panel_id"].fillna("") == panel_id) | (aliases["panel_id"].fillna("") == ""))
                & ((aliases["item_id"].fillna("") == item_id) | (aliases["item_id"].fillna("") == ""))
                & (aliases["surface_key"] == answer_key)
            ]
            if not alias_matches.empty:
                canonical_answer = str(alias_matches.iloc[0]["canonical_answer"])
                status = "alias"
            elif (panel_id, item_id, answer_key) in human_lookup:
                canonical_answer = human_lookup[(panel_id, item_id, answer_key)]
                status = "human_key"
            else:
                candidates = human_candidates.get((panel_id, item_id), [])
                candidate_keys = [candidate_key for candidate_key, _ in candidates if candidate_key]
                best = process.extractOne(answer_key, candidate_keys, scorer=fuzz.ratio) if candidate_keys else None
                if best and best[1] >= config.normalization.fuzzy_match_threshold:
                    matched_key = best[0]
                    for candidate_key, candidate_answer in candidates:
                        if candidate_key == matched_key:
                            canonical_answer = candidate_answer
                            status = "fuzzy"
                            break
                elif config.normalization.allow_unmapped:
                    canonical_answer = row["response_clean"]
                    status = "unmapped"
                else:
                    status = "unmapped"

        normalized = {
            **row,
            "canonical_answer": canonical_answer,
            "normalization_status": status,
        }
        normalized_rows.append(normalized)
        if status in {"invalid", "unmapped"}:
            unresolved_rows.append(normalized)

    normalized_frame = pd.DataFrame(normalized_rows)
    normalized_frame.to_csv(run_dir / "normalized_outputs.csv", index=False)
    pd.DataFrame(unresolved_rows).to_csv(run_dir / "unresolved_queue.csv", index=False)

    manifest = read_json(run_dir / "run_manifest.json")
    manifest["normalization_completed"] = True
    manifest["unresolved_count"] = len(unresolved_rows)
    manifest["raw_record_count"] = len(raw_rows)
    manifest["deduped_raw_record_count"] = len(deduped_rows)
    write_json(run_dir / "run_manifest.json", manifest)

    if unresolved_rows and not config.normalization.allow_unmapped:
        raise RuntimeError(
            "Normalization produced unresolved outputs. Review unresolved_queue.csv or set allow_unmapped=true."
        )
    LOGGER.info("Normalized outputs into %s", run_dir)
    return run_dir
