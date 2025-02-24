from pytubefix import Channel

# Create an empty list
video_list = []

YTchannel = input("YouTube Channel URL: ")

c = Channel(YTchannel)
print(f'Listing videos by: {c.channel_name}')

i = 0

for video in c.videos:
    i = i+1
    print(str(i) + " - " + str(video.age_restricted) + " - " + video.video_id + " - " + video.title)
    video_list.append(video.video_id)

print("Total Videos: ", video_list.count())