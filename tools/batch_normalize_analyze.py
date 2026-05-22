#!/usr/bin/env python3
"""Batch normalize + analyze for existing run directories."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from coordbench.analysis import analyze_run
from coordbench.normalize import normalize_run
from coordbench.paths import aliases_path
from coordbench.utils.files import read_json


def _discover_runs(run_root: Path, exclude_temp: bool) -> list[Path]:
    runs: list[Path] = []
    for manifest_path in sorted(run_root.glob("**/run_manifest.json")):
        run_dir = manifest_path.parent
        if exclude_temp and "temp_test" in str(run_dir):
            continue
        if not (run_dir / "raw_generations.jsonl").exists():
            continue
        runs.append(run_dir.resolve())
    return runs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", default="results/runs_s50")
    parser.add_argument("--config", default="configs/study2_british_en_zh.yaml")
    parser.add_argument("--include-temp", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    run_root = (project_root / args.run_root).resolve()
    config_path = (project_root / args.config).resolve()
    alias_path = aliases_path().resolve()

    import coordbench.normalize as normalize_module

    original_load = normalize_module.load_config

    def _load_with_alias(path, *_a, **_k):
        loaded = original_load(path)
        return replace(
            loaded,
            normalization=replace(
                loaded.normalization,
                alias_path=alias_path,
                allow_unmapped=False,
            ),
        )

    runs = _discover_runs(run_root, exclude_temp=not args.include_temp)
    if not runs:
        raise SystemExit(f"No runs under {run_root}")

    print(f"Config: {config_path}")
    print(f"Alias:  {alias_path}")
    print(f"Runs:   {len(runs)}\n")

    normalize_module.load_config = _load_with_alias  # type: ignore[method-assign]
    try:
        for run_dir in runs:
            name = run_dir.name
            print(f"=== {name} ===")
            try:
                normalize_run(config_path, run_dir, allow_unmapped_override=False)
                norm_status = "ok"
            except RuntimeError as exc:
                if "unresolved outputs" in str(exc).lower():
                    manifest = read_json(run_dir / "run_manifest.json")
                    norm_status = f"ok_with_unresolved({manifest.get('unresolved_count', '?')})"
                else:
                    print(f"  normalize FAILED: {exc}")
                    continue
            except Exception as exc:  # noqa: BLE001
                print(f"  normalize FAILED: {exc}")
                continue
            print(f"  normalize: {norm_status}")

            try:
                analyze_run(config_path, run_dir)
                manifest = read_json(run_dir / "run_manifest.json")
                r2 = manifest.get("round2_candidate_count", "?")
                print(f"  analyze: ok (round2_candidates={r2})")
            except Exception as exc:  # noqa: BLE001
                print(f"  analyze FAILED: {exc}")
    finally:
        normalize_module.load_config = original_load  # type: ignore[method-assign]

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
