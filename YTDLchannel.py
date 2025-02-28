"""
YTDLchannel 0.3

Download all videos from a specific YouTube channel.

Features:
- highest available resolution will be downloaded automatically
- sub-directory structure will be suggested
- already downloaded videos will be skipped

20250228 - v0.3 - added limit for max resolution
20250227 - v0.2 - enhanced file support (checks if already downloaded etc)
20250226 - v0.1 - initial version, based on YTDL v0.3

https://github.com/SteveAustin79
"""


import os
import re
import shutil
import subprocess
import ffmpeg
import json
import sys
import pytubefix.extract
from pytubefix import Channel, YouTube
from pytubefix.cli import on_progress
from datetime import datetime


version = 0.3


class bcolors:
    HEADER     = "\033[95m"
    OKBLUE     = "\033[96m"
    OKGREEN    = "\033[92m"
    WARNING    = "\033[93m"
    FAIL       = "\033[91m"
    BOLD       = "\033[1m"
    UNDERLINE  = "\033[4m"
    ENDC       = "\033[0m"


def print_colored_text(message_text, color):
    return f'{color}{message_text}{bcolors.ENDC}'


def write_textfile_failed_downloads(file, text):
    with open(file, "a", encoding="utf-8") as file:
        file.write("{text}}\n")


def format_header(counter):
    width = 95
    #counter_str = f" \033[96m{counter}\033[0m "  # Add spaces around the number
    counter_str = print_colored_text(f" {counter} ", bcolors.OKBLUE)
    total_length = width - 2  # Exclude parentheses ()

    # Center the counter with asterisks
    formatted = f"{counter_str.center(total_length, '*')}"

    return formatted


def format_view_count(number):
    """Formats a number into a human-readable view count."""
    if number >= 1_000_000_000:  # Billions
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:  # Millions
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:  # Thousands
        return f"{number / 1_000:.0f}K"
    else:
        return str(number)


def clean_string_regex(text):
    """
    Removes characters that do NOT match the given pattern.

    :param text: The input string to clean.
    :param pattern: Regular expression pattern for allowed characters.
    :return: The cleaned string.
    """
    text = text.replace(":", "")

    pattern = r"[^a-zA-Z0-9 ]"

    return re.sub(pattern, "", text)


def load_config():
    """Load settings from config.json."""
    with open("config.json", "r") as file:
        config = json.load(file)
    return config


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


def print_resolutions(yt):
    #yt = YouTube(youtube_base_url + video.video_id, on_progress_callback=on_progress)
    streams = yt.streams.filter(file_extension='mp4')  # StreamQuery object
    # Convert StreamQuery to a formatted string
    stream_string = "\n".join([str(stream) for stream in streams])
    # Extract resolutions using regex
    resolutions = re.findall(r'res="(\d+p)"', stream_string)
    # Remove duplicates and sort in descending order
    unique_resolutions = sorted(set(resolutions), key=lambda x: int(x[:-1]), reverse=True)

    # Print results
    #print("Available Resolutions:", unique_resolutions, "\n")
    return unique_resolutions


def find_file_by_string(directory, search_string, resolution):
    """Searches a directory for a file containing a specific string in its filename.

    Returns the filename if found, otherwise returns None.
    """
    if resolution=="max":
        resolution = ""

    if not os.path.exists(directory):
        #print("Error: Directory does not exist!")
        return None

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Ensure it's a file (not a folder)
        if os.path.isfile(file_path) and search_string in filename and resolution in filename:
            return filename  # Return the first match

    return None  # Return None if no file is found


def limit_resolution(resolution, limit):
    num_resolution = int(''.join(filter(str.isdigit, resolution)))  # Extract number from first resolution
    if limit!="max":
        num_limit = int(''.join(filter(str.isdigit, limit)))  # Extract number from second resolution
    if str(limit)=="max" or num_resolution < num_limit:
        max_resolution = resolution
    else:
        max_resolution = limit

    return max_resolution


def downloadVideo(videoid, counterid):
    yt = YouTube(youtube_base_url + videoid, on_progress_callback=on_progress)

    #print("\n***" + str(counterid) + "********************************************************************************")
    print(format_header(yt.author + " - " + str(counterid)))
    #print("Channel:    ", yt.author)
    print("Title:      ", print_colored_text(yt.title, bcolors.OKBLUE))
    print("Views:      ", format_view_count(yt.views))
    print("Date:       ", yt.publish_date.strftime("%Y-%m-%d"))
    print("Length:     ", str(int(yt.length / 60)) + "m")

    # print_resolutions()
    # res = smart_input("\nResolution: ", resolution)
    #res = max(print_resolutions(), key=lambda x: int(x.rstrip('p')))

    publishingDate = yt.publish_date.strftime("%Y-%m-%d")
    res = max(print_resolutions(yt), key=lambda x: int(x.rstrip('p')))
    if limit_resolution_to != "max":
        res = limit_resolution(res, limit_resolution_to)

    print("Resolution: ", print_colored_text(res, bcolors.WARNING), " (" + limit_resolution_to + ")")

    #print("Resolution: ", res)
    # check if file was already downloaded
    if os.path.exists(dlpath + "/" + str(publishingDate) + " - " + res + " - " + clean_string_regex(yt.title) + " - "+ videoid + ".mp4"):
        print(print_colored_text("\nVideo already downloaded\n", bcolors.OKGREEN))
        #count_already_downloaded += count_already_downloaded
    else:
        #count_downloading += count_downloading

        moreThan1080p = 0

        if res == "2160p" or res == "1440p":
            # print("\nATTENTION: >1080p is stored as webm and cannot be merged by ffmpeg! Moving source files to download path instead!\n")
            moreThan1080p = 1

        print("\nDownloading VIDEO...")

        for idx, i in enumerate(yt.streams):
            if i.resolution == res:
                break
        yt.streams[idx].download()

        print("\nDownloading AUDIO...")

        for idx, i in enumerate(yt.streams):
            if i.bitrate == "128kbps":
                break
        yt.streams[idx].download()

        print("\nMerging...")
        if moreThan1080p == 0:
            merge_video_audio(videoid, str(publishingDate), res)
        else:
            # move_video_audio()
            convert_m4a_to_opus_and_merge(videoid, str(publishingDate), res)


def merge_video_audio(videoid, publishdate, video_resolution):
    video_file, audio_file = find_media_files()

    if not video_file or not audio_file:
        print("❌ No MP4 or M4A files found in the current directory.")
        return

    if not os.path.exists(dlpath):
        os.makedirs(dlpath)

    output_file = dlpath + "/" + publishdate + " - " + video_resolution + " - " + clean_string_regex(os.path.splitext(video_file)[0]) + " - " + videoid + ".mp4"

    """Merge video and audio into a single MP4 file using FFmpeg."""
    try:
        #print(f"🎬 Merging Video: {video_file}")
        #print(f"🎵 Merging Audio: {audio_file}")

        # Input video and audio streams
        video = ffmpeg.input(video_file)
        audio = ffmpeg.input(audio_file)

        # Merge video and audio
        output = ffmpeg.output(video, audio, output_file, vcodec="copy", acodec="aac", strict="experimental")

        # Run FFmpeg command
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        #print(f"\n✅ \033[92mMerged file saved as: {output_file}.\033[0m")
        print(print_colored_text("\nVideo downloaded", bcolors.OKGREEN))

        # remove video and audio streams
        deletTempFiles()

    except Exception as e:
        print(f"❌ Error merging files: {e}")
        write_textfile_failed_downloads("errors.txt", output_file)
        sys.exit(1)

def convert_m4a_to_opus_and_merge(videoid, publishdate, video_resolution):
    video_file, audio_file = find_media_files()
    """Convert M4A to Opus format (WebM-compatible)."""
    command = [
        "ffmpeg", "-loglevel", "quiet", "-i", audio_file, "-c:a", "libopus", "audio.opus"
    ]
    subprocess.run(command, check=True)
    #print(f"✅ Converted {audio_file} to audio.opus")
    merge_webm_opus(videoid, publishdate, video_resolution)


def merge_webm_opus(videoid, publishdate, video_resolution):
    video_file, audio_file = find_media_files()
    output_file = "tmp/" + video_file
    """Merge WebM video with Opus audio."""
    command = [
        "ffmpeg", "-loglevel", "quiet", "-i", video_file, "-i", "audio.opus",
        "-c:v", "copy", "-c:a", "copy", output_file
    ]
    subprocess.run(command, check=True)
    # remove video and audio streams
    deletTempFiles()
    os.remove("audio.opus")
    print(f"Converting to MP4... (this may take a while)")
    convert_webm_to_mp4(output_file, dlpath + "/" + publishdate + " - " + video_resolution + " - " + clean_string_regex(os.path.splitext(video_file)[0]) + " - "+ videoid + ".mp4")


def convert_webm_to_mp4(input_file, output_file):
    """Convert a WebM file to MP4 (H.264/AAC)."""
    command = [
        "ffmpeg", "-loglevel", "quiet", "-i", input_file,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",  # H.264 video encoding
        "-c:a", "aac", "-b:a", "128k",  # AAC audio encoding
        "-movflags", "+faststart",  # Optimize MP4 for streaming
        output_file
    ]
    subprocess.run(command, check=True)
    os.remove(input_file)
    print(print_colored_text("\nVideo downloaded", bcolors.OKGREEN))


while True:
    try:
        # CHECK VIDEOS
        ##############
        # Load config
        config = load_config()
        # Access settings
        output_dir = config["output_directory"]
        youtube_base_url = config["youtube_base_url"]

        # Create an empty list
        video_list = []
        video_list_restricted = []

        print("\nYTDLchannel " + str(version))
        print("***************")
        print("YouTube Channel Downloader\nExit App with Ctrl + C")
        print("https://github.com/SteveAustin79/YTDL\n\n")

        YTchannel = input("YouTube Channel URL:  ")
        #count_fetch_videos = str(smart_input("Fetch x latest Videos (to download all playable/unrestricted videos use 'all'): ", "all"))
        #skip_x_videos = int(smart_input("Skip x videos: ", "0"))

        c = Channel(YTchannel)

        dlpath = smart_input("Download Path:  ", output_dir + "/YTDLchannel/" + c.channel_name)
        limit_resolution_to = smart_input("Max. Resolution:  ", "max")
        print(f'\n\nDownloading videos by: \033[96m{c.channel_name}\033[0m\n')

        count_total_videos = 0
        count_restricted_videos = 0
        count_ok_videos = 0
        count_this_run = 0
        count_skipped = 0

        #video_ids = []

        for url in c.video_urls:
            only_video_id = pytubefix.extract.video_id(url.watch_url)
            #video_ids.append(only_video_id)
            #print(youtube_base_url + only_video_id)

            if find_file_by_string(dlpath, only_video_id, limit_resolution_to)!=None:
                count_ok_videos += 1
                count_skipped += 1
                print(f"\rSkipping {count_skipped} Videos (Already downloaded)", end="", flush=True)
            else:
                #print(only_video_id)

                video = YouTube(youtube_base_url + only_video_id, on_progress_callback=on_progress)
                if (video.age_restricted == False and
                    video.vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE'):
                    print("\n")
                    count_ok_videos += 1
                    count_this_run += 1
                    count_skipped = 0
                    video_list.append(video.video_id)
                    #print(str(count_total_videos) + " - " + video.video_id + " - " + video.title)
                    #print_resolutions()
                    downloadVideo(video.video_id, count_ok_videos)
                else:
                    count_restricted_videos += 1
                    video_list_restricted.append(video.video_id)
                    #print("\033[31m" + str(count_total_videos) + " - " + video.video_id + " - " + video.title + "\n\033[0m")
                    #print_resolutions()

        # for video in c.videos:
        #     count_total_videos += 1
        #     #yt = YouTube(youtube_base_url + video.video_id, on_progress_callback=on_progress)
        #
        #     if (video.age_restricted == False and
        #             video.vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE'):
        #         count_ok_videos += 1
        #         video_list.append(video.video_id)
        #         #print(str(count_total_videos) + " - " + video.video_id + " - " + video.title)
        #         #print_resolutions()
        #         downloadVideo(video.video_id, count_ok_videos)
        #     else:
        #         count_restricted_videos += 1
        #         video_list_restricted.append(video.video_id)
        #         #print("\033[31m" + str(count_total_videos) + " - " + video.video_id + " - " + video.title + "\n\033[0m")
        #         #print_resolutions()
        #
        #     if count_fetch_videos != "all":
        #         if count_total_videos == count_fetch_videos:
        #             break

        print(f"\n\nDownloads finished. Total Videos: {count_ok_videos}, Downloaded in this session: {count_this_run}\n\n")
        #print("Already downloaded: " + str(count_already_downloaded))
        #print("Downloaded:         " + str(count_downloading))

    except Exception as e:
        deletTempFiles()
        print("An error occurred:", str(e))

    except KeyboardInterrupt:
        deletTempFiles()
        print("\n\nGood Bye...\n")
        break