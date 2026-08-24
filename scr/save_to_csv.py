import os
import csv
import json
import time
import glob
import pathlib
from pathlib import Path
from yt_dlp import YoutubeDL
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "settings.json"
CHANNELS = ROOT / "channels"

with open(SETTINGS, "r") as file:
    data: dict[str, dict] = json.load(file)
    ydl_opts: dict[str, bool] = data.get("ydl_opt")
    csv_timeout: int = data.get("csv").get("em_timeout")
    datetype: str = data.get("csv").get("datetype")
    fields: list[str] = data.get("csv").get("fields")

def write_to_csv(videos: list[str], channel: str) -> None:
    channel_name = channel[channel.find("@")::]
    channel_dir = CHANNELS / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    filename = channel_dir / f"Result{datetime.now().strftime(datetype)}.csv"

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

def get_csv_name(channel: str) -> str:
    channel_name: str = channel[channel.find("@")::]
    filepath_get_csv: Path = ROOT / "channels" / channel_name
    files: list[Path] = [f for f in filepath_get_csv.iterdir() if f.is_file()]
    return max(files, key=lambda f: f.stat().st_ctime)


print(get_csv_name("https://www.youtube.com/@fixmyoculus"))