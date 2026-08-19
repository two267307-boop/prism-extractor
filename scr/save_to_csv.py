import os
import csv
import json
import time
from yt_dlp import YoutubeDL
from datetime import datetime

from videos import get_videos


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

def write_to_csv(videos: list[str], channel: str, fields: tuple[str, ...]) -> None:
    with open("../settings.json", "r") as file:
        data: dict[str, dict] = json.load(file)
        ydl_opts: dict[str, bool] = data.get("ydl_opt")
        csv_timeout: int = data.get("csv").get("em_timeout")
        datetype = data.get("csv").get("datetype")

    channel_name = channel[channel.find("@")::]
    directory = fr"..\..\channels\{channel_name}"
    os.makedirs(directory, exist_ok=True)
    filename = fr"{directory}\Result{datetime.now().strftime(datetype)}"

    with YoutubeDL(ydl_opts) as ydl:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(fields)

            for index, url in enumerate(videos, start=1):
                time.sleep(csv_timeout)
                try:
                    info = ydl.extract_info(url, download=False)
                    print(f"▸ [{index}/{len(videos)}] : [{index / len(videos) * 100:.1f}%] {info['title']}")
                    writer.writerow([info.get(field) for field in fields])
                    file.flush()
                except Exception as exp:
                    print(f"{url} failed. It will be skipped. \n{exp}")
                    time.sleep(csv_timeout)

write_to_csv(get_videos("https://www.youtube.com/@pumpknss"), "https://www.youtube.com/@pumpknss", fields)