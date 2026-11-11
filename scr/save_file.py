"""Safe, channel-isolated output writers."""
from __future__ import annotations

import csv
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIELDS = ["id", "title", "uploader", "upload_date", "duration", "view_count",
                  "like_count", "comment_count", "fps", "width", "height", "filesize",
                  "thumbnail", "webpage_url"]


def channel_slug(channel_info: dict[str, Any], channel_url: str) -> str:
    # Prefer the stable human-readable handle so legacy tools can locate the folder.
    match = re.search(r"/(@[^/]+|channel/[^/]+|c/[^/]+|user/[^/]+)", channel_url)
    candidate = match.group(1) if match else (
        (channel_info or {}).get("channel_id") or (channel_info or {}).get("id") or "channel"
    )
    slug = re.sub(r"[^A-Za-z0-9_.@-]+", "_", str(candidate)).strip("._")
    return slug or "channel"


def save_channel_results(result: dict[str, Any], settings: dict[str, Any]) -> Path:
    channel_info = result.get("channel_info") or {}
    channel_url = result["channel_url"]
    videos = result.get("videos") or []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d--%H-%M-%S-%f")
    channel_dir = ROOT / "channels" / channel_slug(channel_info, channel_url)
    raw_dir = channel_dir / "raw"
    logs_dir = channel_dir / "logs"
    json_dir = channel_dir / "results" / "json"
    csv_dir = channel_dir / "results" / "csv"
    for directory in (raw_dir, logs_dir, json_dir, csv_dir):
        directory.mkdir(parents=True, exist_ok=True)

    fields = settings.get("saving", {}).get("fields") or DEFAULT_FIELDS
    exported = [{field: video.get(field) for field in fields} for video in videos]

    if settings.get("raw", {}).get("save_raw", True):
        (raw_dir / f"raw_{now}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )

    if settings.get("json", {}).get("save_json", True):
        json_path = json_dir / f"Result_{now}.json"
        json_path.write_text(
            json.dumps(exported, ensure_ascii=False,
                       indent=settings.get("json", {}).get("indent", 2), default=str),
            encoding="utf-8",
        )

    if settings.get("csv", {}).get("save_csv", True):
        csv_path = csv_dir / f"Result_{now}.csv"
        with csv_path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(exported)
        latest_tmp = csv_dir / f"latest-{now}.tmp"
        latest_tmp.write_bytes(csv_path.read_bytes())
        latest_tmp.replace(csv_dir / "latest.csv")

    if settings.get("logging", {}).get("save_log", True):
        log_path = logs_dir / f"log_{now}.txt"
        lines = [f"Channel: {channel_url}", f"Videos discovered: {len(videos)}",
                 f"Video failures: {len(result.get('failures') or [])}"]
        lines.extend(f"FAILED {failure.get('id')}: {failure.get('error')}"
                     for failure in result.get("failures", []))
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    logging.info("Wrote channel data to %s", channel_dir)
    return channel_dir
