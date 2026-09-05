try:
    from pathlib import Path
    from yt_dlp import YoutubeDL
except ModuleNotFoundError as e:
    raise SystemExit(f"Module {e} not found.")
import json
import csv
from datetime import datetime
import time
import json



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
    SAVE_RAW: bool = data.get("raw").get("save_raw")

def write_to_csv(videos: list[str], channel: str, raw_data: str) -> None:
    log = []
    if videos == []:
        raise SystemExit("No public videos available")

    start = channel.find("@")
    end = channel.find("/", start)
    if end == -1:
        channel_name = channel[start:]
    else:
        channel_name = channel[start:end]

    channel_dir = CHANNELS / channel_name
    results_dir = channel_dir / "results"
    raw_data_dir = channel_dir / "raw"
    logs_dir = channel_dir / "logs"

    dirs = (channel_dir, results_dir, raw_data_dir, logs_dir)
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

    filename = channel_dir / "results" / f"Result_{datetime.now().strftime(datetype)}.csv"
    filename_json = channel_dir / "raw" / f"raw_{datetime.now().strftime(datetype)}.json"
    filename_log = channel_dir / "logs" / f"log_{datetime.now().strftime(datetype_logging)}.txt"

    with YoutubeDL(ydl_opts) as ydl:
        if SAVE_RAW:
            with open(filename_json, "w") as jsfile:
                json.dump(raw_data, jsfile, indent=4)
                jsfile.flush()

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
                    log.append(f"{index} | {url} | {datetime.now().strftime(datetype_logging)} | failed\n")
                    time.sleep(emergency_timeout)
        if LOGGING:
            with open(filename_log, "w", newline="", encoding="utf-8") as file:
                for line in log:
                    file.write(line)
    return None

def get_csv_name(channel: str) -> Path:
    start = channel.find("@")
    end = channel.find("/", start)

    if end == -1:
        channel_name = channel[start:]
    else:
        channel_name = channel[start:end]

    filepath = ROOT / "channels" / channel_name

    files = [
        f for f in filepath.iterdir()
        if f.is_file() and f.suffix == ".csv"
    ]

    return max(files, key=lambda f: f.stat().st_ctime)

