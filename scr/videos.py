from yt_dlp import YoutubeDL
import json

with open("../settings.json", "r") as file:
    data: dict[str, dict[str, bool]] = json.load(file)
    ydl_opts: dict[str, bool] = data.get("ydl_opt")

def get_videos(channel: str) -> list[str]:
    videos: list[str] = []
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel, download=False)
        for video in info.get("entries"):
            videos.append("https://www.youtube.com/watch?v=" + video["id"])
    return videos
