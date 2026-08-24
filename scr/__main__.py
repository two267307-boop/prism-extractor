from videos import get_videos
from save_to_csv import write_to_csv

write_to_csv(get_videos("https://www.youtube.com/@fixmyoculus"), "https://www.youtube.com/@fixmyoculus")