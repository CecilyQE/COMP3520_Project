#!/usr/bin/env python3
"""Generate Round 1 figures for docs/final_report.tex."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "final_project_tables"
OUT = ROOT / "docs" / "figures"
CROSS_CSV = TABLES / "model_level_cross_lingual_r1_r2.csv"
HUMAN_CSV = TABLES / "model_level_human_alignment_r1.csv"

# Publication-friendly styling
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

EN_COLOR = "#4C72B0"
ZH_COLOR = "#DD8452"
JSD_COLOR = "#55A868"
TOP1_COLOR = "#C44E52"


def _display_model(name: str) -> str:
    return (
        name.replace("gpt-5.4 (main)", "gpt-5.4")
        .replace("gpt-5.4 (round2-upload)", "gpt-5.4-upload")
        .replace("MiniMax-M2.7-highspeed", "MiniMax-M2.7-hs")
        .replace("glm-4-flashx-250414", "glm-4-flashx")
    )


def load_cross_lingual() -> pd.DataFrame:
    df = pd.read_csv(CROSS_CSV)
    df = df.rename(columns={"R1 JSD": "r1_jsd", "R1 Top1 match": "r1_top1", "Model": "model"})
    df["model_display"] = df["model"].map(_display_model)
    df = df.sort_values("r1_jsd", ascending=True).reset_index(drop=True)
    return df


def load_human_alignment() -> pd.DataFrame:
    raw = pd.read_csv(HUMAN_CSV)
    en = raw[raw["Prompt language"] == "en"].rename(
        columns={"Model": "model", "JSD": "en_jsd", "Top1 match": "en_top1"}
    )[["model", "en_jsd", "en_top1"]]
    zh = raw[raw["Prompt language"] == "zh"].rename(
        columns={"Model": "model", "JSD": "zh_jsd", "Top1 match": "zh_top1"}
    )[["model", "zh_jsd", "zh_top1"]]
    df = en.merge(zh, on="model")
    df["model_display"] = df["model"].map(_display_model)
    # Order by average human-alignment JSD (EN+ZH)/2 for readability
    df["mean_human_jsd"] = (df["en_jsd"] + df["zh_jsd"]) / 2
    df = df.sort_values("mean_human_jsd", ascending=True).reset_index(drop=True)
    return df


def plot_figure_a(cross: pd.DataFrame, out_path: Path) -> None:
    models = cross["model_display"].tolist()
    y = np.arange(len(models))
    height = 0.36

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 7.2), sharey=True)

    axes[0].barh(y - height / 2, cross["r1_jsd"], height=height, color=JSD_COLOR, label="R1 JSD")
    axes[0].set_xlabel("Mean JSD (EN vs ZH; lower is better)")
    axes[0].set_title("Cross-lingual divergence")
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(models)
    axes[0].invert_yaxis()
    axes[0].grid(axis="x", linestyle="--", alpha=0.35)
    axes[0].set_xlim(left=0)

    axes[1].barh(y - height / 2, cross["r1_top1"], height=height, color=TOP1_COLOR, label="R1 Top-1 match")
    axes[1].set_xlabel("Mean top-1 match (higher is better)")
    axes[1].set_title("Cross-lingual focal agreement")
    axes[1].set_xlim(0, 1.05)
    axes[1].grid(axis="x", linestyle="--", alpha=0.35)

    fig.suptitle("Round 1 cross-lingual stability (RQ2)", fontsize=11, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_figure_b(human: pd.DataFrame, out_path: Path) -> None:
    models = human["model_display"].tolist()
    x = np.arange(len(models))
    width = 0.38

    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    ax.bar(x - width / 2, human["en_jsd"], width, label="Human vs EN", color=EN_COLOR)
    ax.bar(x + width / 2, human["zh_jsd"], width, label="Human vs ZH", color=ZH_COLOR)

    ax.set_ylabel("Mean JSD (lower is closer to humans)")
    ax.set_xlabel("Model")
    ax.set_title("Round 1 human alignment (RQ1)")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=55, ha="right")
    ax.legend(loc="upper left", frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.set_ylim(bottom=0)

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cross = load_cross_lingual()
    human = load_human_alignment()

    fig_a = OUT / "round1_cross_lingual_stability.png"
    fig_b = OUT / "round1_human_alignment_jsd.png"
    plot_figure_a(cross, fig_a)
    plot_figure_b(human, fig_b)
    print(f"Wrote {fig_a}")
    print(f"Wrote {fig_b}")


if __name__ == "__main__":
    main()
