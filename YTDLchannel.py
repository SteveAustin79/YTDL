"""
YTDLchannel 0.5

Download all videos from a specific YouTube channel.

Features:
- highest available resolution will be downloaded automatically
- sub-directory structure will be suggested
- already downloaded videos will be skipped

20250301 - v0.5 - added support to exclude videos by video_id
20250228 - v0.4 - added support for age_restricted videos
20250228 - v0.3 - added optional limit for max resolution, channels.txt as suggestions
20250227 - v0.2 - enhanced file support (checks if already downloaded etc)
20250226 - v0.1 - initial version, based on YTDL v0.3

https://github.com/SteveAustin79
"""


import os
import re
import shutil
import subprocess
from operator import truediv
import ffmpeg
import json
import sys
import pytubefix.extract
from pytubefix import YouTube, Channel
from pytubefix.cli import on_progress
from datetime import datetime


version = 0.5


class bcolors:
    HEADER     = "\033[95m"
    OKBLUE     = "\033[96m"
    OKGREEN    = "\033[92m"
    WARNING    = "\033[93m"
    FAIL       = "\033[91m"
    BOLD       = "\033[1m"
    UNDERLINE  = "\033[4m"
    ENDC       = "\033[0m"


def load_config():
    """Load settings from config.json."""
    with open("config.json", "r") as file:
        config = json.load(file)
    return config


def print_configuration():
    print("************************************************")
    print("* CONFIGURATION (change in config.json):")
    print("************************************************")
    print("* Max Video Duration in Minutes:        ", print_colored_text(max_duration, bcolors.OKBLUE))
    if year_subfolders:
        year_subfolders_colored = print_colored_text(year_subfolders, bcolors.OKBLUE)
    else:
        year_subfolders_colored = print_colored_text(year_subfolders, bcolors.FAIL)
    print("* Year Subfolder-Structure:             ", year_subfolders_colored)
    print("************************************************\n")


def print_colored_text(message_text, color):
    return f"{color}{message_text}{bcolors.ENDC}"


def get_free_space(path):
    """Returns the free disk space for the given path formatted in GB or MB."""
    total, used, free = shutil.disk_usage(path)  # Get disk space (in bytes)

    # Convert bytes to GB or MB for readability
    if free >= 1_000_000_000:  # If space is at least 1GB
        formatted_space = f"{free / 1_073_741_824:.1f} GB"
    else:
        formatted_space = f"{free / 1_048_576:.0f} MB"  # Otherwise, use MB

    return formatted_space


def string_to_list(input_string):
    """Transforms a comma-separated string into a list of strings, removing extra spaces."""
    return [item.strip() for item in input_string.split(",")]


def write_textfile_failed_downloads(file, text):
    with open(file, "a", encoding="utf-8") as file:
        file.write("{text}}\n")


def format_header(counter):
    width = 95
    #counter_str = f" \033[96m{counter}\033[0m "  # Add spaces around the number

    counter_splitted = counter.split(" - ")

    counter_str = ("** " + counter_splitted[0] + " *" + print_colored_text(f" {counter_splitted[1]} ", bcolors.OKBLUE)
                   + "| " + counter_splitted[2] + " (" + get_free_space(dlpath) + " free) ")
    total_length = width - 2  # Exclude parentheses ()

    # Center the counter with asterisks
    formatted = f"{counter_str.ljust(total_length, '*')}"

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
    new_text = text.replace(":", "")

    pattern = r"[^a-zA-Z0-9 ]"

    return re.sub(pattern, "", new_text)


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


def read_file_lines(filename):
    """Reads all lines from a file and returns a list of lines."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file.readlines()]  # Remove newlines
        lines.append("Enter CUSTOM channel URL")
        return lines
    except FileNotFoundError:
        print("❌ Error: File not found.")
        return []


def user_selection(lines):
    """Displays the lines as a selection menu and gets user input."""
    if not lines:
        print("No lines available for selection.")
        return None

    print("\nSelect channel:")
    for index, line in enumerate(lines, start=1):
        print(f"{index}. {line}")

    while True:
        try:
            choice = int(input("\nEnter the number of your choice: "))
            if 1 <= choice <= len(lines):
                return lines[choice - 1]  # Return selected line
            else:
                print("⚠️ Invalid selection. Choose a valid number.")
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")


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
    for root, _, files in os.walk(directory):  # os.walk() traverses all subdirectories
        for filename in files:
            if search_string in filename and resolution in filename:
                return os.path.join(root, filename)  # Return full file path of the first match

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


def downloadVideoRestricted(videoid, counterid, video_total_count, channelName):
    yt = YouTube(youtube_base_url + videoid, use_oauth=True, allow_oauth_cache=True, on_progress_callback = on_progress)
    dlpath = output_dir + "/" + channelName

    print("\n\n" + print_colored_text("Downloading restricted video...\n", bcolors.FAIL))

    print(format_header(videoid + " - " + channelName + " - " + str(counterid) + "/" + str(video_total_count)))
    #print("Channel:       ", print_colored_text(channelName, bcolors.OKBLUE))
    print("Title:         ", print_colored_text(yt.title, bcolors.OKBLUE))
    #print("ID:            ", videoid)
    #print("Views:         ", format_view_count(yt.views))
    print("Date:          ", yt.publish_date.strftime("%Y-%m-%d"))
    print("Length:        ", str(int(yt.length / 60)) + "m")

    publishingDate = yt.publish_date.strftime("%Y-%m-%d")
    if year_subfolders == True:
        year = yt.publish_date.strftime("%Y")
    else:
        year = ""
    # Print results
    #print("\nAvailable Resolutions:", print_resolutions(yt))
    res = max(print_resolutions(yt), key=lambda x: int(x.rstrip('p')))
    if limit_resolution_to != "max":
        res = limit_resolution(res, limit_resolution_to)
    print("Resolution:     ", print_colored_text(res, bcolors.WARNING), " (" + limit_resolution_to + ")")

    #res = smart_input("\n" + print_colored_text("Resolution: ", bcolors.WARNING), max_res)
    # dlpath = smart_input("Download Path:  ", output_dir)

    if os.path.exists(
            dlpath + str(year) + "/restricted/" + str(publishingDate) + " - " + res + " - " + clean_string_regex(
                yt.title) + " - " + yt.video_id + ".mp4"):
        print(print_colored_text("\nVideo already downloaded", bcolors.OKGREEN))
    else:
        moreThan1080p = 0

        # here check if /temp/file already exists

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

        if not os.path.exists(dlpath + f"{year}/restricted"):
            os.makedirs(dlpath + f"{year}/restricted")

        rename_files_in_temp_directory()

        if moreThan1080p == 0:
            print("\nMerging...\n")
            merge_video_audio(yt.video_id, publishingDate, res, year, True)
        else:
            print("\nMerging...")
            # move_video_audio()
            convert_m4a_to_opus_and_merge(yt.video_id, publishingDate, res, year, True)


def downloadVideo(videoid, counterid, video_total_count):
    yt = YouTube(youtube_base_url + videoid, on_progress_callback=on_progress)

    #print("\n***" + str(counterid) + "********************************************************************************")
    print(format_header(videoid + " - " + yt.author + " - " + str(counterid) + "/" + str(video_total_count)))
    #print("Channel:        ", yt.author)
    print("Title:          ", print_colored_text(yt.title, bcolors.OKBLUE))
    #print("ID:             ", videoid)
    #print("Views:          ", format_view_count(yt.views))
    print("Date:           ", yt.publish_date.strftime("%Y-%m-%d"))
    print("Length:         ", str(int(yt.length / 60)) + "m")

    if year_subfolders == True:
        year = "/" + str(yt.publish_date.strftime("%Y"))
    else:
        year = ""
    # print_resolutions()
    # res = smart_input("\nResolution: ", resolution)
    #res = max(print_resolutions(), key=lambda x: int(x.rstrip('p')))

    publishingDate = yt.publish_date.strftime("%Y-%m-%d")
    res = max(print_resolutions(yt), key=lambda x: int(x.rstrip('p')))
    if limit_resolution_to != "max":
        res = limit_resolution(res, limit_resolution_to)

    print("Resolution:     ", print_colored_text(res, bcolors.WARNING), " (" + limit_resolution_to + ")")

    #print("Resolution: ", res)
    # check if file was already downloaded
    if os.path.exists(dlpath + year + "/" + str(publishingDate) + " - " + res + " - " + clean_string_regex(yt.title) + " - "+ videoid + ".mp4"):
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

        rename_files_in_temp_directory()

        print("\nMerging...")
        if moreThan1080p == 0:
            merge_video_audio(videoid, str(publishingDate), res, year, False)
        else:
            # move_video_audio()
            convert_m4a_to_opus_and_merge(videoid, str(publishingDate), res, year, False)


def merge_video_audio(videoid, publishdate, video_resolution, year, restricted):
    video_file, audio_file = find_media_files()

    if not video_file or not audio_file:
        print("❌ No MP4 or M4A files found in the current directory.")
        return

    if not os.path.exists(dlpath + f"{str(year)}"):
        os.makedirs(dlpath + f"{str(year)}")

    if restricted:
        restricted_path = "/restricted/"
    else:
        restricted_path = "/"
    output_file = dlpath + str(year) + restricted_path + publishdate + " - " + video_resolution + " - " + clean_string_regex(os.path.splitext(video_file)[0]) + " - " + videoid + ".mp4"

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

def convert_m4a_to_opus_and_merge(videoid, publishdate, video_resolution, year, restricted):
    video_file, audio_file = find_media_files()
    """Convert M4A to Opus format (WebM-compatible)."""
    command = [
        "ffmpeg", "-loglevel", "quiet", "-i", audio_file, "-c:a", "libopus", "audio.opus"
    ]
    subprocess.run(command, check=True)
    #print(f"✅ Converted {audio_file} to audio.opus")
    merge_webm_opus(videoid, publishdate, video_resolution, year, restricted)


def merge_webm_opus(videoid, publishdate, video_resolution, year, restricted):
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
    if restricted:
        path = (dlpath + str(year) + "/restricted/" + publishdate + " - " + video_resolution
                + " - " + clean_string_regex(os.path.splitext(video_file)[0]) + " - "+ videoid + ".mp4")
    else:
        path = (dlpath + str(year) + "/" + publishdate + " - " + video_resolution + " - "
                + clean_string_regex(os.path.splitext(video_file)[0]) + " - "+ videoid + ".mp4")
    convert_webm_to_mp4(output_file, path)


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
        max_duration = config["max_duration_in_minutes"]
        year_subfolders = config["year_subfolders"]

        # Create an empty list
        video_list = []
        video_list_restricted = []

        print("\nYTDLchannel " + str(version))
        print("***************")
        print("YouTube Channel Downloader\nExit App with Ctrl + C")
        print("https://github.com/SteveAustin79/YTDL\n\n")
        deletTempFiles()
        print_configuration()

        lines = read_file_lines("channels.txt")
        if lines:
            YTchannel = user_selection(lines)
        if "Enter CUSTOM channel URL" in YTchannel:
            YTchannel = input("YouTube Channel URL:  ")
        #count_fetch_videos = str(smart_input("Fetch x latest Videos (to download all playable/unrestricted videos use 'all'): ", "all"))
        #skip_x_videos = int(smart_input("Skip x videos: ", "0"))

        c = Channel(YTchannel)

        dlpath = smart_input("\nDownload Path:  ", output_dir + "/" + clean_string_regex(c.channel_name).rstrip())
        limit_resolution_to = smart_input("Max. Resolution:  ", "max")
        ignore_max_duration = smart_input("Ignore max_duration?  Y/n", "y")
        if ignore_max_duration== "y":
            ignore_max_duration_bool = True
        elif ignore_max_duration=="n":
            ignore_max_duration_bool = False
            print(print_colored_text("Ignoring Videos > " + str(max_duration) + " Minutes!", bcolors.FAIL))

        skip_restricted = smart_input("Skip restricted Videos? Y/n ", "n")
        if skip_restricted== "y":
            skip_restricted_bool = True
            print(print_colored_text("Skipping restricted Videos!", bcolors.FAIL))
        elif skip_restricted=="n":
            skip_restricted_bool = False

        #exclude_video_ids_cache = ""
        exclude_video_ids = input("Exclude Video ID's? (comma separated list): ")
        exclude_list = []
        if exclude_video_ids!="":
            exclude_list = string_to_list(exclude_video_ids)

        video_name_filter = str(input("\nEnter filter word(s) (comma separated list): "))
        video_name_filter_list = string_to_list(video_name_filter)

        video_watch_urls = []
        for url in c.video_urls:
            if(url.video_id not in exclude_list):
                video_watch_urls.append(url.watch_url)

        if ignore_max_duration_bool== False:
            print(f'\n\n{len(video_watch_urls)} Videos (-ignored) by: \033[96m{c.channel_name}\033[0m\n')
        else:
            print(f'\n\n{len(video_watch_urls)} Videos by: \033[96m{c.channel_name}\033[0m\n')

        count_total_videos = 0
        count_restricted_videos = 0
        count_ok_videos = 0
        count_this_run = 0
        count_skipped = 0

        #for url in c.video_urls:
        for url in video_watch_urls:
            only_video_id = pytubefix.extract.video_id(url)
            #video_ids.append(only_video_id)
            #print(youtube_base_url + only_video_id)

            if not os.path.exists(dlpath):
                os.makedirs(dlpath)

            if find_file_by_string(dlpath, only_video_id, limit_resolution_to)!=None:
                count_ok_videos += 1
                count_skipped += 1
                print(print_colored_text(f"\rSkipping {count_skipped} Videos", bcolors.FAIL), end="", flush=True)
            else:
                #print(only_video_id)
                do_not_download = 0
                video = YouTube(youtube_base_url + only_video_id, on_progress_callback=on_progress)

                if video_name_filter=="" or any(word in video.title for word in video_name_filter_list):
                    if ignore_max_duration_bool==False:
                        video_duration = int(video.length/60)
                        if video_duration > int(max_duration):
                            do_not_download = 1
                            #count_skipped += 1
                            #count_ok_videos += 1

                    if (video.age_restricted == False and
                            video.vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE' and
                            do_not_download == 0):
                        print("\n")
                        count_ok_videos += 1
                        count_this_run += 1
                        count_skipped = 0
                        video_list.append(video.video_id)
                        #print(str(count_total_videos) + " - " + video.video_id + " - " + video.title)
                        #print_resolutions()
                        downloadVideo(video.video_id, count_ok_videos, len(video_watch_urls))
                    else:
                        if skip_restricted_bool == False:
                            if (video.vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE' and
                                    do_not_download == 0):
                                count_restricted_videos += 1
                                count_ok_videos += 1
                                count_this_run += 1
                                video_list_restricted.append(video.video_id)
                                downloadVideoRestricted(video.video_id, count_ok_videos, len(video_watch_urls),
                                                        clean_string_regex(c.channel_name).rstrip())
                        #print("\033[31m" + str(count_total_videos) + " - " + video.video_id + " - " + video.title + "\n\033[0m")
                        #print_resolutions()

        if count_this_run == 0:
            print("\n\n" + print_colored_text("nothing to do...\n\n", bcolors.OKGREEN))
        else:
            done_string = f"\n\nDONE! Total Videos: {count_ok_videos}, Downloaded in this session: {count_this_run} (restricted: {len(video_list_restricted)} / ignored: {len(video_watch_urls)-count_ok_videos})\n\n"
            print(print_colored_text(done_string, bcolors.OKGREEN))
        #for restricted_video in video_list_restricted:
        #    print(youtube_base_url + restricted_video)
        #print("Already downloaded: " + str(count_already_downloaded))
        #print("Downloaded:         " + str(count_downloading))

    except Exception as e:
        deletTempFiles()
        #if e == "expected string or bytes-like object, got 'YouTube'":
        #downloadVideoRestricted()
        #else:
        print("An error occurred:", str(e))

    except KeyboardInterrupt:
        deletTempFiles()
        print("\n\nGood Bye...\n")
        break