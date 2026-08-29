from yt_dlp import YoutubeDL
import json
import pathlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "settings.json"

with open(SETTINGS, "r") as file:
    data: dict[str, dict[str, Any]] = json.load(file)
    ydl_opts: dict[str, Any] = data.get("ydl_opt")

def get_videos(channel: str) -> list[str] | str:
    videos: list[str] = []
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel, download=False)
        if info.get("entries") == None or info.get("entries") == []:
            return []
        for video in info.get("entries"):
            videos.append("https://www.youtube.com/watch?v=" + video["id"])
    return [videos, info]
