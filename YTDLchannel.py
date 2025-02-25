import os
import re
import shutil
import subprocess
import ffmpeg
import json
from pytubefix import Channel, YouTube
from pytubefix.cli import on_progress

version = 0.1


def load_config():
    """Load settings from config.json."""
    with open("config.json", "r") as file:
        config = json.load(file)
    return config

def convert_m4a_to_opus_and_merge():
    video_file, audio_file = find_media_files()
    """Convert M4A to Opus format (WebM-compatible)."""
    command = [
        "ffmpeg", "-i", audio_file, "-c:a", "libopus", "audio.opus"
    ]
    subprocess.run(command, check=True)
    print(f"✅ Converted {audio_file} to audio.opus")
    merge_webm_opus()

def merge_webm_opus():
    video_file, audio_file = find_media_files()
    output_file = "tmp/" + video_file
    """Merge WebM video with Opus audio."""
    command = [
        "ffmpeg", "-i", video_file, "-i", "audio.opus",
        "-c:v", "copy", "-c:a", "copy", output_file
    ]
    subprocess.run(command, check=True)
    # remove video and audio streams
    os.remove(video_file)
    os.remove(audio_file)
    os.remove("audio.opus")
    print(f"✅ Merged WebM video with Opus audio into {output_file}")
    convert_webm_to_mp4(output_file, dlpath + "/" + video_file + ".mp4")

def convert_webm_to_mp4(input_file, output_file):
    """Convert a WebM file to MP4 (H.264/AAC)."""
    command = [
        "ffmpeg", "-i", input_file,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",  # H.264 video encoding
        "-c:a", "aac", "-b:a", "128k",  # AAC audio encoding
        "-movflags", "+faststart",  # Optimize MP4 for streaming
        output_file
    ]
    subprocess.run(command, check=True)
    os.remove(input_file)
    print(f"✅ Converted {input_file} to {output_file}\nHave a great day!!!\n")

def deletTempFiles():
    # remove video and audio streams
    video_file, audio_file = find_media_files()
    # Check if files exist before deleting
    if video_file and os.path.exists(video_file):
        os.remove(video_file)

    if audio_file and os.path.exists(audio_file):
        os.remove(audio_file)

def smart_input(prompt, default_value):
    user_input = input(f"{prompt} [{default_value}]: ").strip()
    return user_input if user_input else default_value

def find_media_files():
    """Search for the first MP4 and M4A files in the current directory."""
    video_file = None
    audio_file = None

    # if 2160 selected --> webm file, not mp4!!!

    for file in os.listdir("."):
        #if file.endswith(".mp4") and video_file is None:
        if file.endswith((".mp4", ".webm")) and video_file is None:
            video_file = file
        elif file.endswith(".m4a") and audio_file is None:
            audio_file = file

        if video_file and audio_file:
            break  # Stop searching once both files are found

    return video_file, audio_file

def move_video_audio():
    video_file, audio_file = find_media_files()
    destinationVideo = dlpath + "/" + video_file  # Destination path
    destinationAudio = dlpath + "/" + audio_file  # Destination path

    shutil.move(video_file, destinationVideo)
    shutil.move(audio_file, destinationAudio)

    print(f"✅ Moved files to download path!")

def merge_video_audio():
    video_file, audio_file = find_media_files()

    if not video_file or not audio_file:
        print("❌ No MP4 or M4A files found in the current directory.")
        return

    if not os.path.exists(dlpath):
        os.makedirs(dlpath)

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
        print(f"\n✅ Merged file saved as: {output_file}.\n")

        # remove video and audio streams
        os.remove(video_file)
        os.remove(audio_file)

    except Exception as e:
        print(f"❌ Error merging files: {e}")

def print_resolutions():
    streams = yt.streams.filter(file_extension='mp4')  # StreamQuery object
    # Convert StreamQuery to a formatted string
    stream_string = "\n".join([str(stream) for stream in streams])
    # Extract resolutions using regex
    resolutions = re.findall(r'res="(\d+p)"', stream_string)
    # Remove duplicates and sort in descending order
    unique_resolutions = sorted(set(resolutions), key=lambda x: int(x[:-1]), reverse=True)

    # Print results
    print("Available Resolutions:", unique_resolutions, "\n")

while True:
    try:
        # CHECK VIDEOS
        ##############
        # Load config
        config = load_config()
        # Access settings
        output_dir = config["output_directory"]
        resolution = config["default_resolution"]

        # Create an empty list
        video_list = []
        video_list_restricted = []

        print("\nYTDLchannel " + str(version))
        print("***************")
        print("YouTube Channel Downloader (Exit App with Ctrl + C)\n")

        YTchannel = input("YouTube Channel URL: ")
        count_fetch_videos = str(input("Fetch x latest Videos (for all unrestricted Videos use: All): "))

        c = Channel(YTchannel)
        print(f'\nListing videos by: {c.channel_name}\n')

        count_total_videos = 0
        count_restricted_videos = 0
        count_ok_videos = 0

        for video in c.videos:
            count_total_videos += 1
            yt = YouTube("https://www.youtube.com/watch?v=" + video.video_id, on_progress_callback=on_progress)

            print(video.vid_info)

            if video.age_restricted == False:
                count_ok_videos += 1
                video_list.append(video.video_id)
                print(str(count_total_videos) + " - " + video.video_id + " - " + video.title)
                print_resolutions()
            else:
                count_restricted_videos += 1
                video_list_restricted.append(video.video_id)
                print("\033[31m" + str(count_total_videos) + " - " + video.video_id + " - " + video.title + "\n\033[0m")
                #print_resolutions()

            if count_fetch_videos != "All":
                if count_total_videos == count_fetch_videos:
                    break

        print("Total Videos: " + str(count_total_videos) + ", OK Videos: " + str(count_ok_videos)
              + ", Restricted Videos: " + str(count_restricted_videos) + "\n")


        # DOWNLOAD VIDEOS
        #################
        dlpath = smart_input("Download Path:  ", output_dir)
        res = smart_input("Resolution: ", resolution)

        for video in video_list:
            yt = YouTube("https://www.youtube.com/watch?v=" + video, on_progress_callback=on_progress)

            print("\n******************************************************************************")
            print("Channel:", yt.author)
            print("Title:", yt.title)
            print("Views:", str(int(yt.views / 1000)) + "K")
            print("Length:", str(int(yt.length / 60)) + "m")

            #print_resolutions()
            #res = smart_input("\nResolution: ", resolution)

            moreThan1080p = 0

            if res == "2160p" or res == "1440p":
                # print("\nATTENTION: >1080p is stored as webm and cannot be merged by ffmpeg! Moving source files to download path instead!\n")
                moreThan1080p = 1

            print("\nDownloading VIDEO...")

            for idx, i in enumerate(yt.streams):
                if i.resolution == res:
                    break
            yt.streams[idx].download()

            print("\nDownload VIDEO complete.\n\nDownloading AUDIO...")

            for idx, i in enumerate(yt.streams):
                if i.bitrate == "128kbps":
                    break
            yt.streams[idx].download()

            print("\nDownload AUDIO complete.")

            if moreThan1080p == 0:
                print("\nMerging...")
                merge_video_audio()
            else:
                print("\nMoving temp files...")
                # move_video_audio()
                convert_m4a_to_opus_and_merge()

        print("Have a great day!!!\n")


    except Exception as e:
        deletTempFiles()
        print("An error occurred:", str(e))

    except KeyboardInterrupt:
        deletTempFiles()
        print("\n\nGood Bye...\n")
        break