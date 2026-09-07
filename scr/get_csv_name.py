from pathlib import Path

def get_csv_name(channel: str) -> str | Exception:
    try:
        start = channel.find("@")
        end = channel.find("/", start)
    except ValueError as ve:
        return ve
    if end == -1:
        channel_name = channel[start:]
    else:
        channel_name = channel[start:end]
    try:
        ROOT = Path(__file__).resolve().parent.parent
        filepath_get_csv: Path = ROOT / "channels" / channel_name
        files = [f for f in filepath_get_csv.iterdir() if f.is_file() and f.suffix == ".csv"]
        return max(files, key=lambda f: f.stat().st_ctime)
    except Exception:
        return Exception