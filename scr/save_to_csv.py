try:
    from pathlib import Path
    from yt_dlp import YoutubeDL
except ModuleNotFoundError as e:
    raise SystemExit(f"Module {e} not found.")
import json
import csv
from datetime import datetime
import time

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "settings.json"
CHANNELS = ROOT / "channels"

with open(SETTINGS, "r") as file:
    data: dict[str, dict] = json.load(file)
    ydl_opts: dict[str, bool] = data.get("ydl_opt")
    default_timeout: int = data.get("csv").get("df_timeout")
    emergency_timeout: int = data.get("csv").get("em_timeout")
    datetype: str = data.get("csv").get("datetype")
    fields: list[str] = data.get("csv").get("fields")
    LOGGING: bool = data.get("logging").get("log")
    datetype_logging: str = data.get("logging").get("format")

def write_to_csv(videos: list[str], channel: str) -> None:
    log = []

    start = channel.find("@")
    end = channel.find("/", start)
    if end == -1:
        channel_name = channel[start:]
    else:
        channel_name = channel[start:end]

    channel_dir = CHANNELS / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)
    filename = channel_dir / f"Result_{datetime.now().strftime(datetype)}.csv"
    filename_log = channel_dir / f"log_{datetime.now().strftime(datetype_logging)}.txt"

    with YoutubeDL(ydl_opts) as ydl:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(fields)

            for index, url in enumerate(videos, start=1):
                time.sleep(default_timeout)
                try:
                    info = ydl.extract_info(url, download=False)
                    print(f"▸ [{index}/{len(videos)}] : [{index / len(videos) * 100:.1f}%] {info["title"]}")
                    writer.writerow([info.get(field) for field in fields])
                    file.flush()
                    log.append(f"{index} | {url} | {datetime.now().strftime(datetype_logging)} | succeeded\n")
                except Exception as exp:
                    print(f"{url} failed. It will be skipped and excluded. {exp}")
                    log.append(f"{index} | {url} | {datetime.now().strftime(datetype_logging)} | failed:\n")
                    time.sleep(emergency_timeout)
        if LOGGING:
            with open(filename_log, "w", newline="", encoding="utf-8") as file:
                for line in log:
                    file.write(line)
    return None

def get_csv_name(channel: str) -> str:
    start = channel.find("@")
    end = channel.find("/", start)
    if end == -1:
        channel_name = channel[start:]
    else:
        channel_name = channel[start:end]

    filepath_get_csv: Path = ROOT / "channels" / channel_name
    files = [f for f in filepath_get_csv.iterdir() if f.is_file() and f.suffix == ".csv"]
    return max(files, key=lambda f: f.stat().st_ctime)

