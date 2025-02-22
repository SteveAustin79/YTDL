import os
import re
import ffmpeg
from pytubefix import YouTube
from pytubefix.cli import on_progress


def smart_input(prompt, default_value):
    user_input = input(f"{prompt} [{default_value}]: ").strip()
    return user_input if user_input else default_value


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
    print("\n")
    url = input("Enter the YouTube URL: ")

    yt = YouTube(url, on_progress_callback = on_progress)

    print("\nChannel:", yt.author)
    print("Title:", yt.title)
    print("Views:", yt.views)
    print("Length:", str(int(yt.length/60)) + "m")

    streams = yt.streams.filter(file_extension='mp4')  # StreamQuery object

    # Convert StreamQuery to a formatted string
    stream_string = "\n".join([str(stream) for stream in streams])

    # Extract resolutions using regex
    resolutions = re.findall(r'res="(\d+p)"', stream_string)

    # Remove duplicates and sort in descending order
    unique_resolutions = sorted(set(resolutions), key=lambda x: int(x[:-1]), reverse=True)

    # Print results
    print("\nAvailable Resolutions:", unique_resolutions)

    res = smart_input("\nEnter desired resolution (eg. 1080p): ", "1080p")
    dlpath = smart_input("Enter download path: (eg. d:): ", "/mnt/G")

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
    # remove video and audio streams
    video_file, audio_file = find_media_files()
    os.remove(video_file)
    os.remove(audio_file)
