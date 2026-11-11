"""YouTube channel discovery and video metadata extraction."""
from __future__ import annotations

import logging
import re
import time
from typing import Any
from urllib.parse import urlparse

try:
    from yt_dlp import YoutubeDL
except ImportError as exc:  # pragma: no cover - depends on environment
    raise SystemExit("Missing dependency: install requirements with 'python -m pip install -r requirements.txt'.") from exc


CHANNEL_SUFFIXES = ("/featured", "/posts", "/playlists", "/streams", "/shorts", "/videos", "/about", "/community")


def normalize_channel_url(channel: str) -> str:
    """Accept a channel URL, @handle, or bare handle and return its videos URL."""
    value = channel.strip()
    if not value:
        raise ValueError("channel cannot be empty")
    if value.startswith("@"):
        value = "https://www.youtube.com/" + value
    elif "://" not in value:
        value = "https://www.youtube.com/@" + value.lstrip("/")
    parsed = urlparse(value)
    if parsed.netloc.lower() not in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        raise ValueError(f"not a supported YouTube URL: {channel}")
    path = parsed.path.rstrip("/")
    for suffix in CHANNEL_SUFFIXES:
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break
    if not path or path == "/":
        raise ValueError(f"could not identify a channel in URL: {channel}")
    return f"https://www.youtube.com{path}/videos"


def _ydl_options(settings: dict[str, Any], *, flat: bool) -> dict[str, Any]:
    options = dict(settings.get("ydl_opt", {}))
    options.update({"quiet": True, "no_warnings": True, "skip_download": True})
    options["extract_flat"] = flat
    options.pop("download", None)
    return options


def extract_channel(channel: str, settings: dict[str, Any]) -> dict[str, Any]:
    """Discover a channel's videos, then extract each video's metadata."""
    channel_url = normalize_channel_url(channel)
    retry_settings = settings.get("concurrency", {})
    retries = max(0, int(retry_settings.get("retries", 2)))
    retry_delay = max(0.0, float(retry_settings.get("retry_delay", 5)))
    playlist_info: dict[str, Any] | None = None
    videos: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    with YoutubeDL(_ydl_options(settings, flat=True)) as ydl:
        playlist_info = ydl.extract_info(channel_url, download=False)
    entries = (playlist_info or {}).get("entries") or []
    entries = [entry for entry in entries if entry]
    logging.info("%s: discovered %d entries", channel_url, len(entries))

    detail_options = _ydl_options(settings, flat=False)
    for index, entry in enumerate(entries, start=1):
        video_id = entry.get("id")
        url = entry.get("url") or entry.get("webpage_url")
        if not url and video_id:
            url = f"https://www.youtube.com/watch?v={video_id}"
        if not url:
            failures.append({"id": str(video_id or ""), "error": "entry has no usable URL"})
            continue

        for attempt in range(retries + 1):
            try:
                with YoutubeDL(detail_options) as ydl:
                    info = ydl.extract_info(url, download=False)
                if info:
                    videos.append(info)
                logging.info("%s: processed %d/%d", channel_url, index, len(entries))
                break
            except Exception as exc:
                if attempt >= retries:
                    failures.append({"id": str(video_id or url), "error": str(exc)})
                    logging.warning("%s: skipping %s after %d attempt(s): %s", channel_url, url, attempt + 1, exc)
                else:
                    time.sleep(retry_delay * (attempt + 1))

    return {
        "channel_url": channel_url,
        "channel_info": playlist_info or {},
        "videos": videos,
        "failures": failures,
    }


def get_videos(channel: str) -> tuple[list[str], dict[str, Any]]:
    """Compatibility wrapper for the original API."""
    settings = {"ydl_opt": {"quiet": True, "no_warnings": True}, "concurrency": {"retries": 1}}
    result = extract_channel(channel, settings)
    urls = [video.get("webpage_url") or f"https://www.youtube.com/watch?v={video['id']}"
            for video in result["videos"] if video.get("id")]
    return urls, result["channel_info"]
