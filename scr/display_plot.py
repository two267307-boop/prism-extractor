import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

def display(filename) -> None:
    df: pd.DataFrame = pd.read_csv(filename)

    fig, axes = plt.subplots(3, 2, figsize=(10, 8))
    ax1, ax2, ax3, ax4, ax5, ax6 = axes.ravel()

    plots: list[tuple] = [
        (ax1, "view_count", "Views", "View Count"),
        (ax2, "duration", "Seconds", "Seconds"),
        (ax3, "comment_count", "Comments", "Comment Count"),
        (ax4, "like_count", "Likes", "likes"),
        (ax5, "filesize", "Filesize", "bytes"),
        (ax6, "fps", "FPS", "frames"),
    ]

    for ax, column, title, label in plots:
        data = df[column].fillna(0).tolist()[::-1]

        ax.plot(data)
        ax.set_ylim(bottom=0)
        ax.grid(True)
        ax.set_ylabel(label)
        ax.set_title(title)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()
    plt.show()
