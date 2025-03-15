import os
import re
import shutil
import subprocess
import json
import sys
import pytubefix.extract
from pytubefix import YouTube, Channel
from pytubefix.cli import on_progress


version = "1.2 (20250315)"
header_width_global = 94

class BCOLORS:
    CYAN       = "\033[96m"
    MAGENTA    = "\033[95m"
    BLUE       = "\033[94m"
    YELLOW     = "\033[93m"
    GREEN      = "\033[92m"
    RED        = "\033[91m"
    BLACK      = "\033[90m"
    ORANGE     = "\033[33m"
    UNDERLINE  = "\033[4m"
    BOLD       = "\033[1m"
    MOVES1UP   = "\033[F"
    CLRLINE    = "\033[K"
    ENDC       = "\033[0m"

REQUIRED_APP_CONFIG = {
    "output_directory": "",
    "youtube_base_url": "",
    "min_duration_in_minutes": "",
    "max_duration_in_minutes": "",
    "video_listing": "",
    "show_latest_video_date": False,
    "default_audioMP3": False
}

REQUIRED_VIDEO_CHANNEL_CONFIG = {
    "c_max_resolution": "",
    "c_ignore_min_duration": "",
    "c_ignore_max_duration": "",
    "c_only_restricted": "",
    "c_skip_restricted": "",
    "c_minimum_views": "",
    "c_year_subfolders": "",
    "c_exclude_video_ids": "",
    "c_include_video_ids": "",
    "c_filter_words": ""
}


def cc_load_config(file_path: str):
    """Loads the JSON config file or creates an empty dictionary if the file doesn't exist."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)  # Load existing config
            except json.JSONDecodeError:
                print("❌ Error: Invalid JSON format. Resetting to default config.")
                return {}  # Return an empty config if JSON is corrupted
    return {}  # Return an empty config if file doesn't exist

def cc_save_config(cc_file_path: str, cc_config: str) -> None:
    """Saves the updated config dictionary back to the JSON file."""
    with open(cc_file_path, "w", encoding="utf-8") as cc_file:
        json.dump(cc_config, cc_file, indent=4, ensure_ascii=False)
    #print(f"✅ Updated config saved to {cc_file_path}")

def cc_check_and_update_channel_config(cc_file_path: str, cc_required_config: dict) -> None:
    """Ensures all required keys exist in the config file, adding missing ones."""
    cc_config = cc_load_config(cc_file_path)  # Load existing or empty config

    # Check for missing keys and add them
    missing_keys = []
    for key, default_value in cc_required_config.items():
        if key not in cc_config:
            cc_config[key] = default_value
            missing_keys.append(key)

    if missing_keys:
        #print(f"⚠️ Missing keys added: {', '.join(missing_keys)}")
        cc_save_config(cc_file_path, cc_config)  # Save only if changes were made


def smart_input(prompt: str, default_value: str):
    user_input = input(f"{prompt} [{default_value}]: ").strip()
    return user_input if user_input else default_value


def clear_screen() -> None:
    """Clears the console screen on Windows and Linux/macOS."""
    os.system('cls' if os.name == 'nt' else 'clear')


def load_config(c_file: str):
    """Load settings from config.json."""
    with open(c_file, "r") as file:
        l_config = json.load(file)
    return l_config


def print_asteriks_line() -> None:
    length = header_width_global
    print("*" * length)


def print_colored_text(message_text: str, color: str) -> str:
    return f"{color}{message_text}{BCOLORS.ENDC}"


def extract_number(res: str):
    return int(''.join(filter(str.isdigit, res)))  # Extracts only numbers and converts to int


def clean_youtube_urls(to_clean_video_list: list) -> list[str]:
    prefix = youtube_base_url
    return [to_clean_video.replace(prefix, "") for to_clean_video in to_clean_video_list]


def clean_string_regex(text: str) -> str:
    new_text = text.replace(":", "")
    pattern = r"[^a-zA-Z0-9 ]"
    return re.sub(pattern, "", new_text)


def string_to_list(input_string: str) -> list[str]:
    """Transforms a comma-separated string into a list of strings, removing extra spaces."""
    return [item.strip() for item in input_string.split(",")]


def print_configuration() -> None:
    print("Configuration (" + os.path.abspath("config.json") + "):")
    print_asteriks_line()
    print(print_colored_text("Output directory:                   ", BCOLORS.BLACK),
          print_colored_text(output_dir, BCOLORS.CYAN))
    print(print_colored_text("Minimum Video duration in Minutes:  ", BCOLORS.BLACK),
          print_colored_text(min_duration, BCOLORS.CYAN))
    print(print_colored_text("Maximum Video duration in Minutes:  ", BCOLORS.BLACK),
          print_colored_text(max_duration, BCOLORS.CYAN))
    if video_listing:
        video_listings_colored = print_colored_text(video_listing, BCOLORS.GREEN)
    else:
        video_listings_colored = print_colored_text(video_listing, BCOLORS.RED)
    print(print_colored_text("Video listing:                      ", BCOLORS.BLACK),
          video_listings_colored)
    if show_latest_video_date:
        show_latest_video_date_colored = print_colored_text(show_latest_video_date, BCOLORS.GREEN)
    else:
        show_latest_video_date_colored = print_colored_text(show_latest_video_date, BCOLORS.RED)
    print(print_colored_text("Show latest Video date:             ", BCOLORS.BLACK),
          show_latest_video_date_colored)
    if default_audio_mp3:
        default_audio_mp3_colored = print_colored_text(default_audio_mp3, BCOLORS.GREEN)
    else:
        default_audio_mp3_colored = print_colored_text(default_audio_mp3, BCOLORS.RED)
    print(print_colored_text("Default audio/MP3:                  ", BCOLORS.BLACK),
          default_audio_mp3_colored)
    print_asteriks_line()
    print("")


def format_header(counter: str, width: int) -> str:
    counter_splitted = counter.split(" - ")
    counter_str = ("* " + counter_splitted[0] + " *" + print_colored_text(f" {counter_splitted[1]} ", BCOLORS.CYAN)
                   + "| " + counter_splitted[2] + " (" + get_free_space(output_dir) + " free) ")
    total_length = width - 2  # Exclude parentheses ()

    # Center the counter with asterisks
    formatted = f"{counter_str.ljust(total_length, '*')}"

    return formatted


def print_video_infos(yt: YouTube, res: str, video_views: int) -> None:
    print(print_colored_text("Title:         ", BCOLORS.BLACK),
          print_colored_text(print_colored_text(yt.title, BCOLORS.CYAN), BCOLORS.BOLD))

    views_title = print_colored_text("Views:         ", BCOLORS.BLACK)
    if min_video_views_bool:
        print(views_title, format_view_count(video_views), " (> " + format_view_count(min_video_views) + ")")
    else:
        print(views_title, format_view_count(video_views))

    print(print_colored_text("Date:          ", BCOLORS.BLACK), yt.publish_date.strftime("%Y-%m-%d"))

    length_title = print_colored_text("Length:         ", BCOLORS.BLACK)
    length_title_value = length_title + format_time(yt.length)
    if ignore_max_duration_bool and ignore_min_duration_bool:
        print(length_title_value)
    elif ignore_max_duration_bool:
        print(length_title_value, print_colored_text("  (" + min_duration + "m <", BCOLORS.BLACK))
    elif ignore_min_duration_bool:
        print(length_title_value, print_colored_text("  (< " + max_duration + "m", BCOLORS.BLACK))
    else:
        print(length_title_value, print_colored_text("  (" + min_duration + "m < " + max_duration + "m)", BCOLORS.BLACK))

    if not audio_or_video_bool:
        print(print_colored_text("Resolution:    ", BCOLORS.BLACK),
              print_colored_text(res, BCOLORS.YELLOW),
              print_colored_text("  (" + limit_resolution_to + ")", BCOLORS.BLACK))
        print("               ", print_colored_text(str(print_resolutions(yt)), BCOLORS.BLACK))


def format_time(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}m{seconds}s"


def get_free_space(path: str) -> str:
    """Returns the free disk space for the given path formatted in GB or MB."""
    total, used, free = shutil.disk_usage(path)  # Get disk space (in bytes)

    # Convert bytes to GB or MB for readability
    if free >= 1_000_000_000:  # If space is at least 1GB
        formatted_space = f"{free / 1_073_741_824:.1f} GB"
    else:
        formatted_space = f"{free / 1_048_576:.0f} MB"  # Otherwise, use MB

    return formatted_space


def format_view_count(number: int) -> str:
    """Formats a number into a human-readable view count."""
    if number >= 1_000_000_000:  # Billions
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:  # Millions
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:  # Thousands
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)


def rename_files_in_temp_directory() -> None:
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


def read_channel_txt_lines(filename: str) -> list[str]:
    """Reads all lines from a file and returns a list of lines."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            rc_lines = [line.strip() for line in file.readlines()]  # Remove newlines
        rc_lines.append("--- Enter YouTube Channel or Video URL ---")
        return rc_lines
    except FileNotFoundError:
        print("❌ Error: File not found.")
        return []


def user_selection(u_lines, u_show_latest_video_date: bool):
    """Displays the lines as a selection menu and gets user input."""
    if not u_lines:
        print("No lines available for selection.")
        return None

    latest_date_formated = ""

    temp_disable = "y"
    if show_latest_video_date:
        temp_disable = smart_input("Skip latest Video date for this run?  Y/n", "n")
        # 7 config line, 3 header/footer, 3 leerzeilen = 13
        for _ in range(13):
            sys.stdout.write(BCOLORS.MOVES1UP)  # Move cursor up
            sys.stdout.write(BCOLORS.CLRLINE)  # Clear the line
        print("")
        print_asteriks_line()
        print()

    if temp_disable == "y":
        u_show_latest_video_date = False

    print("Select channel:")
    for u_index, line in enumerate(u_lines, start=1):
        if u_show_latest_video_date:
            if not line == u_lines[(len(u_lines) - 1)]:
                spaces = 53
                ytchannel = Channel(line)
                latest_video = list(ytchannel.videos)
                for i in range(len(latest_video)):
                    if (latest_video[i].vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE' and
                            latest_video[i].vid_info.get('playabilityStatus', {}).get('status') != 'LIVE_STREAM_OFFLINE'):
                        latest_date = latest_video[i].publish_date.strftime("%Y-%m-%d")
                        got_it = find_file_by_string(
                            output_dir + "/" + clean_string_regex(ytchannel.channel_name).rstrip(), latest_date, "", False)
                        if got_it:
                            latest_date = print_colored_text(latest_date, BCOLORS.GREEN)
                        else:
                            latest_date = print_colored_text(latest_date, BCOLORS.RED)
                        latest_date_formated = (" " * (spaces-len(str(u_index))-len(line)) + "Last: "
                                                + latest_date + " | " + latest_video[i].video_id)
                        break

        print(f"{u_index}. {line}{latest_date_formated}")
        latest_date_formated = ""

    while True:
        try:
            choice = int(input("\nEnter the number of your choice: "))
            if 1 <= choice <= len(u_lines):
                return u_lines[choice - 1]  # Return selected line
            else:
                print("⚠️ Invalid selection. Choose a valid number.")
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")


def delete_temp_files() -> None:
    # remove video and audio streams
    video_file, audio_file = find_media_files(".")
    # Check if files exist before deleting
    if video_file and os.path.exists(video_file):
        os.remove(video_file)

    if audio_file and os.path.exists(audio_file):
        os.remove(audio_file)


def find_media_files(fmf_path: str) -> tuple[str | None, str | None]:
    """Search for the first MP4 and M4A files in the current directory."""
    video_file = None
    audio_file = None

    for file in os.listdir(fmf_path):
        if file.endswith((".mp4", ".webm")) and video_file is None:
            video_file = file
        elif file.endswith(".m4a") and audio_file is None:
            audio_file = file

        if video_file and audio_file:
            break  # Stop searching once both files are found

    return video_file, audio_file


def print_resolutions(yt: YouTube) -> list[str]:
    streams = yt.streams.filter(file_extension='mp4')  # StreamQuery object
    # Convert StreamQuery to a formatted string
    stream_string = "\n".join([str(stream) for stream in streams])
    # Extract resolutions using regex
    resolutions = re.findall(r'res="(\d+p)"', stream_string)
    # Remove duplicates and sort in descending order
    unique_resolutions = sorted(set(resolutions), key=lambda x: int(x[:-1]), reverse=True)

    return unique_resolutions


def find_file_by_string(directory: str, search_string: str, resolution: str, mp3: bool) -> str | None:
    """Searches a directory for a file containing a specific string in its filename.
    Returns the filename if found, otherwise returns None.
    """
    if resolution=="max":
        resolution = ""
    if mp3:
        resolution = "mp3"

    if not os.path.exists(directory):
        #print("Error: Directory does not exist!")
        return None

    # Iterate over each file in the directory
    for root, _, files in os.walk(directory):  # os.walk() traverses all subdirectories
        for filename in files:
            if search_string in filename and resolution in filename:
                return os.path.join(root, filename)  # Return full file path of the first match

    return None  # Return None if no file is found


def limit_resolution(resolution: str, limit: str) -> str:
    num_resolution = int(''.join(filter(str.isdigit, resolution)))  # Extract number from first resolution
    num_limit: int = 0
    if limit!="max":
        num_limit = int(''.join(filter(str.isdigit, limit)))  # Extract number from second resolution
    if limit=="max" or num_resolution < num_limit:
        max_resolution = resolution
    else:
        max_resolution = limit

    return max_resolution


def create_directories(restricted: bool, year: str) -> None:
    if restricted:
        if not os.path.exists(ytchannel_path + f"{str(year)}/restricted"):
            os.makedirs(ytchannel_path + f"{str(year)}/restricted")
    else:
        if not os.path.exists(ytchannel_path + f"{str(year)}"):
            os.makedirs(ytchannel_path + f"{str(year)}")


def download_video(channel_name: str, video_id: str, counter_id: int, video_total_count: int,
                   video_views: int, restricted: bool) -> None:
    restricted_path_snippet = ""
    colored_video_id = video_id
    # header_width = 95
    header_width = (header_width_global + 11)
    if restricted:
        yt = YouTube(youtube_base_url + video_id, use_oauth=True, allow_oauth_cache=True,
                     on_progress_callback=on_progress)
        restricted_path_snippet = "restricted/"
        colored_video_id = print_colored_text(video_id, BCOLORS.RED)
        # header_width = 104
        header_width = (header_width_global + 20)
    else:
        yt = YouTube(youtube_base_url + video_id, on_progress_callback=on_progress)

    # print(yt.vid_info)

    print("\n")
    print(format_header(colored_video_id + " - " + channel_name
                         + " - " + str(counter_id) + "/" + str(video_total_count), header_width))

    publishing_date = yt.publish_date.strftime("%Y-%m-%d")

    if year_subfolders:
        year = "/" + str(yt.publish_date.strftime("%Y"))
    else:
        year = ""

    res = max(print_resolutions(yt), key=lambda x: int(x.rstrip('p')))
    if limit_resolution_to != "max":
        res = limit_resolution(res, limit_resolution_to)

    print_video_infos(yt, res, video_views)

    if os.path.exists(
            ytchannel_path + year + "/" + restricted_path_snippet + str(publishing_date) + " - " + res + " - " + clean_string_regex(
                yt.title) + " - " + video_id + ".mp4") and not audio_or_video_bool:
        print(print_colored_text("\nVideo already downloaded\n", BCOLORS.GREEN))
    else:
        if audio_or_video_bool:
            if os.path.exists(
                    ytchannel_path + year + "/" + restricted_path_snippet + str(
                        publishing_date) + " - " + clean_string_regex(
                        yt.title) + " - " + video_id + ".mp3"):
                print(print_colored_text("\nMP3 already downloaded\n", BCOLORS.GREEN))

        more_than1080p = False

        if res == "2160p" or res == "1440p":
            more_than1080p = True
            video_file_tmp, audio_file_tmp = find_media_files("tmp")
            if video_file_tmp is not None:
                path = (ytchannel_path + str(year) + "/" + restricted_path_snippet + str(publishing_date) + " - " + res + " - "
                        + clean_string_regex(os.path.splitext(video_file_tmp)[0]) + " - " + video_id + ".mp4")
                print(print_colored_text("\nMerged file still available!", BCOLORS.BLACK))
                convert_webm_to_mp4("tmp/" + video_file_tmp, path, year, restricted)
            else:
                download_video_process(yt, res, more_than1080p, publishing_date, year, restricted)
        else:
            download_video_process(yt, res, more_than1080p, publishing_date, year, restricted)


def download_video_process(yt: YouTube, res: str, more_than1080p: bool, publishing_date: str, year: str,
                           restricted: bool) -> None:
    if not audio_or_video_bool:
        print(print_colored_text("\nDownloading VIDEO...", BCOLORS.BLACK))

        for idx, i in enumerate(yt.streams):
            if i.resolution == res:
                break
        yt.streams[idx].download()

    print(print_colored_text("\nDownloading AUDIO...", BCOLORS.BLACK))

    for idx, i in enumerate(yt.streams):
        if i.bitrate == "128kbps":
            break
    yt.streams[idx].download()

    rename_files_in_temp_directory()

    if audio_or_video_bool:
        convert_m4a_to_mp3(yt.video_id, publishing_date, year, restricted)
    else:
        if more_than1080p:
            convert_m4a_to_opus_and_merge(yt.video_id, publishing_date, res, year, restricted)
        else:
            merge_video_audio(yt.video_id, publishing_date, res, year, restricted)


def convert_m4a_to_mp3(video_id: str, publish_date: str, year: str, restricted: bool) -> None:
    video_file, audio_file = find_media_files(".")
    if not audio_file:
        print("❌ No M4A files found in the current directory.")
        return

    restricted_path = "/"
    if restricted:
        restricted_path = "/restricted/"

    create_directories(restricted, year)
    output_file = (ytchannel_path + str(year) + restricted_path + publish_date +
                   " - " + clean_string_regex(os.path.splitext(audio_file)[0]) + " - " + video_id + ".mp3")
    print(print_colored_text("\nConverting to MP3...", BCOLORS.BLACK))
    try:
        command = [
            "ffmpeg", "-loglevel", "quiet", "-stats",
            "-i", audio_file,  # Input file
            "-acodec", "libmp3lame",  # Use MP3 codec
            "-q:a", "2",  # Quality setting (lower is better)
            output_file
        ]
        subprocess.run(command, check=True)

    except Exception as ee:
        print(f"❌ Error merging files: {ee}")
        sys.exit(1)

    print(print_colored_text("\nMP3 downloaded\n", BCOLORS.GREEN))
    delete_temp_files()


def merge_video_audio(video_id: str, publish_date: str, video_resolution: str, year: str, restricted: bool) -> None:
    video_file, audio_file = find_media_files(".")

    if not video_file or not audio_file:
        print("❌ No MP4 or M4A files found in the current directory.")
        return

    restricted_path = "/"
    if restricted:
        restricted_path = "/restricted/"

    create_directories(restricted, year)
    output_file = (ytchannel_path + str(year) + restricted_path + publish_date + " - " + video_resolution
                   + " - " + clean_string_regex(os.path.splitext(video_file)[0]) + " - " + video_id + ".mp4")

    """Merge video and audio into a single MP4 file using FFmpeg."""
    try:
        print(print_colored_text("\nMerging to MP4...", BCOLORS.BLACK))
        command = [
            "ffmpeg", "-loglevel", "quiet", "-stats", "-i", video_file, "-i", audio_file,
            "-c:v", "copy", "-c:a", "aac", output_file
        ]
        subprocess.run(command, check=True)

        if restricted:
            print(print_colored_text("\nRestricted Video downloaded\n", BCOLORS.GREEN))
        else:
            print(print_colored_text("\nVideo downloaded\n", BCOLORS.GREEN))
        # remove video and audio streams
        delete_temp_files()

    except Exception as ee:
        print(f"❌ Error merging files: {ee}")
        sys.exit(1)


def convert_m4a_to_opus_and_merge(video_id: str, publish_date: str, video_resolution: str, year: str,
                                  restricted: bool) -> None:
    video_file, audio_file = find_media_files(".")
    """Convert M4A to Opus format (WebM-compatible)."""
    print(print_colored_text("\nConvert M4A audio to Opus format (WebM compatible)...", BCOLORS.BLACK))
    command = [
        "ffmpeg", "-loglevel", "quiet", "-stats", "-i", audio_file, "-c:a", "libopus", "audio.opus"
    ]
    subprocess.run(command, check=True)
    merge_webm_opus(video_id, publish_date, video_resolution, year, restricted)


def merge_webm_opus(video_id: str, publish_date: str, video_resolution: str, year: str, restricted: bool) -> None:
    video_file, audio_file = find_media_files(".")
    output_file = "tmp/" + video_file
    """Merge WebM video with Opus audio."""
    print(print_colored_text("Merging WebM video with Opus audio...", BCOLORS.BLACK))
    command = [
        "ffmpeg", "-loglevel", "quiet", "-stats", "-i", video_file, "-i", "audio.opus",
        "-c:v", "copy", "-c:a", "copy", output_file
    ]
    subprocess.run(command, check=True)
    # remove video and audio streams
    delete_temp_files()
    os.remove("audio.opus")
    restricted_string = "/"
    if restricted:
        restricted_string = "/restricted/"

    path = (ytchannel_path + str(year) + restricted_string + publish_date + " - " + video_resolution + " - "
            + clean_string_regex(os.path.splitext(video_file)[0]) + " - " + video_id + ".mp4")
    convert_webm_to_mp4(output_file, path, year, restricted)


def convert_webm_to_mp4(input_file: str, output_file: str, year: str, restricted: bool) -> None:
    create_directories(restricted, year)
    """Convert a WebM file to MP4 (H.264/AAC)."""
    print(print_colored_text(f"Converting WebM to MP4... (this may take a while)", BCOLORS.BLACK))
    command = [
        "ffmpeg", "-loglevel", "quiet", "-stats", "-i", input_file,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",  # H.264 video encoding
        "-c:a", "aac", "-b:a", "128k",  # AAC audio encoding
        "-movflags", "+faststart",  # Optimize MP4 for streaming
        output_file
    ]
    subprocess.run(command, check=True)
    os.remove(input_file)
    if restricted:
        print(print_colored_text("\nRestricted Video downloaded\n", BCOLORS.GREEN))
    else:
        print(print_colored_text("\nVideo downloaded\n", BCOLORS.GREEN))


while True:
    try:
        # Load config
        config = load_config("config.json")
        try:
        # Access settings
            output_dir = config["output_directory"]
            youtube_base_url = config["youtube_base_url"]
            min_duration = config["min_duration_in_minutes"]
            max_duration = config["max_duration_in_minutes"]
            video_listing = config["video_listing"]
            show_latest_video_date = config["show_latest_video_date"]
            default_audio_mp3 = config["default_audioMP3"]
        except Exception as e:
            print("An error occurred, incomplete config file:", str(e))
            cc_check_and_update_channel_config("config.json", REQUIRED_APP_CONFIG)
            continue

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create an empty list
        video_list = []
        video_list_restricted = []

        clear_screen()
        print(print_colored_text("\nYTDL " + str(version), BCOLORS.YELLOW))
        print("*" * len(str("YTDL " + str(version))))
        print("YouTube Channel Downloader (Exit with Ctrl + C)")
        #print("Exit App with Ctrl + C")
        #print(print_colored_text("https://github.com/SteveAustin79/YTDL\n", BCOLORS.BLACK))
        print("")
        delete_temp_files()
        print_configuration()

        lines = read_channel_txt_lines("channels.txt")
        if lines and len(lines) > 1:
            YTchannel = user_selection(lines, show_latest_video_date)
        else:
            YTchannel = input("\nYouTube Channel or Video URL:  ")
        if "- Enter YouTube Channel or Video URL -" in YTchannel:
            YTchannel = input("\nYouTube Channel or Video URL:  ")

        video_id_from_single_video = ""
        if youtube_base_url in YTchannel:
            ytv = YouTube(YTchannel, on_progress_callback=on_progress)
            YTchannel = ytv.channel_url
            video_id_from_single_video = ytv.video_id

        c = Channel(YTchannel)
        print("\n" + print_colored_text(print_colored_text(str(c.channel_name), BCOLORS.BOLD), BCOLORS.CYAN))
        print(print_colored_text(print_colored_text("*" * len(str(c.channel_name)), BCOLORS.BOLD), BCOLORS.CYAN))

        print(print_colored_text(c.channel_url, BCOLORS.CYAN))

        selected_video_ids = []

        if video_listing:
            more_than = ""
            if len(c.video_urls) > 50:
                more_than = " This can take a while..."

            list_all_videos = smart_input("\nList all " + str(len(c.video_urls)) + " Videos?" + more_than + " (Restricted videos in "
                                          + print_colored_text("red", BCOLORS.RED) + ")  Y/n", "y")

            if list_all_videos == "y":
                print("")

                # Display the video list with numbers
                video_list = list(c.videos)  # Convert to a list if not already

                for index, v_video in enumerate(video_list, start=1):
                    video_date_formated = print_colored_text(str(v_video.publish_date.strftime("%Y-%m-%d")), BCOLORS.BLACK)
                    video_message = f"{index}. {clean_string_regex(v_video.title)}"
                    space_formated = " " * (73-len(video_message))
                    if v_video.age_restricted:
                        print(print_colored_text(video_message + space_formated + video_date_formated, BCOLORS.RED))
                    else:
                        print(video_message + space_formated + video_date_formated)
                # Ask user for selection
                while True:
                    try:
                        choices = input("\nSelect one or more videos by entering numbers separated by commas: ")
                        if choices is None:
                            break
                        selected_indices = [int(x.strip()) for x in choices.split(",")]

                        # Validate selection
                        if all(1 <= index <= len(video_list) for index in selected_indices):
                            selected_videos = [video_list[i - 1] for i in selected_indices]  # Get the chosen videos
                            # print("You selected:")
                            for video in selected_videos:
                                # print(f"- {video.video_id}")
                                selected_video_ids.append(video.video_id)
                            break  # Exit loop if valid input
                        else:
                            print("Invalid choice(s), please enter valid numbers from the list.")
                    except ValueError:
                        print("Invalid input, please enter numbers separated by commas.")

        ytchannel_path = smart_input("\nDownload Path:  ",
                                     output_dir + "/" + clean_string_regex(c.channel_name).rstrip())
        default_max_res = "max"
        default_ignore_min_duration = "y"
        default_ignore_max_duration = "y"
        default_only_restricted = "n"
        default_skip_restricted = "n"
        default_minimum_views = "0"
        default_year_subfolders = "n"
        default_exclude_videos = ""
        default_include_videos = ""
        default_filter_words = ""

        channel_config_path = "/_config_channel.json"

        if os.path.exists(ytchannel_path + channel_config_path):
            incomplete_config = False
            incomplete_string = []
            # Load channel config
            channel_config = load_config(ytchannel_path + channel_config_path)
            # Access and set settings
            if "c_max_resolution" in channel_config:
                if channel_config["c_max_resolution"] != "":
                    default_max_res = channel_config["c_max_resolution"]
            else:
                incomplete_config = True
                incomplete_string.append("c_max_resolution")

            if "c_ignore_min_duration" in channel_config:
                if channel_config["c_ignore_min_duration"] != "":
                    default_ignore_min_duration = channel_config["c_ignore_min_duration"]
            else:
                incomplete_config = True
                incomplete_string.append("c_ignore_min_duration")

            if "c_ignore_max_duration" in channel_config:
                if channel_config["c_ignore_max_duration"] != "":
                    default_ignore_max_duration = channel_config["c_ignore_max_duration"]
            else:
                incomplete_config = True
                incomplete_string.append("c_ignore_max_duration")

            if "c_only_restricted" in channel_config:
                if channel_config["c_only_restricted"] != "":
                    default_only_restricted = channel_config["c_only_restricted"]
            else:
                incomplete_config = True
                incomplete_string.append("c_only_restricted")

            if "c_skip_restricted" in channel_config:
                if channel_config["c_skip_restricted"] != "":
                    default_skip_restricted = channel_config["c_skip_restricted"]
            else:
                incomplete_config = True
                incomplete_string.append("c_skip_restricted")

            if "c_minimum_views" in channel_config:
                if channel_config["c_minimum_views"] != "":
                    default_minimum_views = channel_config["c_minimum_views"]
            else:
                incomplete_config = True
                incomplete_string.append("c_minimum_views")

            if "c_year_subfolders" in channel_config:
                if channel_config["c_year_subfolders"] != "":
                    default_year_subfolders = channel_config["c_year_subfolders"]
            else:
                incomplete_config = True
                incomplete_string.append("c_year_subfolders")

            default_exclude_videos = channel_config["c_exclude_video_ids"]
            default_include_videos = channel_config["c_include_video_ids"]
            default_filter_words = channel_config["c_filter_words"]

            if incomplete_config:
                print(print_colored_text("\nIncomplete ", BCOLORS.ORANGE)
                      + print_colored_text("channel config file! --> Adding missing key(s) to file ", BCOLORS.BLUE)
                      + print_colored_text(str(incomplete_string), BCOLORS.ORANGE))
                cc_check_and_update_channel_config(ytchannel_path + channel_config_path, REQUIRED_VIDEO_CHANNEL_CONFIG)
            else:
                print(print_colored_text("\nChannel config file found! ", BCOLORS.BLUE) +
                      print_colored_text("(" + ytchannel_path + channel_config_path + ")", BCOLORS.BLACK))

        if video_id_from_single_video != "":
            default_include_videos = video_id_from_single_video

        if default_audio_mp3:
            default_value_mp3 = "a"
        else:
            default_value_mp3 = "v"
        audio_or_video = smart_input("\nAudio or Video?  a/v", default_value_mp3)
        audio_or_video_bool = True
        if audio_or_video == "v":
            audio_or_video_bool = False

        if audio_or_video_bool:
            limit_resolution_to = "max"
        else:
            limit_resolution_to = smart_input("Max. Resolution:  ", default_max_res)

        ignore_min_duration = smart_input("Ignore min_duration?  Y/n", default_ignore_min_duration)
        ignore_min_duration_bool = True
        if ignore_min_duration == "n":
            ignore_min_duration_bool = False
            print(print_colored_text("Ignoring Video(s) < " + str(min_duration) + " Minutes!", BCOLORS.RED))

        ignore_max_duration = smart_input("Ignore max_duration?  Y/n", default_ignore_max_duration)
        ignore_max_duration_bool = True
        if ignore_max_duration == "n":
            ignore_max_duration_bool = False
            print(print_colored_text("Ignoring Video(s) > " + str(max_duration) + " Minutes!", BCOLORS.RED))

        only_restricted_videos = smart_input("Only restricted video(s)?  Y/n", default_only_restricted)
        only_restricted_videos_bool = False
        if only_restricted_videos == "y":
            only_restricted_videos_bool = True
            print(print_colored_text("Downloading only restricted Video(s)!", BCOLORS.RED))

        skip_restricted_bool = False
        if not only_restricted_videos_bool:
            skip_restricted = smart_input("Skip restricted Video(s)?  Y/n", default_skip_restricted)
            if skip_restricted == "y":
                skip_restricted_bool = True
                print(print_colored_text("Skipping restricted Video(s)!", BCOLORS.RED))

        min_video_views = int(smart_input("Minimum Views (0=disabled): ", default_minimum_views))
        if min_video_views > 0:
            min_video_views_bool = True
        else:
            min_video_views_bool = False

        year_subfolders = False
        year_subfolders_temp = smart_input("Year sub folder structure?  Y/n", default_year_subfolders)
        if year_subfolders_temp == "y":
            year_subfolders = True
            print(print_colored_text("Year sub folder structure active!", BCOLORS.RED))

        exclude_video_ids = smart_input("\nExclude Video ID's (comma separated list): ", default_exclude_videos)
        exclude_list = []
        if exclude_video_ids != "":
            exclude_list = clean_youtube_urls(string_to_list(exclude_video_ids))

        if video_listing:
            if len(selected_video_ids) > 0:
                default_include_videos = ",".join(selected_video_ids)
        include_video_ids = smart_input("Include Video ID's (comma separated list): ", default_include_videos)
        include_list = []
        if include_video_ids != "":
            include_list = clean_youtube_urls(string_to_list(include_video_ids))

        video_name_filter = str(
            smart_input("\nEnter filter word(s) (comma separated list): ", default_filter_words))
        video_name_filter_list = string_to_list(video_name_filter)

        count_total_videos = 0
        count_restricted_videos = 0
        count_ok_videos = 0
        count_this_run = 0
        count_skipped = 0

        video_watch_urls = []

        if len(include_list) > 0:
            for include in include_list:
                video_watch_urls.append(youtube_base_url + include)
        else:
            print()
            for url in c.video_urls:
                count_total_videos += 1
                if url.video_id not in exclude_list:
                    if len(include_list) > 0:
                        if url.video_id in include_list:
                            video_watch_urls.append(url.watch_url)
                    else:
                        video_watch_urls.append(url.watch_url)
                print(f"\rFetching " + str(count_total_videos) + " videos", end="", flush=True)
            print(f"\rTotal {count_total_videos} Video(s) by: \033[96m{c.channel_name}\033[0m", end="", flush=True)
            print("\n")

        for url in video_watch_urls:
            only_video_id = pytubefix.extract.video_id(url)
            if find_file_by_string(ytchannel_path, only_video_id, limit_resolution_to, audio_or_video_bool) is not None:
                count_ok_videos += 1
                count_skipped += 1
                print(print_colored_text(f"\rSkipping {count_skipped} Videos", BCOLORS.MAGENTA), end="", flush=True)
            else:
                do_not_download = 0
                video = YouTube(youtube_base_url + only_video_id, on_progress_callback=on_progress)

                if video_name_filter == "" or any(
                        word.lower() in video.title.lower() for word in video_name_filter_list):
                    if not ignore_min_duration_bool:
                        video_duration = int(video.length / 60)
                        if video_duration < int(min_duration):
                            do_not_download = 1

                    if not ignore_max_duration_bool:
                        video_duration = int(video.length / 60)
                        if video_duration > int(max_duration):
                            do_not_download = 1

                    if min_video_views > 0:
                        if video.views < min_video_views:
                            do_not_download = 1

                    if (video.age_restricted == False and
                            video.vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE' and
                            video.vid_info.get('playabilityStatus', {}).get('status') != 'LIVE_STREAM_OFFLINE' and
                            do_not_download == 0 and not only_restricted_videos_bool):
                        count_ok_videos += 1
                        count_this_run += 1
                        count_skipped = 0
                        video_list.append(video.video_id)
                        download_video(clean_string_regex(c.channel_name).rstrip(), video.video_id,
                                       count_ok_videos, len(video_watch_urls), video.views, False)
                    else:
                        if not skip_restricted_bool:
                            if (video.vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE' and
                            video.vid_info.get('playabilityStatus', {}).get('status') != 'LIVE_STREAM_OFFLINE' and
                                    do_not_download == 0):
                                count_restricted_videos += 1
                                count_ok_videos += 1
                                count_this_run += 1
                                video_list_restricted.append(video.video_id)
                                download_video(clean_string_regex(c.channel_name).rstrip(), video.video_id,
                                               count_ok_videos, len(video_watch_urls), video.views, True)

        if count_this_run == 0:
            print("\n\n" + print_colored_text("Nothing to do...\n\n", BCOLORS.GREEN))
        else:
            print(print_colored_text(f"\nDONE! Downloaded in this session: {count_this_run}", BCOLORS.GREEN))
            print(f"\n{get_free_space(ytchannel_path)} free\n")

        continue_ytdl = smart_input("Continue?  Y/n ", "y")
        print("\n")
        if continue_ytdl == "y":
            continue
        else:
            break

    except Exception as e:
        delete_temp_files()
        print("An error occurred:", str(e))
        continue_ytdl = smart_input("There was an exception. Continue?  Y/n ", "y")
        print("\n")
        if continue_ytdl == "y":
            continue
        else:
            break

    except KeyboardInterrupt:
        delete_temp_files()
        continue_ytdl = smart_input("\n\nCtrl + C detected. Continue?  Y/n ", "y")
        print("\n")
        if continue_ytdl == "y":
            continue
        else:
            break
