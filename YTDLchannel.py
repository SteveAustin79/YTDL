from pytubefix import Channel

c = Channel("https://www.youtube.com/@NetworkChuck")

print(f'Lsiting videos by: {c.channel_name}')

i = 0

for video in c.videos:
    i = i+1
    print(str(i) + " - " + video.title)