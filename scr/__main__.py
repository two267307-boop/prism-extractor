from videos import get_videos
from save_to_csv import write_to_csv, get_csv_name
from display_plot import display

CHANNEL = "https://www.youtube.com/@Blur009_2/videos"
if not "/videos" in CHANNEL:
    CHANNEL += "/videos"



write_to_csv(get_videos(CHANNEL), CHANNEL)
display(get_csv_name(CHANNEL))
