#!/usr/bin/env python3
"""Re-normalize runs with current alias table and aggregate round-1 unmapped surface forms."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

import pandas as pd

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


def _renormalize(run_dir: Path, alias_path: Path) -> bool:
    import coordbench.normalize as normalize_module

    # Use stable benchmark config (manifest configs may reference missing env vars).
    config_path = str((Path(__file__).resolve().parents[1] / "configs/study2_british_en_zh.yaml").resolve())

    original_load = normalize_module.load_config
    resolved_alias = alias_path.resolve()

    def _load_with_alias(path, *_args, **_kwargs):
        loaded = original_load(path)
        return replace(
            loaded,
            normalization=replace(
                loaded.normalization,
                alias_path=resolved_alias,
                allow_unmapped=False,
            ),
        )

    normalize_module.load_config = _load_with_alias  # type: ignore[method-assign]
    try:
        normalize_run(config_path, run_dir, allow_unmapped_override=False)
        return True
    except RuntimeError as exc:
        if "unresolved outputs" not in str(exc).lower():
            raise
        return False
    finally:
        normalize_module.load_config = original_load  # type: ignore[method-assign]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-root",
        default="results/runs_s50",
        help="Directory containing experiment run folders.",
    )
    parser.add_argument(
        "--alias-file",
        default=None,
        help="Alias CSV (default: data/aliases/default_aliases.csv).",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=4,
        help="Report surface forms with total count strictly greater than (default: 3 → min-count 4).",
    )
    parser.add_argument(
        "--skip-renormalize",
        action="store_true",
        help="Only aggregate existing normalized_outputs.csv (no re-normalize).",
    )
    parser.add_argument("--include-temp", action="store_true")
    parser.add_argument(
        "--output",
        default="results/round1_unmapped_gt3_current_aliases.csv",
        help="Output CSV path.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    run_root = (project_root / args.run_root).resolve()
    alias_path = Path(args.alias_file).resolve() if args.alias_file else aliases_path()
    out_path = (project_root / args.output).resolve()

    runs = _discover_runs(run_root, exclude_temp=not args.include_temp)
    if not runs:
        raise SystemExit(f"No runs found under {run_root}")

    answer_counts: Counter[tuple[str, str]] = Counter()
    answer_models: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    answer_runs: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    total_r1 = 0
    unmapped_r1 = 0
    failed_normalize: list[str] = []

    for run_dir in runs:
        if not args.skip_renormalize:
            ok = _renormalize(run_dir, alias_path)
            if not ok:
                failed_normalize.append(run_dir.name)

        norm_path = run_dir / "normalized_outputs.csv"
        if not norm_path.exists():
            continue
        frame = pd.read_csv(norm_path, low_memory=False)
        if "round_index" not in frame.columns:
            continue
        r1 = frame[frame["round_index"].astype(int) == 1]
        total_r1 += len(r1)
        if "normalization_status" not in r1.columns:
            continue
        bad = r1[r1["normalization_status"].isin(["unmapped", "invalid"])]
        unmapped_r1 += len(bad)

        for row in bad.itertuples():
            raw_surface = getattr(row, "response_clean", "") or getattr(row, "parsed_answer", "") or ""
            if pd.isna(raw_surface):
                raw_surface = ""
            surface = str(raw_surface).strip()
            if not surface or surface.lower() == "nan":
                surface = "<empty>"
            item_id = str(row.item_id)
            key = (item_id, surface)
            answer_counts[key] += 1
            answer_models[key].add(str(getattr(row, "model", run_dir.name)))
            answer_runs[key].add(run_dir.name)

    min_count = int(args.min_count)
    filtered = [(k, c) for k, c in answer_counts.items() if c >= min_count]
    filtered.sort(key=lambda x: (-x[1], x[0][0], x[0][1]))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["count", "item_id", "response_clean", "num_models", "num_runs", "models", "runs"]
        )
        for (item_id, surface), count in filtered:
            writer.writerow(
                [
                    count,
                    item_id,
                    surface,
                    len(answer_models[(item_id, surface)]),
                    len(answer_runs[(item_id, surface)]),
                    ";".join(sorted(answer_models[(item_id, surface)])),
                    ";".join(sorted(answer_runs[(item_id, surface)])),
                ]
            )

    print(f"Runs: {len(runs)} | Re-normalize failures (unresolved, expected): {len(failed_normalize)}")
    print(f"Round-1 rows: {total_r1} | unmapped+invalid: {unmapped_r1}")
    print(f"Surface forms with count >= {min_count}: {len(filtered)}")
    print(f"Wrote {out_path}\n")
    print(f"{'count':>6}  {'item_id':<22}  response_clean")
    print("-" * 90)
    for (item_id, surface), count in filtered[:60]:
        surf = surface if len(surface) <= 55 else surface[:52] + "..."
        print(f"{count:>6}  {item_id:<22}  {surf}")
    if len(filtered) > 60:
        print(f"... and {len(filtered) - 60} more (see CSV)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
