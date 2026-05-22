#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from dataclasses import replace
from pathlib import Path

import pandas as pd

from coordbench.analysis import analyze_run
from coordbench.normalize import normalize_run
from coordbench.runner import run_sampling
from coordbench.utils.files import read_json

PRIMARY_BASE_URL = "https://api.mytokenland.com/v1"
FALLBACK_BASE_URL = "https://api.mytokenland.com"


def discover_source_runs(run_root: Path) -> list[Path]:
    runs: list[Path] = []
    for manifest in sorted(run_root.glob("*/run_manifest.json")):
        run_dir = manifest.parent
        name = run_dir.name
        if name.startswith("track_b_") or "temp_test" in name:
            continue
        if not (run_dir / "raw_generations.jsonl").exists():
            continue
        cand = run_dir / "round2_candidates.csv"
        if not cand.exists():
            continue
        cdf = pd.read_csv(cand)
        if cdf.empty:
            continue
        runs.append(run_dir.resolve())
    return runs


def primary_model_for_round1(run_dir: Path) -> str:
    raw = pd.read_json(run_dir / "raw_generations.jsonl", lines=True)
    r1 = raw[raw["round_index"] == 1]
    if r1.empty:
        raise RuntimeError(f"No round1 rows in {run_dir}")
    mode = r1["model"].astype(str).mode()
    return str(mode.iloc[0]) if not mode.empty else str(r1.iloc[0]["model"])


def copy_round1_only(src_run: Path, dst_run: Path) -> str:
    dst_run.mkdir(parents=True, exist_ok=True)
    manifest = read_json(src_run / "run_manifest.json")
    manifest["run_id"] = dst_run.name
    with (dst_run / "run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    raw = pd.read_json(src_run / "raw_generations.jsonl", lines=True)
    r1 = raw[raw["round_index"] == 1].copy()
    model = primary_model_for_round1(src_run)
    r1.to_json(dst_run / "raw_generations.jsonl", orient="records", lines=True, force_ascii=False)
    return model


def patch_load_config(*, base_url: str, api_key_env: str, model_name: str):
    import coordbench.analysis as analysis_module
    import coordbench.normalize as normalize_module
    import coordbench.runner as runner_module

    original_runner = runner_module.load_config
    original_normalize = normalize_module.load_config
    original_analyze = analysis_module.load_config

    def _patched(path, *_args, **_kwargs):
        cfg = original_runner(path)
        providers = {name: replace(provider, enabled=False) for name, provider in cfg.providers.items()}
        anth = cfg.providers["anthropic"]
        providers["anthropic"] = replace(
            anth,
            enabled=True,
            model=model_name,
            api_key_env=api_key_env,
            extra={
                **anth.extra,
                "base_url": base_url,
                "compat_mode": "anthropic",
                "anthropic_version": "2023-06-01",
            },
        )
        return replace(cfg, providers=providers)

    runner_module.load_config = _patched  # type: ignore[method-assign]
    normalize_module.load_config = _patched  # type: ignore[method-assign]
    analysis_module.load_config = _patched  # type: ignore[method-assign]
    return (runner_module, normalize_module, analysis_module, original_runner, original_normalize, original_analyze)


def restore_load_config(state) -> None:
    runner_module, normalize_module, analysis_module, original_runner, original_normalize, original_analyze = state
    runner_module.load_config = original_runner  # type: ignore[method-assign]
    normalize_module.load_config = original_normalize  # type: ignore[method-assign]
    analysis_module.load_config = original_analyze  # type: ignore[method-assign]


def run_one_clean(
    src_run: Path,
    dst_run: Path,
    config_path: Path,
    base_url: str,
    api_key_env: str,
) -> tuple[bool, str]:
    model_name = copy_round1_only(src_run, dst_run)
    state = patch_load_config(base_url=base_url, api_key_env=api_key_env, model_name=model_name)
    try:
        normalize_run(config_path, dst_run, allow_unmapped_override=False)
    except RuntimeError as exc:
        if "unresolved outputs" not in str(exc).lower():
            restore_load_config(state)
            return (False, f"normalize round1 failed: {exc}")
    analyze_run(config_path, dst_run)
    cands = pd.read_csv(dst_run / "round2_candidates.csv")
    item_ids = cands["item_id"].dropna().astype(str).tolist() if not cands.empty else []
    if not item_ids:
        restore_load_config(state)
        return (True, f"no candidates (model={model_name})")

    try:
        run_sampling(config_path, run_dir=dst_run, round_index=2, item_ids=item_ids)
        try:
            normalize_run(config_path, dst_run, allow_unmapped_override=False)
        except RuntimeError as exc:
            if "unresolved outputs" not in str(exc).lower():
                raise
        analyze_run(config_path, dst_run)
        man = read_json(dst_run / "run_manifest.json")
        # Strict cleanliness gate for round2: each language cell should be complete.
        coord_cell_path = dst_run / "coord_cell_completeness.csv"
        if coord_cell_path.exists():
            cc = pd.read_csv(coord_cell_path)
            r2 = cc[cc["round_index"] == 2].copy()
            if not r2.empty:
                if ("is_complete" in r2.columns) and (not r2["is_complete"].fillna(False).all()):
                    incomplete = r2[~r2["is_complete"].fillna(False)][
                        ["item_id", "prompt_language", "successful_samples", "expected_samples", "completion_rate"]
                    ]
                    raise RuntimeError(
                        "round2 incomplete cells: "
                        + "; ".join(
                            f"{row.item_id}/{row.prompt_language} {int(row.successful_samples)}/{int(row.expected_samples)}"
                            for row in incomplete.itertuples()
                        )
                    )
        restore_load_config(state)
        return (
            True,
            f"ok model={model_name} cand={len(item_ids)} round2_count={man.get('round2_candidate_count', '?')}",
        )
    except Exception as exc:  # noqa: BLE001
        restore_load_config(state)
        return (False, f"round2 failed model={model_name}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run clean round2 in fresh run dirs.")
    parser.add_argument("--source-root", default="results/runs_s50")
    parser.add_argument("--dest-root", default="results/runs_s50_clean_round2")
    parser.add_argument("--config", default="configs/study2_british_en_zh.yaml")
    parser.add_argument("--api-key-env", default="SUM_API_KEY")
    args = parser.parse_args()

    if not os.environ.get(args.api_key_env):
        raise SystemExit(f"{args.api_key_env} is empty.")

    project_root = Path(__file__).resolve().parents[1]
    source_root = (project_root / args.source_root).resolve()
    dest_root = (project_root / args.dest_root).resolve()
    config_path = (project_root / args.config).resolve()
    dest_root.mkdir(parents=True, exist_ok=True)

    runs = discover_source_runs(source_root)
    if not runs:
        raise SystemExit("No source runs with round2 candidates found.")

    print(f"Source runs: {len(runs)}")
    print(f"Dest root: {dest_root}")
    print(f"Config: {config_path}")
    print(f"API key env: {args.api_key_env}")
    print(f"Primary URL: {PRIMARY_BASE_URL}")
    print(f"Fallback URL: {FALLBACK_BASE_URL}")
    print("")

    failures: list[str] = []
    for src in runs:
        dst = dest_root / f"{src.name}__cleanr2"
        print(f"=== {src.name} -> {dst.name} ===")
        ok, msg = run_one_clean(src, dst, config_path, PRIMARY_BASE_URL, args.api_key_env)
        if ok:
            print(msg)
            continue
        print(f"primary failed: {msg}")
        ok2, msg2 = run_one_clean(src, dst, config_path, FALLBACK_BASE_URL, args.api_key_env)
        if ok2:
            print(f"fallback ok: {msg2}")
        else:
            print(f"fallback failed: {msg2}")
            failures.append(src.name)

    print("")
    if failures:
        print(f"Completed with failures ({len(failures)}): {', '.join(failures)}")
        return 1
    print("Completed clean round2 for all source runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
