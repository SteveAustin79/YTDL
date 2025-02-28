"""
YTDL 0.4

A command line YouTube video downloader, downloading a specific video resolution file
and a 128kps audio stream, finally merged into a single file. Use of ffmpeg and pytubefix.

20250227 - v0.4 - download path structure based on YTDLchannel v0.1
20250224 - v0.3 - config file support
20250223 - v0.2 - added webm support (>1080p)
20250220 - v0.1 - initial version

https://github.com/SteveAustin79
"""

import os
import re
import shutil
import subprocess
import ffmpeg
import json
from pytubefix import YouTube
from pytubefix.cli import on_progress


version = 0.4


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


def format_header(counter):
    width = 87
    #counter_str = f" \033[96m{counter}\033[0m "  # Add spaces around the number
    counter_str = f"***{counter}"
    total_length = width - 2  # Exclude parentheses ()

    # Center the counter with asterisks
    formatted = f"{counter_str.ljust(total_length, '*')}"

    return formatted


def clean_string_regex(text):
    """
    Removes characters that do NOT match the given pattern.

    :param text: The input string to clean.
    :param pattern: Regular expression pattern for allowed characters.
    :return: The cleaned string.
    """
    pattern = r"[^a-zA-Z0-9 ]"

    return re.sub(pattern, "", text)


def rename_files_in_temp_directory():
    """Removes ':' from filenames in a given directory."""
    directory = os.getcwd()
    if not os.path.exists(directory):
        print("Error: Directory does not exist!")
        return

    for filename in os.listdir(directory):
        if ":" in filename:  # Check if filename contains ':'
            sanitized_name = filename.replace(":", "")
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, sanitized_name)

            os.rename(old_path, new_path)
            #print(f"Renamed: {filename} → {sanitized_name}")


def print_resolutions():
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


def load_config():
    """Load settings from config.json."""
    with open("config.json", "r") as file:
        config = json.load(file)
    return config


def convert_m4a_to_opus_and_merge(videoid, publishdate):
    video_file, audio_file = find_media_files()
    """Convert M4A to Opus format (WebM-compatible)."""
    if quiet_on=="y":
        command = [
            "ffmpeg", "-loglevel", "quiet", "-i", audio_file, "-c:a", "libopus", "audio.opus"
        ]
    elif quiet_on=="n":
        command = ["ffmpeg", "-i", audio_file, "-c:a", "libopus", "audio.opus"]
    subprocess.run(command, check=True)
    print(f"✅ Converted {audio_file} to audio.opus")
    merge_webm_opus(videoid, publishdate)


def merge_webm_opus(videoid, publishdate, video_resolution):
    video_file, audio_file = find_media_files()
    output_file = "tmp/" + video_file
    """Merge WebM video with Opus audio. """
    if quiet_on == "y":
        command = [
            "ffmpeg", "-loglevel", "quiet", "-i", video_file, "-i", "audio.opus",
            "-c:v", "copy", "-c:a", "copy", output_file
        ]
    elif quiet_on == "n":
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
    convert_webm_to_mp4(output_file, dlpath + str(year) + "/" + publishdate + " - " + video_resolution + " - " + clean_string_regex(os.path.splitext(video_file)[0]) + " - "+ videoid + ".mp4")


def convert_webm_to_mp4(input_file, output_file):
    """Convert a WebM file to MP4 (H.264/AAC)."""
    if quiet_on == "y":
        command = [
            "ffmpeg", "-loglevel", "quiet", "-i", input_file,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",  # H.264 video encoding
            "-c:a", "aac", "-b:a", "128k",  # AAC audio encoding
            "-movflags", "+faststart",  # Optimize MP4 for streaming
            output_file
        ]
    elif quiet_on == "n":
        command = [
            "ffmpeg", "-i", input_file,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",  # H.264 video encoding
            "-c:a", "aac", "-b:a", "128k",  # AAC audio encoding
            "-movflags", "+faststart",  # Optimize MP4 for streaming
            output_file
        ]
    subprocess.run(command, check=True)
    os.remove(input_file)
    #print(f"✅ Converted {input_file} to {output_file}\nHave a great day!!!\n")
    #print(f"\n\033[92mVideo downloaded\033[0m")
    print(print_colored_text("Video downloaded", bcolors.OKGREEN))


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


def merge_video_audio(videoid, publishdate, video_resolution):
    video_file, audio_file = find_media_files()

    if not video_file or not audio_file:
        print("❌ No MP4 or M4A files found in the current directory.")
        return

    #output_file = dlpath + "/" + video_file
    output_file = dlpath + str(year) + "/" + publishdate + " - " + video_resolution + " - " + clean_string_regex(
        os.path.splitext(video_file)[0]) + " - " + videoid + ".mp4"

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
        if quiet_on=="y":
            ffmpeg.run(output, overwrite_output=True, quiet=True)
        elif quiet_on=="n":
            ffmpeg.run(output, overwrite_output=True, quiet=False)
        #print(f"\n✅ Merged file saved as: {output_file}.\nHave a great day!!!\n")
        print(print_colored_text("Video downloaded", bcolors.OKGREEN))

        # remove video and audio streams
        os.remove(video_file)
        os.remove(audio_file)

    except Exception as e:
        print(f"❌ Error merging files: {e}")


while True:
    try:
        # Load config
        config = load_config()
        # Access settings
        output_dir = config["output_directory"]
        year_subfolders = config["year_subfolders"]

        print("\n\nYTDL " + str(version))
        print("********")
        print("YouTube Video/Audio Downloader (Exit App with Ctrl + C)")
        print("https://github.com/SteveAustin79/YTDL\n\n")
        print("Year Subfolder-Structure: ", year_subfolders, "\n\n")
        #cleanup directory
        deletTempFiles()
        url = input("YouTube Video URL: ")

        yt = YouTube(url, on_progress_callback = on_progress)
        dlpath = smart_input("\nDownload Path:  ", output_dir + "/" + yt.author)
        quiet_on = smart_input("Quiet output? Y/n: ", "y")

        print("\n" + format_header("*"))
        print("Channel:    ", print_colored_text(yt.author, bcolors.OKBLUE))
        print("Title:      ", print_colored_text(yt.title, bcolors.OKBLUE))
        print("Views:      ", format_view_count(yt.views))
        print("Date:       ", yt.publish_date.strftime("%Y-%m-%d"))
        print("Length:     ", str(int(yt.length/60)) + "m")

        publishingDate = yt.publish_date.strftime("%Y-%m-%d")
        if year_subfolders == True:
            year = yt.publish_date.strftime("%Y")
        else:
            year = ""
        # Print results
        print("\nAvailable Resolutions:", print_resolutions())
        max_res = max(print_resolutions(), key=lambda x: int(x.rstrip('p')))

        res = smart_input("\n" + print_colored_text("Resolution: ", bcolors.WARNING), max_res)
        #dlpath = smart_input("Download Path:  ", output_dir)

        if os.path.exists(
                dlpath + str(year) + "/" + str(publishingDate) + " - " + res + " - " + clean_string_regex(yt.title) + " - " + yt.video_id + ".mp4"):
            print(print_colored_text("\nVideo already downloaded", bcolors.OKGREEN))
        else:
            moreThan1080p = 0

            if res == "2160p" or res == "1440p":
                #print("\nATTENTION: >1080p is stored as webm and cannot be merged by ffmpeg! Moving source files to download path instead!\n")
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

            if not os.path.exists(dlpath + f"{year}"):
                os.makedirs(dlpath + f"{year}")

            rename_files_in_temp_directory()

            if moreThan1080p==0:
                print("\nMerging...\n")
                merge_video_audio(yt.video_id, publishingDate, res)
            else:
                print("\nMoving temp files...")
                #move_video_audio()
                convert_m4a_to_opus_and_merge(yt.video_id, publishingDate, res)


    except Exception as e:
        deletTempFiles()
        print("An error occurred:", str(e))

    except KeyboardInterrupt:
        deletTempFiles()
        print("\n\nGood Bye...\n")
        break