from pytubefix import YouTube
from pytubefix.cli import on_progress

try:
    # Ask the user to input the YouTube URL
    url = input("Enter the YouTube URL: ")

    yt = YouTube(url, on_progress_callback = on_progress)

    print("\n")
    print("Title:", yt.title)
    print("Views:", yt.views)
    print("\n")
    #print(yt.streams.filter(file_extension='mp4'))
    #print(yt.streams)
    #print("\n")

    #videoVersion = input ("Enter itag: ")
    res = input("Enter wanted resolution (1080p): ")

    dlpath = input("Enter path to download: ")

    # Get the highest resolution stream
    #yd = yt.streams.get_by_itag(videoVersion)
    #yd = yt.streams.get_highest_resolution()

    # Download the video to the current directory
    #yd.download(output_path=dlpath)

    for idx, i in enumerate(yt.streams):
        if i.resolution == res:
            #print(idx)
            #print(i.resolution)
            break
    #print(yt.streams[idx])
    yt.streams[idx].download(output_path=dlpath)

    print("Download VIDEO complete.")

    for idx, i in enumerate(yt.streams):
        if i.bitrate == "128kbps":
            #print(idx)
            #print(i.resolution)
            break
    #print(yt.streams[idx])
    yt.streams[idx].download(output_path=dlpath)

    print("Download AUDIO complete.")
except Exception as e:
    print("An error occurred:", str(e))
