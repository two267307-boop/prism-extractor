"""Plot selected video metrics from a channel CSV."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


PLOTS = [
    ("view_count", "Views", "View count"),
    ("duration", "Duration", "Seconds"),
    ("comment_count", "Comments", "Comment count"),
    ("like_count", "Likes", "Like count"),
    ("filesize", "File size", "Bytes"),
    ("fps", "Frame rate", "FPS"),
]


def display(filename: str | Path) -> None:
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    available = [(column, title, label) for column, title, label in PLOTS if column in frame.columns]
    if not available:
        print(f"No plottable metric columns found in {path}")
        return

    columns = 2
    rows = (len(available) + columns - 1) // columns
    figure, axes = plt.subplots(rows, columns, figsize=(12, 4 * rows), squeeze=False)
    flat_axes = axes.ravel()
    for axis, (column, title, label) in zip(flat_axes, available):
        values = pd.to_numeric(frame[column], errors="coerce").fillna(0).iloc[::-1].reset_index(drop=True)
        axis.plot(values)
        axis.set_title(title)
        axis.set_ylabel(label)
        axis.set_xlabel("Video (oldest to newest)")
        axis.set_ylim(bottom=0)
        axis.grid(True, alpha=0.3)
        axis.xaxis.set_major_locator(MaxNLocator(integer=True))
    for axis in flat_axes[len(available):]:
        axis.set_visible(False)
    figure.tight_layout()
    plt.show()
