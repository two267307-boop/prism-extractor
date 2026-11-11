# Prism Extractor

Prism Extractor collects public video metadata from YouTube channels and exports it to CSV and JSON, with optional plots.

## Features

- Process multiple channels concurrently.
- Isolate channel failures so one unavailable channel does not cancel the others.
- Retry transient video extraction errors with configurable backoff.
- Keep each channel's output in its own directory.
- Export timestamped CSV/JSON, raw extraction data, and a per-run log.
- Generate plots for metrics available in the exported CSV.

## Install

Python 3.10 or newer is recommended.

```bash
git clone https://github.com/two267307-boop/prism-extractor.git
cd prism-extractor
python -m pip install -r requirements.txt
```

## Desktop app

Launch the windowed interface with:

```bash
python -m scr --gui
```

Paste one channel URL or `@handle` per line, choose the maximum number of concurrent workers, and click **Start extraction**. Each channel gets its own worker panel with an independent status, progress bar, and live log. The GUI uses the same extraction and output code as the CLI. Tkinter is included with most standard Python installations; on some Linux distributions it may need to be installed separately (for example, `python3-tk`).

## Usage

Pass one or more channel URLs or handles:

```bash
python -m scr https://www.youtube.com/@SomeChannel @AnotherChannel
```

You can also repeat `--channel`:

```bash
python -m scr --channel @SomeChannel --channel @AnotherChannel --workers 4
```

Useful options:

- `--workers N`: maximum number of channels processed at the same time.
- `--no-plot`: save results without opening plot windows.
- `--no-logo`: skip the terminal animation.
- `--version`: print the program version.

Run `python -m scr --help` for the complete CLI help.

## Output layout

```
channels/
  <channel-id-or-handle>/
    raw/
    logs/
    results/
      csv/
        Result_<timestamp>.csv
        latest.csv
      json/
        Result_<timestamp>.json
```

## Configuration

Edit `settings.json` to configure yt-dlp options, concurrency, retries, exported fields, and output formats. Keep channel concurrency modest; YouTube may throttle automated requests.

The tool only requests metadata (`download=False`) and does not download video files.
