#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, replace
from pathlib import Path

import pandas as pd

from coordbench.analysis import analyze_run
from coordbench.normalize import normalize_run
from coordbench.runner import run_sampling
from coordbench.utils.files import read_json


PRIMARY_BASE_URL = "https://api.mytokenland.com/v1"
FALLBACK_BASE_URL = "https://api.mytokenland.com"

# OpenAIProvider posts to {base_url}/chat/completions (base usually includes /v1 where applicable).
DEFAULT_GLM_OPENAI_BASE = "https://open.bigmodel.cn/api/paas/v4"
DEFAULT_DEEPSEEK_OPENAI_BASE = "https://api.deepseek.com"
DEFAULT_MINIMAX_OPENAI_BASE = "https://api.minimax.io/v1"
DEFAULT_QWEN_OPENAI_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"


@dataclass(frozen=True, slots=True)
class _Transport:
    api_key_env: str
    base_url: str
    label: str
    backend: str = "openai"  # "openai" (OpenAI-compatible HTTP) or "gemini" (native GeminiProvider)


def _env_nonempty(name: str) -> bool:
    return bool(str(os.environ.get(name, "") or "").strip())


def _is_glm_model(model: str) -> bool:
    n = str(model).lower()
    return n.startswith("glm") or "glm-" in n


def _is_openai_style_model(model: str) -> bool:
    """Heuristic: models that should use OPENAI_API_KEY / official or OpenAI-compatible URL."""
    n = str(model).lower()
    if _is_glm_model(model):
        return False
    return any(
        n.startswith(p)
        for p in (
            "gpt-",
            "gpt",
            "o1",
            "o3",
            "o4",
            "chatgpt",
            "text-davinci",
        )
    ) or "gpt-4" in n or "gpt-5" in n or "gpt-3" in n


def _is_deepseek_model(model: str) -> bool:
    n = str(model).lower()
    return "deepseek" in n or n == "deepseek-chat"


def _is_minimax_model(model: str) -> bool:
    return "minimax" in str(model).lower()


def _is_qwen_model(model: str) -> bool:
    return "qwen" in str(model).lower()


def _is_gemini_model(model: str) -> bool:
    return "gemini" in str(model).lower()


def _is_qwen_ds_minimax_model(model: str) -> bool:
    """Runs that should use Qwen / DeepSeek / MiniMax .env keys (parallel batch lane A)."""
    return _is_qwen_model(model) or _is_deepseek_model(model) or _is_minimax_model(model)


def _is_openai_or_glm_model(model: str) -> bool:
    """Round-1 model is one we treat as GLM or OpenAI-style (vendor key routing)."""
    return _is_glm_model(model) or _is_openai_style_model(model)


def transports_for_model(
    model: str,
    *,
    default_key_env: str,
    gateway_primary: str,
    gateway_fallback: str,
    use_vendor_keys: bool = True,
) -> list[_Transport]:
    """Ordered attempts: vendor-native keys first, then SUM gateway URL(s)."""
    out: list[_Transport] = []
    seen: set[tuple[str, str]] = set()

    def add(key_env: str, base: str, label: str, *, backend: str = "openai") -> None:
        if not _env_nonempty(key_env):
            return
        if backend == "openai" and not str(base).strip():
            return
        b = str(base).rstrip("/") if backend == "openai" else ""
        k = (key_env, b, backend)
        if k in seen:
            return
        seen.add(k)
        out.append(_Transport(api_key_env=key_env, base_url=b, label=label, backend=backend))

    if use_vendor_keys:
        if _is_glm_model(model) and _env_nonempty("GLM_API_KEY"):
            glm_base = str(os.environ.get("GLM_BASE_URL", "") or "").strip() or DEFAULT_GLM_OPENAI_BASE
            add("GLM_API_KEY", glm_base, "glm_openai_compat")

        if _is_openai_style_model(model) and _env_nonempty("OPENAI_API_KEY"):
            oa_base = str(os.environ.get("OPENAI_BASE_URL", "") or "").strip() or "https://api.openai.com/v1"
            add("OPENAI_API_KEY", oa_base, "openai_official_or_env_base")

        if _is_deepseek_model(model) and _env_nonempty("DEEPSEEK_API_KEY"):
            ds_base = (
                str(os.environ.get("DEEPSEEK_BASE_URL", "") or "").strip() or DEFAULT_DEEPSEEK_OPENAI_BASE
            )
            add("DEEPSEEK_API_KEY", ds_base, "deepseek_openai_compat")

        if _is_minimax_model(model) and _env_nonempty("MINIMAX_API_KEY"):
            mm_base = (
                str(os.environ.get("MINIMAX_BASE_URL", "") or "").strip() or DEFAULT_MINIMAX_OPENAI_BASE
            )
            add("MINIMAX_API_KEY", mm_base, "minimax_openai_compat")

        if _is_qwen_model(model) and _env_nonempty("QWEN_API_KEY"):
            qw_base = str(os.environ.get("QWEN_BASE_URL", "") or "").strip() or DEFAULT_QWEN_OPENAI_BASE
            add("QWEN_API_KEY", qw_base, "qwen_dashscope_openai_compat")

        if _is_gemini_model(model) and _env_nonempty("GEMINI_API_KEY"):
            add("GEMINI_API_KEY", "", "gemini_official", backend="gemini")

    add(default_key_env, gateway_primary, "sum_gateway_primary")
    if gateway_fallback:
        add(default_key_env, gateway_fallback, "sum_gateway_fallback")
    return out


def discover_source_runs(run_root: Path) -> list[Path]:
    runs: list[Path] = []
    for manifest_path in sorted(run_root.glob("*/run_manifest.json")):
        run_dir = manifest_path.parent
        name = run_dir.name
        if name.startswith("track_b_") or "temp_test" in name:
            continue
        if not (run_dir / "raw_generations.jsonl").exists():
            continue
        cand_path = run_dir / "round2_candidates.csv"
        if not cand_path.exists():
            continue
        try:
            candidates = pd.read_csv(cand_path)
        except pd.errors.EmptyDataError:
            continue
        if candidates.empty:
            continue
        runs.append(run_dir.resolve())
    return runs


def primary_round1_identity(run_dir: Path) -> tuple[str, str]:
    raw = pd.read_json(run_dir / "raw_generations.jsonl", lines=True)
    r1 = raw[raw["round_index"] == 1].copy()
    if r1.empty:
        raise RuntimeError(f"No Round 1 rows in {run_dir}")
    provider = str(r1["provider"].astype(str).mode().iloc[0])
    model = str(r1["model"].astype(str).mode().iloc[0])
    return provider, model


def copy_round1_only(src_run: Path, dst_run: Path) -> None:
    dst_run.mkdir(parents=True, exist_ok=True)
    manifest = read_json(src_run / "run_manifest.json")
    manifest["run_id"] = dst_run.name
    manifest["completed_rounds"] = [1]
    manifest["analysis_completed"] = False
    manifest["normalization_completed"] = False
    with (dst_run / "run_manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)

    raw = pd.read_json(src_run / "raw_generations.jsonl", lines=True)
    r1 = raw[raw["round_index"] == 1].copy()
    r1.to_json(dst_run / "raw_generations.jsonl", orient="records", lines=True, force_ascii=False)


def prepare_dst_run(src_run: Path, dst_run: Path) -> None:
    """Seed Round-1 into dest unless dest already has Round-2 rows (resume without wiping)."""
    raw_path = dst_run / "raw_generations.jsonl"
    if raw_path.exists():
        try:
            existing = pd.read_json(raw_path, lines=True)
            r2_count = int((existing["round_index"] == 2).sum())
        except (ValueError, KeyError, pd.errors.EmptyDataError):
            r2_count = 0
        if r2_count > 0:
            print(
                f"RESUME {src_run.name}: keep existing raw ({r2_count} Round-2 rows); "
                "run_sampling will fill missing cells only.",
                flush=True,
            )
            dst_run.mkdir(parents=True, exist_ok=True)
            if not (dst_run / "run_manifest.json").exists():
                manifest = read_json(src_run / "run_manifest.json")
                manifest["run_id"] = dst_run.name
                with (dst_run / "run_manifest.json").open("w", encoding="utf-8") as handle:
                    json.dump(manifest, handle, ensure_ascii=False, indent=2)
            return
    copy_round1_only(src_run, dst_run)


def patch_universal_openai_model(
    *,
    base_url: str,
    api_key_env: str,
    model_name: str,
    max_retries: int,
    max_concurrency: int,
):
    import coordbench.analysis as analysis_module
    import coordbench.normalize as normalize_module
    import coordbench.runner as runner_module

    original_runner = runner_module.load_config
    original_normalize = normalize_module.load_config
    original_analyze = analysis_module.load_config

    def _patched(path, *_args, **_kwargs):
        cfg = original_runner(path)
        providers = {name: replace(provider, enabled=False) for name, provider in cfg.providers.items()}
        openai_provider = cfg.providers["openai"]
        providers["openai"] = replace(
            openai_provider,
            enabled=True,
            model=model_name,
            api_key_env=api_key_env,
            max_retries=max_retries,
            concurrency=min(openai_provider.concurrency, max(1, int(max_concurrency))),
            extra={
                **openai_provider.extra,
                "base_url": base_url,
            },
        )
        return replace(cfg, providers=providers)

    runner_module.load_config = _patched  # type: ignore[method-assign]
    normalize_module.load_config = _patched  # type: ignore[method-assign]
    analysis_module.load_config = _patched  # type: ignore[method-assign]
    return (runner_module, normalize_module, analysis_module, original_runner, original_normalize, original_analyze)


def patch_universal_gemini_model(
    *,
    api_key_env: str,
    model_name: str,
    max_retries: int,
    max_concurrency: int,
):
    import coordbench.analysis as analysis_module
    import coordbench.normalize as normalize_module
    import coordbench.runner as runner_module

    original_runner = runner_module.load_config
    original_normalize = normalize_module.load_config
    original_analyze = analysis_module.load_config

    def _patched(path, *_args, **_kwargs):
        cfg = original_runner(path)
        gemini_cfg_path = Path(path).resolve().parent / "gemini2.5flash.yaml"
        if not gemini_cfg_path.exists():
            gemini_cfg_path = Path(__file__).resolve().parents[1] / "configs" / "gemini2.5flash.yaml"
        gemini_provider = original_runner(gemini_cfg_path).providers["gemini"]
        providers = {name: replace(provider, enabled=False) for name, provider in cfg.providers.items()}
        providers["gemini"] = replace(
            gemini_provider,
            enabled=True,
            model=model_name,
            api_key_env=api_key_env,
            max_retries=max_retries,
            concurrency=min(gemini_provider.concurrency, max(1, int(max_concurrency))),
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


def normalize_analyze(run_dir: Path, config_path: Path) -> None:
    try:
        normalize_run(config_path, run_dir, allow_unmapped_override=False)
    except RuntimeError as exc:
        if "unresolved outputs" not in str(exc).lower():
            raise
    analyze_run(config_path, run_dir)


def candidate_items(run_dir: Path) -> list[str]:
    candidates = pd.read_csv(run_dir / "round2_candidates.csv")
    if candidates.empty:
        return []
    return candidates["item_id"].dropna().astype(str).tolist()


def candidate_items_from_source(src_run: Path) -> list[str]:
    """Round-2 item list from the baseline run (before dest normalize recomputes candidates)."""
    cand_path = src_run / "round2_candidates.csv"
    if not cand_path.exists():
        return []
    try:
        candidates = pd.read_csv(cand_path)
    except pd.errors.EmptyDataError:
        return []
    if candidates.empty:
        return []
    return candidates["item_id"].dropna().astype(str).tolist()


def write_preflight(
    dst_run: Path, *, src_run: Path, provider: str, model: str, items: list[str], round2_provider: str = "openai"
) -> None:
    frame = pd.DataFrame(
        [
            {
                "source_run": src_run.name,
                "dest_run": dst_run.name,
                "round1_provider": provider,
                "round2_provider": round2_provider,
                "round1_model": model,
                "round2_model": model,
                "item_id": item,
            }
            for item in items
        ]
    )
    frame.to_csv(dst_run / "round2_preflight_model_item_check.csv", index=False)


def postflight_check(
    dst_run: Path,
    *,
    expected_model: str,
    expected_items: list[str],
    expected_samples_per_cell: int,
) -> tuple[bool, str]:
    raw = pd.read_json(dst_run / "raw_generations.jsonl", lines=True)
    r2 = raw[raw["round_index"] == 2].copy()
    expected_set = set(expected_items)
    actual_items = set(r2["item_id"].dropna().astype(str).unique())
    actual_models = set(r2["model"].dropna().astype(str).unique())
    valid = r2[
        r2["error"].isna()
        & r2["response_text"].fillna("").astype(str).str.strip().ne("")
    ].copy()
    per_cell = (
        r2.groupby(["model", "item_id", "prompt_language"], dropna=False)
        .size()
        .reset_index(name="raw_count")
        .sort_values(["model", "item_id", "prompt_language"])
    )
    valid_counts = (
        valid.groupby(["model", "item_id", "prompt_language"], dropna=False)
        .size()
        .reset_index(name="valid_count")
    )
    per_cell = per_cell.merge(valid_counts, on=["model", "item_id", "prompt_language"], how="left")
    per_cell["valid_count"] = per_cell["valid_count"].fillna(0).astype(int)
    per_cell.to_csv(dst_run / "round2_postflight_model_item_counts.csv", index=False)
    expected_cells = {(expected_model, item, lang) for item in expected_items for lang in ("en", "zh")}
    actual_valid_counts = {
        (str(row.model), str(row.item_id), str(row.prompt_language)): int(row.valid_count)
        for row in per_cell.itertuples()
    }
    incomplete = [
        f"{model}/{item}/{lang}={actual_valid_counts.get((model, item, lang), 0)}/{expected_samples_per_cell}"
        for model, item, lang in sorted(expected_cells)
        if actual_valid_counts.get((model, item, lang), 0) < expected_samples_per_cell
    ]
    ok = actual_items == expected_set and actual_models == {expected_model} and not incomplete
    msg = (
        f"expected_model={expected_model}; actual_models={sorted(actual_models)}; "
        f"expected_items={sorted(expected_set)}; actual_items={sorted(actual_items)}; "
        f"incomplete_valid_cells={incomplete}"
    )
    return ok, msg


def run_one(
    *,
    src_run: Path,
    dst_run: Path,
    config_path: Path,
    api_key_env: str,
    base_url: str,
    max_retries: int,
    max_concurrency: int,
    expected_samples_per_cell: int,
    backend: str = "openai",
) -> tuple[bool, str]:
    round1_provider, model = primary_round1_identity(src_run)
    expected_items = candidate_items_from_source(src_run)
    raw_path = dst_run / "raw_generations.jsonl"
    if expected_items and raw_path.exists():
        ok_existing, existing_msg = postflight_check(
            dst_run,
            expected_model=model,
            expected_items=expected_items,
            expected_samples_per_cell=expected_samples_per_cell,
        )
        if ok_existing:
            print(
                f"SKIP {src_run.name}: Round 2 already satisfies strict postflight "
                f"({len(expected_items)} item(s)); not wiping raw or re-sampling.",
                flush=True,
            )
            return True, f"skip already complete (strict postflight): {existing_msg}"

    prepare_dst_run(src_run, dst_run)

    r2_provider = "gemini" if backend == "gemini" else "openai"
    if backend == "gemini":
        state = patch_universal_gemini_model(
            api_key_env=api_key_env,
            model_name=model,
            max_retries=max_retries,
            max_concurrency=max_concurrency,
        )
    else:
        state = patch_universal_openai_model(
            base_url=base_url,
            api_key_env=api_key_env,
            model_name=model,
            max_retries=max_retries,
            max_concurrency=max_concurrency,
        )
    try:
        normalize_analyze(dst_run, config_path)
        items = candidate_items(dst_run)
        if not items:
            return True, f"skip no candidates after recompute: {model}"
        write_preflight(
            dst_run,
            src_run=src_run,
            provider=round1_provider,
            model=model,
            items=items,
            round2_provider=r2_provider,
        )
        print(
            f"PRECHECK {src_run.name}: r1_provider={round1_provider} r2_provider={r2_provider} model={model} items={items}",
            flush=True,
        )
        run_sampling(config_path, run_dir=dst_run, round_index=2, item_ids=items)
        ok_post, post_msg = postflight_check(
            dst_run,
            expected_model=model,
            expected_items=items,
            expected_samples_per_cell=expected_samples_per_cell,
        )
        if not ok_post:
            return False, "postflight mismatch: " + post_msg
        normalize_analyze(dst_run, config_path)
        ok_post, post_msg = postflight_check(
            dst_run,
            expected_model=model,
            expected_items=items,
            expected_samples_per_cell=expected_samples_per_cell,
        )
        if not ok_post:
            return False, "postflight mismatch after analyze: " + post_msg
        return True, "ok: " + post_msg
    finally:
        restore_load_config(state)


def apply_gentle_api_env_defaults() -> None:
    """Longer exponential backoff / cooldown when hitting flaky aggregators (429, TLS, empty SSE).

    Skipped if `--no-gentle-api`; user can override any value by exporting env before invocation.
    """
    os.environ.setdefault("COORDBENCH_PROVIDER_RETRY_LINEAR_SEC", "12")
    os.environ.setdefault("COORDBENCH_PROVIDER_RETRY_EXP_BASE_SEC", "10")
    os.environ.setdefault("COORDBENCH_PROVIDER_RETRY_MAX_SLEEP_SEC", "600")
    os.environ.setdefault("COORDBENCH_SUCCESS_REQUEST_COOLDOWN_SEC", "6")


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean per-model Round 2 rerun on each model's own top1 mismatch items.")
    parser.add_argument("--source-root", default="results/runs_s50")
    parser.add_argument("--dest-root", default="results/runs_s50_per_model_round2")
    parser.add_argument("--config", default="configs/universal_api_full_s50.yaml")
    parser.add_argument("--api-key-env", default="SUM_API_KEY")
    parser.add_argument("--base-url", default=PRIMARY_BASE_URL)
    parser.add_argument("--fallback-base-url", default=FALLBACK_BASE_URL)
    parser.add_argument(
        "--no-vendor-keys",
        action="store_true",
        help="Do not use vendor .env keys (GLM/OpenAI/DeepSeek/MiniMax); only SUM gateway transports.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=18,
        help="Per-request attempts in coordbench.runner (YAML default alone is overridden by CLI in this script).",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=2,
        help="Cap OpenAI provider concurrency during Round 2 (lower = fewer 429 bursts on shared gateways).",
    )
    parser.add_argument(
        "--no-gentle-api",
        action="store_true",
        help="Do not apply default COORDBENCH_* backoff/cooldown env vars for flaky APIs.",
    )
    parser.add_argument("--expected-samples-per-cell", type=int, default=10)
    parser.add_argument("--only-run", default="", help="Optional source run directory name to run only one model.")
    model_filter = parser.add_mutually_exclusive_group()
    model_filter.add_argument(
        "--only-openai-glm-models",
        action="store_true",
        help="Only source runs whose Round-1 model is GLM or OpenAI-style.",
    )
    model_filter.add_argument(
        "--skip-openai-glm-models",
        action="store_true",
        help="Exclude GLM/OpenAI-style Round-1 models (everything else continues on SUM gateway).",
    )
    vendor_lane = parser.add_mutually_exclusive_group()
    vendor_lane.add_argument(
        "--only-qwen-ds-minimax-models",
        action="store_true",
        help="Only Qwen / DeepSeek / MiniMax Round-1 models (pair with --skip-openai-glm-models for lane A).",
    )
    vendor_lane.add_argument(
        "--skip-qwen-ds-minimax-models",
        action="store_true",
        help="Exclude Qwen / DeepSeek / MiniMax (pair with --skip-openai-glm-models for lane B).",
    )
    vendor_lane.add_argument(
        "--only-qwen-models",
        action="store_true",
        help="Only Qwen Round-1 models (2 runs). Pair with --skip-openai-glm-models.",
    )
    vendor_lane.add_argument(
        "--only-deepseek-models",
        action="store_true",
        help="Only DeepSeek Round-1 models (2 runs). Pair with --skip-openai-glm-models.",
    )
    vendor_lane.add_argument(
        "--only-minimax-models",
        action="store_true",
        help="Only MiniMax Round-1 models (2 runs). Pair with --skip-openai-glm-models.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    try:
        from dotenv import load_dotenv

        load_dotenv(project_root / ".env", override=True)
    except ImportError:
        pass

    if not args.no_gentle_api:
        apply_gentle_api_env_defaults()

    if not (
        _env_nonempty(args.api_key_env)
        or _env_nonempty("OPENAI_API_KEY")
        or _env_nonempty("GLM_API_KEY")
        or _env_nonempty("DEEPSEEK_API_KEY")
        or _env_nonempty("MINIMAX_API_KEY")
        or _env_nonempty("QWEN_API_KEY")
        or _env_nonempty("GEMINI_API_KEY")
    ):
        raise SystemExit(
            "No API credentials: set SUM_API_KEY (or --api-key-env), and/or OPENAI_API_KEY, GLM_API_KEY, "
            "DEEPSEEK_API_KEY, MINIMAX_API_KEY, QWEN_API_KEY, GEMINI_API_KEY in .env."
        )

    source_root = (project_root / args.source_root).resolve()
    dest_root = (project_root / args.dest_root).resolve()
    config_path = (project_root / args.config).resolve()
    dest_root.mkdir(parents=True, exist_ok=True)

    runs = discover_source_runs(source_root)
    if args.only_run:
        runs = [run for run in runs if run.name == args.only_run]
    if args.only_openai_glm_models:
        before = len(runs)
        kept: list[Path] = []
        skipped: list[str] = []
        for run in runs:
            _prov, m = primary_round1_identity(run)
            if _is_openai_or_glm_model(m):
                kept.append(run)
            else:
                skipped.append(f"{run.name} (model={m})")
        runs = kept
        print(
            f"--only-openai-glm-models: kept {len(runs)}/{before} runs; "
            f"skipped {len(skipped)} non-vendor models",
            flush=True,
        )
        for line in skipped:
            print(f"  skip: {line}", flush=True)
    elif args.skip_openai_glm_models:
        before = len(runs)
        kept = []
        skipped = []
        for run in runs:
            _prov, m = primary_round1_identity(run)
            if _is_openai_or_glm_model(m):
                skipped.append(f"{run.name} (model={m})")
            else:
                kept.append(run)
        runs = kept
        print(
            f"--skip-openai-glm-models: kept {len(runs)}/{before} runs; "
            f"skipped {len(skipped)} GLM/OpenAI-style models",
            flush=True,
        )
        for line in skipped:
            print(f"  skip: {line}", flush=True)
    if args.only_qwen_ds_minimax_models:
        before = len(runs)
        kept = []
        skipped = []
        for run in runs:
            _prov, m = primary_round1_identity(run)
            if _is_qwen_ds_minimax_model(m):
                kept.append(run)
            else:
                skipped.append(f"{run.name} (model={m})")
        runs = kept
        print(
            f"--only-qwen-ds-minimax-models: kept {len(runs)}/{before}; skipped {len(skipped)}",
            flush=True,
        )
        for line in skipped:
            print(f"  skip: {line}", flush=True)
    elif args.only_qwen_models:
        before = len(runs)
        kept = []
        skipped = []
        for run in runs:
            _prov, m = primary_round1_identity(run)
            if _is_qwen_model(m):
                kept.append(run)
            else:
                skipped.append(f"{run.name} (model={m})")
        runs = kept
        print(f"--only-qwen-models: kept {len(runs)}/{before}; skipped {len(skipped)}", flush=True)
        for line in skipped:
            print(f"  skip: {line}", flush=True)
    elif args.only_deepseek_models:
        before = len(runs)
        kept = []
        skipped = []
        for run in runs:
            _prov, m = primary_round1_identity(run)
            if _is_deepseek_model(m):
                kept.append(run)
            else:
                skipped.append(f"{run.name} (model={m})")
        runs = kept
        print(f"--only-deepseek-models: kept {len(runs)}/{before}; skipped {len(skipped)}", flush=True)
        for line in skipped:
            print(f"  skip: {line}", flush=True)
    elif args.only_minimax_models:
        before = len(runs)
        kept = []
        skipped = []
        for run in runs:
            _prov, m = primary_round1_identity(run)
            if _is_minimax_model(m):
                kept.append(run)
            else:
                skipped.append(f"{run.name} (model={m})")
        runs = kept
        print(f"--only-minimax-models: kept {len(runs)}/{before}; skipped {len(skipped)}", flush=True)
        for line in skipped:
            print(f"  skip: {line}", flush=True)
    elif args.skip_qwen_ds_minimax_models:
        before = len(runs)
        kept = []
        skipped = []
        for run in runs:
            _prov, m = primary_round1_identity(run)
            if _is_qwen_ds_minimax_model(m):
                skipped.append(f"{run.name} (model={m})")
            else:
                kept.append(run)
        runs = kept
        print(
            f"--skip-qwen-ds-minimax-models: kept {len(runs)}/{before}; skipped {len(skipped)}",
            flush=True,
        )
        for line in skipped:
            print(f"  skip: {line}", flush=True)
    if not runs:
        raise SystemExit("No source runs with candidates found.")

    failures: list[str] = []
    print(f"Source runs: {len(runs)}")
    print(f"Destination: {dest_root}")
    print(f"Config: {config_path}")
    print(
        "Credentials: SUM+gateway + vendor routes (GLM/OpenAI/DeepSeek/MiniMax/Qwen/Gemini) when keys exist "
        f"({'vendor keys disabled' if args.no_vendor_keys else 'vendor keys enabled'})",
        flush=True,
    )
    print(f"Default gateway API key env: {args.api_key_env}", flush=True)
    print(f"max_retries={args.max_retries} max_concurrency={args.max_concurrency} gentle_api={not args.no_gentle_api}")
    if not args.no_gentle_api:
        print(
            "COORDBENCH retry env: "
            f"LINEAR_SEC={os.environ.get('COORDBENCH_PROVIDER_RETRY_LINEAR_SEC')} "
            f"EXP_BASE_SEC={os.environ.get('COORDBENCH_PROVIDER_RETRY_EXP_BASE_SEC')} "
            f"MAX_SLEEP_SEC={os.environ.get('COORDBENCH_PROVIDER_RETRY_MAX_SLEEP_SEC')} "
            f"SUCCESS_COOLDOWN_SEC={os.environ.get('COORDBENCH_SUCCESS_REQUEST_COOLDOWN_SEC')}",
            flush=True,
        )
    print(f"Primary base URL: {args.base_url}")
    print(f"Fallback base URL: {args.fallback_base_url}")
    for src_run in runs:
        dst_run = dest_root / f"{src_run.name}__permodelr2"
        print(f"\n=== {src_run.name} -> {dst_run.name} ===", flush=True)
        _, model = primary_round1_identity(src_run)
        transports = transports_for_model(
            model,
            default_key_env=args.api_key_env,
            gateway_primary=args.base_url,
            gateway_fallback=args.fallback_base_url,
            use_vendor_keys=not args.no_vendor_keys,
        )
        if not transports:
            print("No usable transports (missing API keys / empty base URLs?) for model=" + model, flush=True)
            failures.append(src_run.name)
            continue

        ok = False
        last_msg = ""
        for leg in transports:
            if not _env_nonempty(leg.api_key_env):
                print(f"[SKIP] transport={leg.label}: env {leg.api_key_env} empty", flush=True)
                continue
            if leg.backend == "gemini":
                print(f"transport {leg.label}: api_key_env={leg.api_key_env} backend=gemini", flush=True)
            else:
                print(
                    f"transport {leg.label}: api_key_env={leg.api_key_env} base_url={leg.base_url}",
                    flush=True,
                )
            ok, last_msg = run_one(
                src_run=src_run,
                dst_run=dst_run,
                config_path=config_path,
                api_key_env=leg.api_key_env,
                base_url=leg.base_url,
                max_retries=args.max_retries,
                max_concurrency=args.max_concurrency,
                expected_samples_per_cell=args.expected_samples_per_cell,
                backend=leg.backend,
            )
            if ok:
                print(
                    f"[OK] run={src_run.name} model={model} transport={leg.label} "
                    f"key_env={leg.api_key_env} base_url={leg.base_url} :: {last_msg}",
                    flush=True,
                )
                break
            print(
                f"[FAIL] run={src_run.name} model={model} transport={leg.label} "
                f"key_env={leg.api_key_env} base_url={leg.base_url} :: {last_msg}",
                flush=True,
            )
        if not ok:
            failures.append(src_run.name)
            print(
                f"[FAIL] run={src_run.name} model={model} (exhausted {len(transports)} transport(s))",
                flush=True,
            )

    if failures:
        print(f"\nCompleted with failures ({len(failures)}): {', '.join(failures)}")
        return 1
    print("\nCompleted per-model Round 2 for all source runs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
