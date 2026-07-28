try:
    import time
    import argparse
    from yt_dlp import YoutubeDL
    import csv
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
    default=1,
    help="delay in between requests")
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
CSV_FILENAME = "prism_results.csv"

fields: tuple[str, ...] = (
    "uploader_id",
    "channel",
    "channel_id",
    "channel_follower_count",
    "creator",
    "artist",
    "title",
    "thumbnail",
    "id",
    "duration",
    "duration_string",
    "view_count",
    "like_count",
    "comment_count",
    "repost_count",
    "average_rating",
    "categories",
    "tags",
    "language",
    "age_limit",
    "live_status",
    "was_live",
    "availability",
    "playlist",
    "playlist_id",
    "playlist_title",
    "playlist_index",
    "n_entries",
    "fps",
    "resolution",
    "format_id",
    "ext",
    "vcodec",
    "acodec",
    "dynamic_range",
    "aspect_ratio",
    "filesize",
    "tbr",
    "vbr",
    "abr",
    "asr",
    "audio_channels",
    "extractor",
    "extractor_key",
    "webpage_url",
    "original_url",
    "webpage_url_basename",
    "webpage_url_domain",
    "upload_date",
    "timestamp",
    "release_date",
    "release_timestamp",
    "modified_date",
    "license",
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
                    print(f"▸ [{index}/{len(videos)}] {info['title']}")
                    writer.writerow([info.get(field) for field in fields])

                except Exception as exp:
                    print(f"{url} failed.")
                    print(exp)
                    time.sleep(TIMEOUT_YTDLP)

def display_csv() -> None:
    df = pd.read_csv(CSV_FILENAME)

    views = df["view_count"].fillna(0).tolist()
    duration_rs = df["duration"].fillna(0).tolist()
    comments = df["comment_count"].fillna(0).tolist()
    likes = df["like_count"].fillna(0).tolist()
    reposts = df["repost_count"].fillna(0).tolist()
    filesize = df["filesize"].fillna(0).tolist()

    views.reverse()
    duration_rs.reverse()
    comments.reverse()
    likes.reverse()
    reposts.reverse()
    filesize.reverse()

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
    plt.show()

    print(df.to_string())
    input(">>> ")

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