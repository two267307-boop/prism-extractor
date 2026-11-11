"""Command-line entry point for Prism Extractor."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .display_plot import display
from .save_file import save_channel_results
from .videos import extract_channel, normalize_channel_url

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = ROOT / "settings.json"


def load_settings() -> dict[str, Any]:
    try:
        with SETTINGS_PATH.open(encoding="utf-8") as stream:
            settings = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not load {SETTINGS_PATH}: {exc}") from exc
    settings.setdefault("concurrency", {})
    settings["concurrency"].setdefault("channels", 3)
    settings["concurrency"].setdefault("retries", 2)
    settings["concurrency"].setdefault("retry_delay", 5)
    return settings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="prism-extractor",
        description="Collect public metadata from one or more YouTube channels.",
    )
    parser.add_argument(
        "channels",
        nargs="*",
        help="YouTube channel URLs or handles (separate multiple channels with spaces).",
    )
    parser.add_argument(
        "-c", "--channel",
        action="append",
        dest="extra_channels",
        default=[],
        help="Add a channel; may be supplied more than once.",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=None,
        help="Maximum number of channels processed concurrently (default: settings.json).",
    )
    parser.add_argument("--gui", action="store_true", help="Open the desktop windowed interface.")
    parser.add_argument("--no-plot", action="store_true", help="Do not display result plots.")
    parser.add_argument("--no-logo", action="store_true", help="Skip the animated terminal logo.")
    parser.add_argument("--version", action="version", version="Prism Extractor 2.0.0")
    args = parser.parse_args(argv)
    args.channels = list(dict.fromkeys(args.channels + args.extra_channels))
    if not args.channels and not args.gui:
        parser.error("provide at least one channel URL or handle, or use --gui")
    if args.workers is not None and args.workers < 1:
        parser.error("--workers must be at least 1")
    return args


def _process_one(channel: str, settings: dict[str, Any]) -> tuple[str, Path | None, Exception | None]:
    try:
        result = extract_channel(channel, settings)
        if not result["videos"]:
            logging.warning("%s: no videos were found", channel)
        output_dir = save_channel_results(result, settings)
        logging.info("%s: saved %d video records to %s", channel, len(result["videos"]), output_dir)
        return channel, output_dir, None
    except Exception as exc:  # Keep one channel's failure from cancelling the others.
        logging.exception("%s: channel processing failed", channel)
        return channel, None, exc


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.gui:
        from .gui import main as gui_main
        gui_main()
        return 0
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = load_settings()

    if not args.no_logo and settings.get("show_logo", True):
        try:
            from .logo import _logos, _play_logo_intro
            _play_logo_intro(_logos, 0.08)
        except (ImportError, OSError):
            pass

    channels = [normalize_channel_url(value) for value in args.channels]
    workers = args.workers or int(settings["concurrency"]["channels"])
    workers = max(1, min(workers, len(channels)))

    print(f"Processing {len(channels)} channel(s) with {workers} worker(s).")
    outputs: list[Path] = []
    failures = 0
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="prism-channel") as pool:
        futures = {pool.submit(_process_one, channel, settings): channel for channel in channels}
        for future in as_completed(futures):
            channel, output_dir, error = future.result()
            if error is not None:
                failures += 1
                print(f"[FAILED] {channel}: {error}", file=sys.stderr)
            elif output_dir is not None:
                outputs.append(output_dir)
                print(f"[DONE] {channel} -> {output_dir}")

    if not args.no_plot:
        for output_dir in outputs:
            csv_path = output_dir / "csv" / "latest.csv"
            if csv_path.exists():
                display(csv_path)

    print(f"Finished: {len(outputs)} succeeded, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
