from pytubefix import YouTube
from pytubefix.cli import on_progress

try:
    # Ask the user to input the YouTube URL
    url = input("Enter the YouTube URL: ")

    yt = YouTube(url, on_progress_callback = on_progres)

    print("\n")
    print("Title:", yt.title)
    print("Views:", yt.views)
    print("\n")
    #print(yt.streams.filter(file_extension='mp4'))
    print(yt.streams)
    print("\n")

    videoVersion = input ("Enter itag: ")

    dlpath = input("Enter path to download: ")

    # Get the highest resolution stream
    yd = yt.streams.get_by_itag(videoVersion)

    # Download the video to the current directory
    yd.download(output_path=dlpath)

    print("Download complete.")
except Exception as e:
    print("An error occurred:", str(e))
