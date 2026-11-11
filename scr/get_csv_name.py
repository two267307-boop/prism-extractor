"""Locate the latest CSV generated for a channel."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def get_csv_name(channel: str) -> Path:
    match = re.search(r"/(@[^/]+|channel/[^/]+|c/[^/]+|user/[^/]+)", channel)
    slug = match.group(1) if match else "channel"
    directory = ROOT / "channels" / slug / "results" / "csv"
    latest = directory / "latest.csv"
    if latest.is_file():
        return latest
    files = sorted(directory.glob("Result_*.csv"), key=lambda path: path.stat().st_mtime)
    if not files:
        raise FileNotFoundError(f"No CSV results found for {channel}")
    return files[-1]
