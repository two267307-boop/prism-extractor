import os
import csv
import json
import time
from yt_dlp import YoutubeDL
from datetime import datetime

with open("../settings.json", "r") as file:
    data: dict[str, dict] = json.load(file)
    ydl_opts: dict[str, bool] = data.get("ydl_opt")
    csv_timeout: int = data.get("csv").get("em_timeout")
    datetype: str = data.get("csv").get("datetype")
    fields: list[str] = data.get("csv").get("fields")

def write_to_csv(videos: list[str], channel: str) -> None:
    channel_name = channel[channel.find("@")::]
    directory = fr"..\channels\{channel_name}"
    os.makedirs(directory, exist_ok=True)
    filename = fr"{directory}\Result{datetime.now().strftime(datetype)}.csv"

    with YoutubeDL(ydl_opts) as ydl:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(fields)

            for index, url in enumerate(videos, start=1):
                time.sleep(csv_timeout)
                try:
                    info = ydl.extract_info(url, download=False)
                    print(f"▸ [{index}/{len(videos)}] : [{index / len(videos) * 100:.1f}%] {info["title"]}")
                    writer.writerow([info.get(field) for field in fields])
                    file.flush()
                except Exception as exp:
                    print(f"{url} failed. It will be skipped and excluded. {exp}")
                    time.sleep(csv_timeout)
    return None

