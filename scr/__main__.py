from videos import get_videos
from save_to_csv import write_to_csv, get_csv_name
from display_plot import display

CHANNEL = "https://www.youtube.com/@JoeBartGames"

#if CHANNEL.endswith("/featured"):
    #CHANNEL.replace("/featured", "/videos")
#elif CHANNEL.endswith()
#if not CHANNEL.endswith("/videos"):
    #CHANNEL += "/video"


if not "/videos" in CHANNEL:
    CHANNEL += "/videos"

videos_x = get_videos(CHANNEL)

write_to_csv(videos_x[0], CHANNEL, videos_x[1])
display(get_csv_name(CHANNEL))
