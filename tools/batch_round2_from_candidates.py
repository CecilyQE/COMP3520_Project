#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def _discover_runs(run_root: Path) -> list[Path]:
    runs: list[Path] = []
    for manifest_path in sorted(run_root.glob("**/run_manifest.json")):
        run_dir = manifest_path.parent
        if "temp_test" in str(run_dir):
            continue
        if not (run_dir / "round2_candidates.csv").exists():
            continue
        if not (run_dir / "raw_generations.jsonl").exists():
            continue
        runs.append(run_dir.resolve())
    return runs


def _patch_load_config_for_round2(
    *,
    base_url: str,
    api_key_env: str,
    model_name: str,
):
    import coordbench.analysis as analysis_module
    import coordbench.normalize as normalize_module
    import coordbench.runner as runner_module

    original_runner = runner_module.load_config
    original_normalize = normalize_module.load_config
    original_analyze = analysis_module.load_config

    def _patched(path, *_args, **_kwargs):
        cfg = original_runner(path)
        providers = {}
        for name, provider in cfg.providers.items():
            providers[name] = replace(provider, enabled=False)
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


def _restore_load_config(patch_tuple) -> None:
    runner_module, normalize_module, analysis_module, original_runner, original_normalize, original_analyze = patch_tuple
    runner_module.load_config = original_runner  # type: ignore[method-assign]
    normalize_module.load_config = original_normalize  # type: ignore[method-assign]
    analysis_module.load_config = original_analyze  # type: ignore[method-assign]


def _run_round2_for_run(run_dir: Path, config_path: Path) -> tuple[bool, str]:
    candidates_path = run_dir / "round2_candidates.csv"
    candidates = pd.read_csv(candidates_path)
    item_ids = candidates["item_id"].dropna().astype(str).tolist() if not candidates.empty else []
    if not item_ids:
        return (True, "skip(no candidates)")
    run_sampling(config_path, run_dir=run_dir, round_index=2, item_ids=item_ids)
    try:
        normalize_run(config_path, run_dir, allow_unmapped_override=False)
        norm_status = "normalize:ok"
    except RuntimeError as exc:
        if "unresolved outputs" in str(exc).lower():
            manifest = read_json(run_dir / "run_manifest.json")
            norm_status = f"normalize:ok_with_unresolved({manifest.get('unresolved_count', '?')})"
        else:
            raise
    analyze_run(config_path, run_dir)
    manifest = read_json(run_dir / "run_manifest.json")
    return (True, f"{norm_status}; round2_candidates={manifest.get('round2_candidate_count', '?')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run round2 for all runs using existing round2_candidates.csv")
    parser.add_argument("--run-root", default="results/runs_s50")
    parser.add_argument("--config", default="configs/study2_british_en_zh.yaml")
    parser.add_argument("--api-key-env", default="SUM_API_KEY")
    parser.add_argument("--model-env", default="ANTHROPIC_MODEL")
    parser.add_argument("--model-override", default="")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    run_root = (project_root / args.run_root).resolve()
    config_path = (project_root / args.config).resolve()
    model_name = args.model_override or os.environ.get(args.model_env, "")
    if not model_name:
        raise SystemExit(
            f"Model not set. Provide --model-override or set {args.model_env} in env/.env."
        )
    if not os.environ.get(args.api_key_env):
        raise SystemExit(f"{args.api_key_env} is empty. Please set it before running.")

    runs = _discover_runs(run_root)
    if not runs:
        raise SystemExit(f"No eligible runs found under {run_root}")

    print(f"Runs found: {len(runs)}")
    print(f"Config: {config_path}")
    print(f"Provider: anthropic")
    print(f"Model: {model_name}")
    print(f"API key env: {args.api_key_env}")
    print(f"Primary base URL: {PRIMARY_BASE_URL}")
    print(f"Fallback base URL: {FALLBACK_BASE_URL}")
    print("")

    for base_url in (PRIMARY_BASE_URL, FALLBACK_BASE_URL):
        print(f"=== Round2 attempt with base URL: {base_url} ===")
        patch_tuple = _patch_load_config_for_round2(
            base_url=base_url,
            api_key_env=args.api_key_env,
            model_name=model_name,
        )
        try:
            all_ok = True
            for run_dir in runs:
                name = run_dir.name
                try:
                    ok, msg = _run_round2_for_run(run_dir, config_path)
                    print(f"{name}: {msg}")
                    all_ok = all_ok and ok
                except Exception as exc:  # noqa: BLE001
                    print(f"{name}: FAILED ({exc})")
                    all_ok = False
            if all_ok:
                print("\nAll runs finished on this base URL.")
                return 0
            print("\nSome runs failed on this base URL, trying fallback if available...")
        finally:
            _restore_load_config(patch_tuple)

    print("\nCompleted with failures after fallback.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
