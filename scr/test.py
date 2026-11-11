
from get_csv_name import get_csv_name
from display_plot import  display
from pathlib import  Path
import  pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator



def check_channel(channel: str) -> str:
    endings: list[str] = ["/featured", "/posts", "/playlists", "/streams", "/shorts"]
    if not channel.endswith("/videos"):
        for ending in endings:
            if channel.endswith(ending):
                return channel.replace(ending, "/videos")
        if not channel.endswith("/videos"):
            return f"{channel}{"/videos"}"
    return channel
CHANNEL = "https://www.youtube.com/@pumpknss/videos"

CHANNEL = check_channel(CHANNEL)

display(get_csv_name(CHANNEL))

