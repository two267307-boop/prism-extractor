import time
import argparse
import csv
import os
try:
    from yt_dlp import YoutubeDL
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib.ticker import MaxNLocator

except ModuleNotFoundError as e:
    print(e)
    raise SystemExit(1)

parser = argparse.ArgumentParser(description="Analyze a YouTube channel")
parser.add_argument(
    "channel",
    nargs="?",
    help="YouTube channel url")
parser.add_argument(
    "-t", "--timeout",
    type=int,
    default=2,
    help="delay in between requests")
parser.add_argument(
    "-s", "--save",
    action="store_true",
    help="Save plot as png automatically")
parser.add_argument(
    "-r", "--reuse",
    action="store_true",
    help="Reuse existing data")
args = parser.parse_args()


ydl_opts: dict[str, bool] = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": True,
    "skip_download": True,
}

TIMEOUT_YTDLP: int = 60 #script will wait for given amount of time before going to the next video, the failed one will not be used for analyzation.
CSV_FILENAME: str = "prism_results.csv"

fields: tuple[str, ...] = (
    "uploader_id","channel","channel_id","channel_follower_count",
    "creator","artist","title","thumbnail",
    "id","duration","duration_string","view_count","like_count",
    "comment_count","repost_count","average_rating","categories",
    "tags","language","age_limit","live_status","was_live",
    "availability","playlist","playlist_id","playlist_title",
    "playlist_index","n_entries","fps","resolution",
    "format_id","ext","vcodec","acodec",
    "dynamic_range","aspect_ratio","filesize","tbr",
    "vbr","abr","asr","audio_channels",
    "extractor","extractor_key","webpage_url","original_url",
    "webpage_url_basename","webpage_url_domain","upload_date","timestamp",
    "release_date","release_timestamp","modified_date","license",
    "epoch",
)


def get_videos(channel: str) -> list[str]:
    videos: list[str] = []
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel, download=False)
        for video in info["entries"]:
            videos.append("https://www.youtube.com/watch?v=" + video["id"])
    return videos

def write_to_csv(videos: list[str], timeout: int=15) -> None:
    with YoutubeDL(ydl_opts) as ydl:
        with open(CSV_FILENAME, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(fields)

            for index, url in enumerate(videos, start=1):
                time.sleep(timeout)
                try:
                    info = ydl.extract_info(url, download=False)
                    print(f"▸ [{index}/{len(videos)}] [{index / len(videos) * 100:.1f}%] {info['title']}")
                    writer.writerow([info.get(field) for field in fields])
                    file.flush()
                except Exception as exp:
                    print(f"{url} failed.")
                    print(exp)
                    time.sleep(TIMEOUT_YTDLP)

def display_csv() -> None:
    df = pd.read_csv(CSV_FILENAME)
    
    views = df["view_count"].fillna(0).tolist()[::-1]
    duration_rs = df["duration"].fillna(0).tolist()[::-1]
    comments = df["comment_count"].fillna(0).tolist()[::-1]
    likes = df["like_count"].fillna(0).tolist()[::-1]
    reposts = df["repost_count"].fillna(0).tolist()[::-1]
    filesize = df["filesize"].fillna(0).tolist()[::-1]

    fig, axes = plt.subplots(3, 2, figsize=(10, 8))
    ax1, ax2, ax3, ax4, ax5, ax6 = axes.ravel()

    plots: list[tuple] = [
        (ax1, views, "Total Views", "Views"),
        (ax2, duration_rs, "Duration", "Seconds"),
        (ax3, comments, "Comments", "Comments"),
        (ax4, likes, "Likes", "Likes"),
        (ax5, filesize, "Filesize", "Bytes"),
        (ax6, reposts, "Reposts", "Reposts"),
    ]

    for ax, data, title, ylabel in plots:
        ax.plot(data)
        ax.set_ylim(bottom=0)
        ax.grid(True)
        ax.set_xlabel("Video")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.tight_layout()
    if args.save:
        plt.savefig("analysis.png", dpi=600)
    plt.show()

    print(df.to_string())
    input("> ")

def start() -> None:
    if args.reuse:
        display_csv()
        return
    if args.channel is None:
        parser.error("channel is required unless --reuse is used")
    else:
        videos: list[str] = get_videos(args.channel)
        write_to_csv(videos, args.timeout)
        display_csv()
        print("Finished!")

if __name__ == "__main__":
    start()



"""
create directories

prism/
├───README.md
├───Src/
│   ├───__main__
│   ├───get_videos.py
│   ├───writeo_to_csv.py
│   ├───display_graph.py
│   └───app.py
├───creators/
│   ├───@USER_1/
│   │   ├───Result_2025_01_02.csv
│   │   └───Result_2025_02_03.csv
│   └───@USER_2/
│       ├───Result_2025_01_02.csv
│       └───Result_2025_02_03.csv
└───settings.json 

├───
│   ├───
│   │   └───
│   └───
└───
"""
























