


channel = "https://www.youtube.com/@Ididathing/videos"
start = channel.find("@")
end = channel.find("/", start)
if end == -1:
    channel_name = channel[start:]
else:
    channel_name = channel[start:end]

print(channel_name)