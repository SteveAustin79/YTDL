from pytubefix import Channel

YTchannel = input("YouTube Channel URL: ")

c = Channel(YTchannel)
print(f'Listing videos by: {c.channel_name}')

i = 0

for video in c.videos:
    i = i+1
    print(str(i) + " - " + str(video.age_restricted) + " - " + video.video_id + " - " + video.title)

print("Total Videos: ", i)