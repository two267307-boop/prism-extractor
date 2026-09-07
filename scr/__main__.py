from videos import get_videos
from get_csv_name import get_csv_name
from display_plot import display
from save_file import write_data

CHANNEL = input("Channel: ")

endings = ["/featured", "/posts", "playlists", "/streams", "/shorts"]

if not CHANNEL.endswith("/videos"):
    for ending in endings:
        if CHANNEL.endswith(ending):
            CHANNEL = CHANNEL.replace(ending, "/videos")
    if not CHANNEL.endswith("/videos"):
        CHANNEL += "/videos"

videos_x = get_videos(CHANNEL)
write_data(videos_x[0], CHANNEL, videos_x[1])
display(get_csv_name(CHANNEL))
