from pytubefix import Channel

c = Channel("https://www.youtube.com/@NetworkChuck")

print(f'Lsiting videos by: {c.channel_name}')

for video in c.videos:
    print(video.title + "\n")