from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from coordbench.metrics import distribution_from_answers, jsd, spearman_frequency, top1_match, tvd

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CompanyCompareOutputs:
    out_dir: Path
    pair_item_metrics_csv: Path
    pair_agg_metrics_csv: Path
    effect_sizes_json: Path
    plots_dir: Path


def _default_company_for_model(model: str) -> str:
    m = (model or "").lower()
    if not m:
        return "unknown"

    # OpenAI
    if m.startswith(("gpt-", "o1", "o3", "o4", "chatgpt")) or "openai" in m:
        return "openai"
    # Google
    if "gemini" in m:
        return "google"
    # Anthropic
    if "claude" in m or "anthropic" in m:
        return "anthropic"
    # DeepSeek
    if "deepseek" in m:
        return "deepseek"
    # Zhipu / GLM
    if m.startswith("glm") or "zhipu" in m:
        return "zhipu"
    # MiniMax
    if "minimax" in m:
        return "minimax"
    # Moonshot (Kimi)
    if m.startswith("kimi") or "moonshot" in m:
        return "moonshot"
    # Alibaba / Qwen
    if m.startswith("qwen") or "qwen" in m:
        return "alibaba"
    # ByteDance (Seed/KDoubao) - heuristic
    if "seed" in m or "doubao" in m:
        return "bytedance"

    return "other"


def _load_model_company_map(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    if not path.exists():
        return {}
    frame = pd.read_csv(path)
    cols = {c.lower(): c for c in frame.columns}
    if "model" not in cols or "company" not in cols:
        raise ValueError(f"Company map must have columns model, company. Got: {list(frame.columns)}")
    mapping = {}
    for row in frame[[cols["model"], cols["company"]]].itertuples(index=False):
        model = str(row[0]).strip()
        company = str(row[1]).strip()
        if model:
            mapping[model] = company or "unknown"
    return mapping


def _discover_run_dirs(runs_root: Path) -> list[Path]:
    if not runs_root.exists():
        raise FileNotFoundError(f"runs_root not found: {runs_root}")
    # Heuristic: any directory containing normalized_outputs.csv.
    run_dirs: list[Path] = []
    for path in sorted(runs_root.glob("*")):
        if not path.is_dir():
            continue
        if (path / "normalized_outputs.csv").exists():
            run_dirs.append(path)
    return run_dirs


def _read_run_normalized(run_dir: Path) -> pd.DataFrame:
    frame = pd.read_csv(run_dir / "normalized_outputs.csv")
    if frame.empty:
        return frame
    # Normalize types we rely on.
    for col in ["provider", "model", "panel_id", "item_id", "prompt_language"]:
        if col in frame.columns:
            frame[col] = frame[col].fillna("").astype(str)
    if "round_index" in frame.columns:
        frame["round_index"] = frame["round_index"].astype(int)
    return frame


def _ensure_answer_key(frame: pd.DataFrame) -> pd.DataFrame:
    if "coord_answer_key" in frame.columns:
        out = frame.copy()
        out["coord_answer_key"] = out["coord_answer_key"].fillna("").astype(str)
        return out
    # Fallback: best-effort use already-normalized coord_answer (if present); otherwise response_clean.
    out = frame.copy()
    if "coord_answer" in out.columns:
        out["coord_answer_key"] = out["coord_answer"].fillna("").astype(str)
    elif "response_clean" in out.columns:
        out["coord_answer_key"] = out["response_clean"].fillna("").astype(str)
    else:
        out["coord_answer_key"] = ""
    return out


def _item_distributions(
    normalized: pd.DataFrame,
    *,
    round_index: int,
    prompt_languages: Iterable[str] | None = None,
) -> dict[tuple[str, str, str, str], dict[str, float]]:
    """
    Returns {(provider, model, item_id, prompt_language) -> distribution over coord_answer_key}.
    """
    if normalized.empty:
        return {}
    frame = _ensure_answer_key(normalized)
    frame = frame[frame.get("round_index", 0) == int(round_index)].copy()
    if prompt_languages is not None:
        wanted = {str(v) for v in prompt_languages}
        frame = frame[frame["prompt_language"].isin(wanted)].copy()
    frame = frame[frame["coord_answer_key"].fillna("").astype(str) != ""].copy()
    if frame.empty:
        return {}
    dists: dict[tuple[str, str, str, str], dict[str, float]] = {}
    grouped = frame.groupby(["provider", "model", "item_id", "prompt_language"], dropna=False)
    for (provider, model, item_id, prompt_language), group in grouped:
        dist = distribution_from_answers(group["coord_answer_key"].astype(str).tolist())
        dists[(str(provider), str(model), str(item_id), str(prompt_language))] = dist
    return dists


def _pairwise_item_metrics(
    dists: dict[tuple[str, str, str, str], dict[str, float]],
    model_to_company: dict[str, str],
) -> pd.DataFrame:
    # Build index by (item_id, prompt_language) -> {(provider, model): dist}
    bucket: dict[tuple[str, str], dict[tuple[str, str], dict[str, float]]] = {}
    for (provider, model, item_id, prompt_language), dist in dists.items():
        key = (item_id, prompt_language)
        bucket.setdefault(key, {})[(provider, model)] = dist

    rows: list[dict[str, object]] = []
    for (item_id, prompt_language), by_key in bucket.items():
        keys = sorted(by_key)  # (provider, model)
        for i, (provider_a, model_a) in enumerate(keys):
            for provider_b, model_b in keys[i + 1 :]:
                dist_a = by_key[(provider_a, model_a)]
                dist_b = by_key[(provider_b, model_b)]

                company_a = model_to_company.get(model_a) or _default_company_for_model(model_a)
                company_b = model_to_company.get(model_b) or _default_company_for_model(model_b)
                same_company = int(company_a == company_b and company_a not in {"unknown", "other"})

                provider_pair = "__".join(sorted([str(provider_a), str(provider_b)]))
                rows.append(
                    {
                        "item_id": item_id,
                        "prompt_language": prompt_language,
                        "provider_a": provider_a,
                        "provider_b": provider_b,
                        "provider_pair": provider_pair,
                        "model_a": model_a,
                        "model_b": model_b,
                        "company_a": company_a,
                        "company_b": company_b,
                        "same_company": same_company,
                        "jsd": jsd(dist_a, dist_b),
                        "tvd": tvd(dist_a, dist_b),
                        "top1_match": top1_match(dist_a, dist_b),
                        "spearman": spearman_frequency(dist_a, dist_b),
                    }
                )
    return pd.DataFrame(rows)


def _pairwise_aggregate(pair_item: pd.DataFrame) -> pd.DataFrame:
    if pair_item.empty:
        return pair_item
    group_cols = [
        "prompt_language",
        "provider_a",
        "provider_b",
        "provider_pair",
        "model_a",
        "model_b",
        "company_a",
        "company_b",
        "same_company",
    ]
    agg = (
        pair_item.groupby(group_cols, dropna=False)
        .agg(
            item_count=("item_id", "nunique"),
            mean_jsd=("jsd", "mean"),
            mean_tvd=("tvd", "mean"),
            top1_match_rate=("top1_match", "mean"),
            mean_spearman=("spearman", lambda s: float(pd.to_numeric(s, errors="coerce").dropna().mean()) if s.notna().any() else np.nan),
        )
        .reset_index()
    )
    agg["pair_type"] = np.where(agg["same_company"].astype(int) == 1, "within_company", "cross_company")
    return agg


def _bootstrap_delta(
    within: np.ndarray,
    cross: np.ndarray,
    *,
    metric: str,
    resamples: int = 5000,
    seed: int = 20260420,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)

    within = within[np.isfinite(within)]
    cross = cross[np.isfinite(cross)]
    if within.size == 0 or cross.size == 0:
        return {"delta": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}

    # Direction: positive delta means "within is more aligned than cross"
    # - For distance metrics (jsd/tvd): aligned => smaller => delta = median(cross) - median(within)
    # - For agreement metrics (top1_match/spearman): aligned => larger => delta = median(within) - median(cross)
    distance_metrics = {"mean_jsd", "mean_tvd"}
    agreement_metrics = {"top1_match_rate", "mean_spearman"}
    if metric in distance_metrics:
        def delta_fn(w: np.ndarray, c: np.ndarray) -> float:
            return float(np.median(c) - np.median(w))
    elif metric in agreement_metrics:
        def delta_fn(w: np.ndarray, c: np.ndarray) -> float:
            return float(np.median(w) - np.median(c))
    else:
        raise ValueError(f"Unknown metric: {metric}")

    deltas = []
    for _ in range(resamples):
        w_draw = rng.choice(within, size=within.size, replace=True)
        c_draw = rng.choice(cross, size=cross.size, replace=True)
        deltas.append(delta_fn(w_draw, c_draw))
    deltas_np = np.asarray(deltas, dtype=float)
    return {
        "delta": float(np.median(deltas_np)),
        "ci_low": float(np.quantile(deltas_np, 0.025)),
        "ci_high": float(np.quantile(deltas_np, 0.975)),
    }


def _write_effect_sizes(pair_agg: pd.DataFrame, out_path: Path) -> dict[str, object]:
    effect: dict[str, object] = {"by_language": {}}
    if pair_agg.empty:
        out_path.write_text(json.dumps(effect, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return effect

    # Route A: control provider differences by stratifying on provider_pair and aggregating deltas equally across strata.
    metrics = ["top1_match_rate"]
    for prompt_language, subset in pair_agg.groupby("prompt_language"):
        out = {}
        for metric in metrics:
            deltas = []
            within_total = 0
            cross_total = 0
            for provider_pair, stratum in subset.groupby("provider_pair"):
                within = stratum[stratum["pair_type"] == "within_company"]
                cross = stratum[stratum["pair_type"] == "cross_company"]
                w = pd.to_numeric(within[metric], errors="coerce").to_numpy(dtype=float)
                c = pd.to_numeric(cross[metric], errors="coerce").to_numpy(dtype=float)
                within_total += int(np.isfinite(w).sum())
                cross_total += int(np.isfinite(c).sum())
                if np.isfinite(w).sum() == 0 or np.isfinite(c).sum() == 0:
                    continue
                # Agreement metric: delta = median(within) - median(cross)
                deltas.append(float(np.median(w[np.isfinite(w)]) - np.median(c[np.isfinite(c)])))

            deltas_np = np.asarray(deltas, dtype=float)
            if deltas_np.size == 0:
                out[metric] = {"within_n": within_total, "cross_n": cross_total, "delta": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
            else:
                # Bootstrap over provider-pair strata (equal weight).
                rng = np.random.default_rng(20260420)
                boot = []
                for _ in range(5000):
                    draw = rng.choice(deltas_np, size=deltas_np.size, replace=True)
                    boot.append(float(np.median(draw)))
                boot_np = np.asarray(boot, dtype=float)
                out[metric] = {
                    "within_n": within_total,
                    "cross_n": cross_total,
                    "delta": float(np.median(boot_np)),
                    "ci_low": float(np.quantile(boot_np, 0.025)),
                    "ci_high": float(np.quantile(boot_np, 0.975)),
                    "provider_pair_strata": int(deltas_np.size),
                }
        effect["by_language"][str(prompt_language)] = out

    out_path.write_text(json.dumps(effect, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return effect


def _plot_distributions(pair_agg: pd.DataFrame, plots_dir: Path) -> None:
    metrics = [("top1_match_rate", "Top-1 match rate (higher = more aligned)")]
    for prompt_language, subset in pair_agg.groupby("prompt_language"):
        for metric, ylabel in metrics:
            data = subset[["pair_type", metric]].copy()
            data[metric] = pd.to_numeric(data[metric], errors="coerce")
            data = data.dropna()
            if data.empty:
                continue

            order = ["within_company", "cross_company"]
            values = [data.loc[data["pair_type"] == key, metric].to_numpy(dtype=float) for key in order]

            fig, ax = plt.subplots(figsize=(8, 5))
            ax.boxplot(values, labels=order, showfliers=False)
            # jitter points
            rng = np.random.default_rng(20260420)
            for i, arr in enumerate(values, start=1):
                if arr.size == 0:
                    continue
                x = rng.normal(loc=i, scale=0.06, size=arr.size)
                ax.scatter(x, arr, s=10, alpha=0.25)
            ax.set_title(f"Round1 model-model similarity ({prompt_language})")
            ax.set_ylabel(ylabel)
            fig.tight_layout()
            fig.savefig(plots_dir / f"dist_{prompt_language}_{metric}.png", dpi=200)
            fig.savefig(plots_dir / f"dist_{prompt_language}_{metric}.pdf")
            plt.close(fig)


def _plot_forest(effect_sizes: dict[str, object], plots_dir: Path) -> None:
    metrics = [("top1_match_rate", "Δ (within median − cross median)")]
    by_language = effect_sizes.get("by_language", {}) if isinstance(effect_sizes, dict) else {}
    for prompt_language, payload in by_language.items():
        rows = []
        for metric, xlab in metrics:
            stat = payload.get(metric, {}) if isinstance(payload, dict) else {}
            rows.append(
                {
                    "metric": metric,
                    "delta": float(stat.get("delta", float("nan"))),
                    "ci_low": float(stat.get("ci_low", float("nan"))),
                    "ci_high": float(stat.get("ci_high", float("nan"))),
                    "xlabel": xlab,
                }
            )
        frame = pd.DataFrame(rows)
        if frame.empty:
            continue

        fig, ax = plt.subplots(figsize=(8, 4.5))
        y = np.arange(len(frame))[::-1]
        ax.errorbar(
            frame["delta"],
            y,
            xerr=[frame["delta"] - frame["ci_low"], frame["ci_high"] - frame["delta"]],
            fmt="o",
            capsize=3,
        )
        ax.axvline(0.0, color="black", linewidth=1, alpha=0.6)
        ax.set_yticks(y)
        ax.set_yticklabels(frame["metric"])
        ax.set_title(f"Effect sizes: within-company vs cross-company ({prompt_language})")
        ax.set_xlabel("Positive Δ => within-company more aligned")
        fig.tight_layout()
        fig.savefig(plots_dir / f"forest_{prompt_language}.png", dpi=200)
        fig.savefig(plots_dir / f"forest_{prompt_language}.pdf")
        plt.close(fig)


def _plot_heatmap(pair_agg: pd.DataFrame, plots_dir: Path, *, metric: str = "mean_jsd") -> None:
    for prompt_language, subset in pair_agg.groupby("prompt_language"):
        df = subset.copy()
        df[metric] = pd.to_numeric(df[metric], errors="coerce")
        df = df.dropna(subset=[metric])
        if df.empty:
            continue

        models = sorted(set(df["model_a"]) | set(df["model_b"]))
        index = {m: i for i, m in enumerate(models)}
        mat = np.full((len(models), len(models)), np.nan, dtype=float)
        for row in df.itertuples(index=False):
            a = getattr(row, "model_a")
            b = getattr(row, "model_b")
            v = float(getattr(row, metric))
            i = index[a]
            j = index[b]
            mat[i, j] = v
            mat[j, i] = v
        # Diagonal should reflect "self similarity".
        # Distances (e.g. mean_jsd/mean_tvd) -> 0.0; agreement/rates (e.g. top1_match_rate) -> 1.0
        if metric.endswith("_rate") or metric.startswith("mean_top1") or metric.startswith("top1_match"):
            np.fill_diagonal(mat, 1.0)
        else:
            np.fill_diagonal(mat, 0.0)

        fig, ax = plt.subplots(figsize=(max(6, len(models) * 0.5), max(6, len(models) * 0.5)))
        im = ax.imshow(mat, interpolation="nearest", aspect="auto")
        ax.set_title(f"Round1 model-model {metric} heatmap ({prompt_language})")
        ax.set_xticks(np.arange(len(models)))
        ax.set_yticks(np.arange(len(models)))
        ax.set_xticklabels(models, rotation=90, fontsize=7)
        ax.set_yticklabels(models, fontsize=7)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(plots_dir / f"heatmap_{prompt_language}_{metric}.png", dpi=200)
        fig.savefig(plots_dir / f"heatmap_{prompt_language}_{metric}.pdf")
        plt.close(fig)


def compare_companies(
    *,
    runs_root: str | Path,
    out_root: str | Path,
    round_index: int = 1,
    prompt_languages: list[str] | None = None,
    model_company_map_csv: str | Path | None = None,
) -> CompanyCompareOutputs:
    runs_root = Path(runs_root).resolve()
    out_root = Path(out_root).resolve()
    tag = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = out_root / f"company_compare_{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    run_dirs = _discover_run_dirs(runs_root)
    if not run_dirs:
        raise RuntimeError(f"No run dirs with normalized_outputs.csv under {runs_root}")

    explicit_map = _load_model_company_map(Path(model_company_map_csv).resolve()) if model_company_map_csv else {}

    all_dists: dict[tuple[str, str, str, str], dict[str, float]] = {}
    for run_dir in run_dirs:
        normalized = _read_run_normalized(run_dir)
        dists = _item_distributions(normalized, round_index=round_index, prompt_languages=prompt_languages)
        all_dists.update(dists)

    pair_item = _pairwise_item_metrics(all_dists, model_to_company=explicit_map)
    pair_item_metrics_csv = out_dir / "pair_item_metrics.csv"
    pair_item.to_csv(pair_item_metrics_csv, index=False)

    pair_agg = _pairwise_aggregate(pair_item)
    pair_agg_metrics_csv = out_dir / "pair_agg_metrics.csv"
    pair_agg.to_csv(pair_agg_metrics_csv, index=False)

    effect_sizes_json = out_dir / "effect_sizes.json"
    effect_sizes = _write_effect_sizes(pair_agg, effect_sizes_json)

    if not pair_agg.empty:
        _plot_distributions(pair_agg, plots_dir)
        _plot_forest(effect_sizes, plots_dir)
        _plot_heatmap(pair_agg, plots_dir, metric="top1_match_rate")

    LOGGER.info("Wrote company-compare outputs into %s", out_dir)
    return CompanyCompareOutputs(
        out_dir=out_dir,
        pair_item_metrics_csv=pair_item_metrics_csv,
        pair_agg_metrics_csv=pair_agg_metrics_csv,
        effect_sizes_json=effect_sizes_json,
        plots_dir=plots_dir,
    )

