from videos import get_videos
from get_csv_name import get_csv_name
from display_plot import display
from save_file import write_data
from logo import _logos, _clear_terminal, _play_logo_intro

use_logo = True
if use_logo:
    _play_logo_intro(_logos, 0.3)

def check_channel(channel: str) -> str:
    endings: list[str] = ["/featured", "/posts", "/playlists", "/streams", "/shorts"]
    if not channel.endswith("/videos"):
        for ending in endings:
            if channel.endswith(ending):
                return channel.replace(ending, "/videos")
        if not channel.endswith("/videos"):
            return f"{channel}{"/videos"}"
    return channel


CHANNEL:  str  = input("Channel > ")
CHANNEL = check_channel(CHANNEL)


videos_x = get_videos(CHANNEL)
write_data(videos_x[0], CHANNEL, videos_x[1])
display(get_csv_name(CHANNEL))
