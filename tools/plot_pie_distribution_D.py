from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter


def main() -> None:
    # Extracted from screenshot: Choose one of 6 numbers
    labels = ["7", "100", "13", "261", "99", "555"]
    counts = [28, 41, 21, 0, 3, 7]

    out_path = Path(__file__).resolve().parents[1] / "figures" / "distribution_D_bar.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total = sum(counts)
    pct = np.array([c / total if total else 0.0 for c in counts], dtype=float)

    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    x = np.arange(len(labels))
    bars = ax.bar(x, pct, color=plt.rcParams["axes.prop_cycle"].by_key()["color"][: len(labels)])
    ax.set_title("Choose one of 6 numbers — distribution", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)

    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _pos: f"{y * 100:.0f}%"))
    ax.set_ylabel("Share", fontsize=10)
    ax.set_ylim(0, max(0.01, float(pct.max()) * 1.18))

    for rect, p in zip(bars, pct, strict=True):
        if p <= 0:
            continue
        ax.text(
            rect.get_x() + rect.get_width() / 2,
            rect.get_height(),
            f"{p * 100:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    fig.savefig(out_path.with_suffix(".pdf"))
    plt.close(fig)

    print(out_path)


if __name__ == "__main__":
    main()

