import json
from pathlib import Path

import pandas as pd

from coordbench.runner import run_sampling


def _write_runner_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "providers:",
                "  mock:",
                "    enabled: true",
                "    model: mock-v1",
                "    api_key_env: ''",
                "    concurrency: 1",
                "    max_retries: 1",
                "    temperature: 1.0",
                "    max_output_tokens: 8",
                "sampling:",
                "  panel_id: study2_british_within",
                "  answer_language: English",
                "  prompt_languages: [en]",
                "  round1_samples: 2",
                "  round2_samples: 1",
                "  enable_round2: false",
                "  round2_trigger: cross_lingual_top1_mismatch",
                "  random_seed: 1",
                "normalization:",
                f"  alias_path: {tmp_path.as_posix()}/aliases.csv",
                "  allow_unmapped: true",
                "  fuzzy_match_threshold: 95",
                "analysis:",
                "  bootstrap_resamples: 10",
                "  item_bootstrap_resamples: 10",
                "outputs:",
                f"  run_root: {tmp_path.as_posix()}/runs",
                f"  cache_root: {tmp_path.as_posix()}/cache",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "aliases.csv").write_text("panel_id,item_id,surface_form,canonical_answer,notes\n", encoding="utf-8")
    return config_path


def _write_panel_items(snapshot_dir: Path, *, item_text: str) -> None:
    snapshot_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "panel_id": "study2_british_within",
                "study_id": "study2",
                "respondent_group": "british",
                "target_group": "british",
                "relation": "within",
                "item_id": "study2_item_01",
                "item_number": 1,
                "item_text_en": item_text,
                "item_text_zh": "说出一座城市",
            }
        ]
    ).to_csv(snapshot_dir / "panel_items.csv", index=False)


def test_run_sampling_resumes_without_duplicate_rows_and_keeps_bound_snapshot(tmp_path: Path, monkeypatch):
    prepared_root = tmp_path / "prepared"
    first_snapshot = prepared_root / "snapshot_a"
    second_snapshot = prepared_root / "snapshot_b"
    _write_panel_items(first_snapshot, item_text="Name a city")
    _write_panel_items(second_snapshot, item_text="Different item text")

    config_path = _write_runner_config(tmp_path)
    run_dir = tmp_path / "runs" / "resume-run"

    monkeypatch.setattr("coordbench.runner.latest_prepared_snapshot_or_raise", lambda: first_snapshot)
    monkeypatch.setattr("coordbench.run_state.prepared_root", lambda: prepared_root)

    run_sampling(config_path, run_dir=run_dir)
    first_rows = [json.loads(line) for line in (run_dir / "raw_generations.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(first_rows) == 2

    monkeypatch.setattr("coordbench.runner.latest_prepared_snapshot_or_raise", lambda: second_snapshot)
    run_sampling(config_path, run_dir=run_dir)

    second_rows = [json.loads(line) for line in (run_dir / "raw_generations.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(second_rows) == 2
    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["prepared_snapshot_id"] == "snapshot_a"
