from pytubefix import Channel

version = 0.1

# Create an empty list
video_list = []
video_list_restricted = []

print("\nYTDLchannel " + str(version))
print("***************")
print("YouTube Channel Downloader (Exit App with Ctrl + C)\n")

YTchannel = input("YouTube Channel URL: ")

c = Channel(YTchannel)
print(f'\nListing videos by: {c.channel_name}')

count_total_videos = 0
count_restricted_videos = 0
count_ok_videos = 0

for video in c.videos:
    count_total_videos = count_total_videos+1
    if video.age_restricted == False:
        count_ok_videos = count_ok_videos + 1
        video_list.append(video.video_id)
        print(str(count_total_videos) + " - " + video.video_id + " - " + video.title)
    else:
        count_restricted_videos = count_restricted_videos+1
        video_list_restricted.append(video.video_id)
        print("\033[31m" + str(count_total_videos) + " - " + video.video_id + " - " + video.title + "\033[0m")
    if count_total_videos==10:
        break

print("Total Videos: " + str(count_total_videos) + ", OK Videos: " + str(count_ok_videos)
      + ", Restricted Videos: " + count_restricted_videos)
