try:
    from pathlib import Path
    from yt_dlp import YoutubeDL
except ModuleNotFoundError as e:
    raise SystemExit(f"Module {e} not found.")
from datetime import datetime
import time
import json
import csv



def write_data(videos: list[str], channel: str, raw_data: dict) -> None | Exception:
    if videos is None or videos == []:
        raise SystemExit("No videos to loop over, empty list")
    if channel is None or channel == "":
        raise SystemExit("Channel not given, this is required for folder names.")

    start = channel.find("@")
    end = channel.find("/", start)
    if end == -1:
        channel_name = channel[start:]
    else:
        channel_name = channel[start:end]

    #directory name stuff
    ROOT = Path(__file__).resolve().parent.parent
    SETTINGS = ROOT / "settings.json"
    CHANNELS = ROOT / "channels"

    channel_dir = CHANNELS / channel_name
    results_dir = channel_dir / "results"
    raw_data_dir = channel_dir / "raw"
    logs_dir = channel_dir / "logs"
    json_dir = results_dir / "json"
    csv_dir = results_dir / "csv"

    #create directories
    dirs = (channel_dir, results_dir, raw_data_dir, logs_dir, json_dir, csv_dir)
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

    #loading settings
    with open(SETTINGS, "r") as file:
        data: dict[str, dict] = json.load(file)

        YDL_OPTIONS = data.get("ydl_opt")

        EMERGENCY_TIMEOUT = data.get("saving").get("em_timeout")
        DEFAULT_TIMEOUT   = data.get("saving").get("df_timeout")
        FIELDS            = data.get("saving").get("fields")

        SAVE_RAW   = data.get("raw").get("save_raw")
        SAVE_LOG   = data.get("logging").get("save_log")
        SAVE_JSON  = data.get("json").get("save_json")
        SAVE_CSV   = data.get("csv").get("save_csv")

        RAW_DATETYPE  = data.get("raw").get("format")
        LOG_DATETYPE  = data.get("logging").get("format")
        JSON_DATETYPE = data.get("json").get("format")
        CSV_DATETYPE  = data.get("csv").get("format")

        RAW_INDENT    = data.get("raw").get("indent")
        JSON_INDENT    = data.get("json").get("indent")

    if not SAVE_RAW and not SAVE_LOG and not SAVE_JSON and not SAVE_CSV:
        raise SystemExit("No savestate enabled")

    filename_raw = channel_dir / "raw" / f"raw_{datetime.now().strftime(RAW_DATETYPE)}.json"
    filename_log = channel_dir / "logs" / f"log_{datetime.now().strftime(LOG_DATETYPE)}.txt"
    filename_json = channel_dir / "results" / "json" / f"Result_{datetime.now().strftime(JSON_DATETYPE)}.json"
    filename_csv = channel_dir / "results" / "csv" / f"Result_{datetime.now().strftime(CSV_DATETYPE)}.csv"

    #I lowkey had no clue how to do this so I did kinda relie on chatgpt
    csv_file = None
    csv_writer = None

    if SAVE_CSV:
        csv_file = open(filename_csv, "a", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(FIELDS)

    json_file = None
    first_json = True

    if SAVE_JSON:
        json_file = open(filename_json, "w", encoding="utf-8")
        json_file.write("[")

    if SAVE_RAW:
        with open(filename_raw, "w") as rawfile:
            json.dump(raw_data, rawfile, indent=RAW_INDENT)
            rawfile.flush()

    if SAVE_LOG:
        log_file = open(filename_log, "a", encoding="utf-8")

    with YoutubeDL(YDL_OPTIONS) as ydl:
        for index, url in enumerate(videos, start=1):
            time.sleep(DEFAULT_TIMEOUT)

            try:
                info = ydl.extract_info(url, download=False)
                print(f"▸ [{index}/{len(videos)}] : [{index / len(videos) * 100:.1f}%] {info["title"]}")

                if SAVE_CSV:
                    csv_writer.writerow([info.get(field) for field in FIELDS])
                    csv_file.flush()

                    if SAVE_JSON:
                        json_info = {field: info.get(field) for field in FIELDS}

                        if not first_json:
                            json_file.write(",")

                        json.dump(json_info, json_file, indent=JSON_INDENT)
                        json_file.flush()

                        first_json = False

                if SAVE_LOG:
                    log_file.write(f"{index} | {url} | {datetime.now().strftime(LOG_DATETYPE)} | succeeded\n")

            except Exception as exp:
                print(f"{url} failed. It will be skipped and excluded. {exp}")
                if SAVE_LOG:
                    log_file.write(f"{index} | {url} | {datetime.now().strftime(LOG_DATETYPE)} | failed\n")
                time.sleep(EMERGENCY_TIMEOUT)

        if SAVE_JSON:
            json_file.write("]")
            json_file.close()

        if SAVE_CSV:
            csv_file.close()

        if SAVE_LOG:
            log_file.close()



