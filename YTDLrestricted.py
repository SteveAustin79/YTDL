import os
import ffmpeg
from pytubefix import YouTube, request
from pytubefix.cli import on_progress
import browser_cookie3


# ✅ Function to Load Cookies from cookies.txt
def load_cookies_from_file(filename):
    """Reads cookies from a cookies.txt file and returns them as a dictionary."""
    cookies = {}
    with open(filename, "r") as f:
        for line in f:
            if not line.startswith("#"):
                parts = line.strip().split("\t")
                if len(parts) >= 7:
                    cookies[parts[5]] = parts[6]  # Extract name and value
    return cookies


def find_media_files():
    """Search for the first MP4 and M4A files in the current directory."""
    video_file = None
    audio_file = None

    for file in os.listdir("."):
        if file.endswith(".mp4") and video_file is None:
            video_file = file
        elif file.endswith(".m4a") and audio_file is None:
            audio_file = file

        if video_file and audio_file:
            break  # Stop searching once both files are found

    return video_file, audio_file


def merge_video_audio():
    video_file, audio_file = find_media_files()

    if not video_file or not audio_file:
        print("❌ No MP4 or M4A files found in the current directory.")
        return

    output_file = dlpath + "/" + video_file

    """Merge video and audio into a single MP4 file using FFmpeg."""
    try:
        print(f"🎬 Merging Video: {video_file}")
        print(f"🎵 Merging Audio: {audio_file}")

        # Input video and audio streams
        video = ffmpeg.input(video_file)
        audio = ffmpeg.input(audio_file)

        # Merge video and audio
        output = ffmpeg.output(video, audio, output_file, vcodec="copy", acodec="aac", strict="experimental")

        # Run FFmpeg command
        ffmpeg.run(output, overwrite_output=True)
        print(f"\n✅ Merged file saved as: {output_file}, have a great day!\n")

        # remove video and audio streams
        os.remove(video_file)
        os.remove(audio_file)

    except Exception as e:
        print(f"❌ Error merging files: {e}")

try:
    # Fetch YouTube cookies from browser for user aoth to download restricted videos
    cookies = browser_cookie3.firefox(domain_name="youtube.com")  # Change to firefox() or edge() if needed

    # Convert cookies into a dictionary format
    cookie_dict = load_cookies_from_file("cookies.txt")

    # Manually set cookies in the PyTubeFix request session
    session = request.default_session()
    session.cookies.update(cookie_dict)

    print("\n")
    url = input("Enter the YouTube URL: ")
    yt = YouTube(url, cookies=cookie_dict)

    yt.watch_html = request.get(url)  # Re-fetch the video page with cookies

    # Perform age check (needed for restricted videos)
    yt.age_check()

    print("Title:", yt.title)
    print("Views:", yt.views)

    res = input("Enter desired resolution (eg. 1080p): ")
    dlpath = input("Enter path to download: (eg. d:): ")

    for idx, i in enumerate(yt.streams):
        if i.resolution == res:
            break

    print("Downloading VIDEO...\n")

    yt.streams[idx].download()

    print("Download VIDEO complete. Downloading AUDIO...\n")

    for idx, i in enumerate(yt.streams):
        if i.bitrate == "128kbps":
            break
    yt.streams[idx].download()

    print("Download AUDIO complete. Merging now...")
    merge_video_audio()

except Exception as e:
    print("An error occurred:", str(e))
