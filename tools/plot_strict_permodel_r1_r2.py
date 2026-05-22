#!/usr/bin/env python3
"""Plot Round 1 vs Round 2 cross-lingual bars from strict per-model R2 runs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STRICT = ROOT / "results" / "runs_s50_per_model_round2_strict"
TABLES = ROOT / "results" / "final_project_tables"
OUT = ROOT / "docs" / "figures"

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 7,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)

R1_COLOR = "#4C72B0"
R2_COLOR = "#DD8452"


def _display_label(model: str, run: str) -> str:
    short = run.split("_")[0] if run else model
    if model in {"deepseek-chat", "gpt-5.4"} and short != model.replace(".", ""):
        return f"{model}\n({short})"
    return model.replace("MiniMax-M2.7-highspeed", "MiniMax-M2.7-hs").replace(
        "glm-4-flashx-250414", "glm-4-flashx"
    )


def load_same_item_model_summary() -> pd.DataFrame:
    """Mean JSD / top-1 on the same candidate items per model (R1 vs R2)."""
    rows: list[dict] = []
    for run_dir in sorted(STRICT.glob("*__permodelr2")):
        item_path = run_dir / "item_metrics.csv"
        if not item_path.exists():
            continue
        run = run_dir.name.replace("__permodelr2", "")
        im = pd.read_csv(item_path)
        cross = im[im["metric_family"] == "cross_lingual"].copy()
        if cross.empty:
            continue
        model = str(cross["model"].iloc[0])
        r1 = cross[cross["round_index"] == 1].set_index("item_id")[["jsd", "top1_match"]]
        r2 = cross[cross["round_index"] == 2].set_index("item_id")[["jsd", "top1_match"]]
        common = sorted(r1.index.intersection(r2.index))
        if not common:
            continue
        r1_sub = r1.loc[common]
        r2_sub = r2.loc[common]
        rows.append(
            {
                "run": run,
                "model": model,
                "n_items": len(common),
                "r1_mean_jsd": float(r1_sub["jsd"].mean()),
                "r2_mean_jsd": float(r2_sub["jsd"].mean()),
                "r1_mean_top1": float(r1_sub["top1_match"].mean()),
                "r2_mean_top1": float(r2_sub["top1_match"].mean()),
                "delta_jsd": float(r2_sub["jsd"].mean() - r1_sub["jsd"].mean()),
                "delta_top1": float(r2_sub["top1_match"].mean() - r1_sub["top1_match"].mean()),
            }
        )
    return pd.DataFrame(rows)


def plot_same_item_grouped_bars(
    plot_df: pd.DataFrame,
    *,
    r1_col: str,
    r2_col: str,
    ylabel: str,
    title: str,
    out_path: Path,
) -> None:
    plot_df = plot_df.sort_values(r1_col, ascending=True)
    labels = [_display_label(m, r) for m, r in zip(plot_df["model"], plot_df["run"])]
    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(max(12, len(labels) * 0.55), 5.8))
    r1_vals = plot_df[r1_col].to_numpy()
    r2_vals = plot_df[r2_col].to_numpy()
    ax.bar(
        x - width / 2,
        r1_vals,
        width,
        label="Round 1 (same candidate items)",
        color=R1_COLOR,
    )
    ax.bar(x + width / 2, r2_vals, width, label="Round 2", color=R2_COLOR)

    for i, n in enumerate(plot_df["n_items"]):
        ax.text(i, max(r1_vals[i], r2_vals[i]) + 0.02, f"n={int(n)}", ha="center", va="bottom", fontsize=6, color="#555")

    ax.set_ylabel(ylabel)
    ax.set_xlabel("Model")
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=55, ha="right")
    ax.legend(loc="upper left", frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    if "top1" in r1_col:
        ax.set_ylim(0, 1.08)
    else:
        ax.set_ylim(bottom=0)

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def load_cross_lingual_table() -> pd.DataFrame:
    rows: list[dict] = []
    for run_dir in sorted(STRICT.glob("*__permodelr2")):
        item_path = run_dir / "item_metrics.csv"
        if not item_path.exists():
            continue
        run = run_dir.name.replace("__permodelr2", "")
        im = pd.read_csv(item_path)
        cross = im[im["metric_family"] == "cross_lingual"].copy()
        if cross.empty:
            continue
        model = str(cross["model"].iloc[0])
        for rnd in (1, 2):
            sub = cross[cross["round_index"] == rnd]
            if sub.empty:
                rows.append(
                    {
                        "run": run,
                        "model": model,
                        "round": rnd,
                        "mean_jsd": np.nan,
                        "mean_top1": np.nan,
                        "n_items": 0,
                        "status": "missing",
                    }
                )
                continue
            rows.append(
                {
                    "run": run,
                    "model": model,
                    "round": rnd,
                    "mean_jsd": float(sub["jsd"].mean()),
                    "mean_top1": float(sub["top1_match"].mean()),
                    "n_items": int(sub["item_id"].nunique()),
                    "status": "ok",
                }
            )
    return pd.DataFrame(rows)


def plot_grouped_bars(df: pd.DataFrame, metric: str, ylabel: str, title: str, out_path: Path) -> None:
    r1 = df[(df["round"] == 1) & df[metric].notna()][["run", "model", metric, "n_items"]].rename(
        columns={metric: "r1_val", "n_items": "n_items_r1"}
    )
    r2 = df[(df["round"] == 2) & df[metric].notna()][["run", "model", metric, "n_items"]].rename(
        columns={metric: "r2_val", "n_items": "n_items_r2"}
    )
    plot_df = r1.merge(r2, on=["run", "model"], how="inner")
    if plot_df.empty:
        raise RuntimeError(f"No models with both R1 and R2 for {metric}")

    plot_df = plot_df.sort_values("r1_val", ascending=True)
    labels = [_display_label(m, r) for m, r in zip(plot_df["model"], plot_df["run"])]
    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(max(12, len(labels) * 0.55), 5.8))
    r1_vals = plot_df["r1_val"].to_numpy()
    r2_vals = plot_df["r2_val"].to_numpy()
    ax.bar(x - width / 2, r1_vals, width, label="Round 1 (15 items)", color=R1_COLOR)
    ax.bar(x + width / 2, r2_vals, width, label="Round 2 (candidates)", color=R2_COLOR)

    for i, (_, row) in enumerate(plot_df.iterrows()):
        ax.text(
            i + width / 2,
            r2_vals[i] + 0.02,
            f"n={int(row['n_items_r2'])}",
            ha="center",
            va="bottom",
            fontsize=6,
            color="#555555",
        )

    ax.set_ylabel(ylabel)
    ax.set_xlabel("Model")
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=55, ha="right")
    ax.legend(loc="upper left", frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    if metric == "mean_top1":
        ax.set_ylim(0, 1.08)
    else:
        ax.set_ylim(bottom=0)

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    df = load_cross_lingual_table()
    csv_path = TABLES / "strict_permodel_cross_lingual_r1_r2.csv"
    df.to_csv(csv_path, index=False)

    wide = df.pivot_table(index=["run", "model"], columns="round", values=["mean_jsd", "mean_top1", "n_items"])
    print("Wrote", csv_path)
    print(wide.to_string())

    r2_runs = set(df[df["round"] == 2]["run"])
    no_r2_rows = df[(df["round"] == 1) & (~df["run"].isin(r2_runs))]
    if not no_r2_rows.empty:
        print("\nRuns without usable R2 cross-lingual metrics:")
        for run in no_r2_rows["run"].unique():
            print(" ", run)

    jsd_fig = OUT / "strict_permodel_r1_r2_cross_jsd.png"
    top1_fig = OUT / "strict_permodel_r1_r2_cross_top1.png"
    plot_grouped_bars(
        df,
        "mean_jsd",
        "Mean JSD (EN vs ZH; lower is better)",
        "Cross-lingual stability: Round 1 vs Round 2 (strict per-model R2)",
        jsd_fig,
    )
    plot_grouped_bars(
        df,
        "mean_top1",
        "Mean top-1 match (higher is better)",
        "Cross-lingual focal agreement: Round 1 vs Round 2 (strict per-model R2)",
        top1_fig,
    )
    print(f"Wrote {jsd_fig}")
    print(f"Wrote {top1_fig}")

    same = load_same_item_model_summary()
    same_csv = TABLES / "strict_permodel_same_items_model_summary.csv"
    same.to_csv(same_csv, index=False)
    print(f"\nWrote {same_csv}")
    print(same.to_string(index=False))

    jsd_same = OUT / "strict_permodel_same_items_r1_r2_jsd.png"
    top1_same = OUT / "strict_permodel_same_items_r1_r2_top1.png"
    plot_same_item_grouped_bars(
        same,
        r1_col="r1_mean_jsd",
        r2_col="r2_mean_jsd",
        ylabel="Mean JSD on candidate items (EN vs ZH; lower is better)",
        title="Same candidate items: Round 1 vs Round 2 cross-lingual JSD",
        out_path=jsd_same,
    )
    plot_same_item_grouped_bars(
        same,
        r1_col="r1_mean_top1",
        r2_col="r2_mean_top1",
        ylabel="Mean top-1 match on candidate items (higher is better)",
        title="Same candidate items: Round 1 vs Round 2 cross-lingual top-1",
        out_path=top1_same,
    )
    print(f"Wrote {jsd_same}")
    print(f"Wrote {top1_same}")


if __name__ == "__main__":
    main()
