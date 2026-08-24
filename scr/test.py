from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
filepath = ROOT / "channels" /


files = [f for f in ROOT.iterdir() if f.is_file()]

latest_file = max(files, key=lambda f: f.stat().st_ctime)


print(latest_file)
print(ROOT)