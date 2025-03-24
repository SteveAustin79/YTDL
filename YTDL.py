import os
import re
import shutil
import subprocess
import json
import sys
import pytubefix.extract
from pytubefix import YouTube, Channel, Playlist
from pytubefix.cli import on_progress
from pathlib import Path
from datetime import datetime

# make min/max duration as channel config, not main config

version = "1.3.7 (20250324)"
header_width_global = 99
first_column_width = 17
first_column_width_wide = 37
youtube_url = "https://www.youtube.com/"
channel_config_path = "/_config_channel.json"
date_format_display = "%d.%m.%Y"
date_time_format = "%d.%m.%Y %H:%M:%S"
date_format_math = "%Y-%m-%d"

class BCOLORS:
    WHITE      = "\033[97m"
    CYAN       = "\033[96m"
    MAGENTA    = "\033[95m"
    BLUE       = "\033[94m"
    YELLOW     = "\033[93m"
    GREEN      = "\033[92m"
    RED        = "\033[91m"
    BLACK      = "\033[90m"
    DARK_WHITE = "\033[37m"
    DARK_CYAN  = "\033[36m"
    DARK_YELLOW= "\033[33m"
    DARK_GREEN = "\033[32m"
    DARK_RED   = "\033[31m"
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
    "show_latest_video_date": "",
    "filters_on_in_channels_list": "",
    "default_audioMP3": ""
}

REQUIRED_VIDEO_CHANNEL_CONFIG = {
    "c_max_resolution": "",
    "c_ignore_min_duration": "",
    "c_ignore_max_duration": "",
    "c_minimum_year": "",
    "c_maximum_year": "",
    "c_only_restricted": "",
    "c_skip_restricted": "",
    "c_minimum_views": "",
    "c_year_subfolders": "",
    "c_exclude_video_ids": "",
    "c_include_video_ids": "",
    "c_filter_words": ""
}


def channel_config_control() -> None:
    """ CHANNEL CONFIG CONTROL """

    if os.path.exists(ytchannel_path + channel_config_path):
        if (default_max_res != limit_resolution_to or default_ignore_min_duration != ignore_min_duration or
                default_ignore_max_duration != ignore_max_duration or default_minimum_year != min_year or
                default_maximum_year != max_year or default_only_restricted != only_restricted_videos or
                default_skip_restricted != skip_restricted or default_minimum_views != min_video_views or
                default_year_subfolders != year_subfolders_temp or default_exclude_videos != exclude_video_ids or
                default_include_videos != include_video_ids or default_filter_words != video_name_filter):
            update_settings_text = print_colored_text("\nUpdate settings in channel config file?  Y/n", BCOLORS.BLUE)
            save_settings_in_channel_config = smart_input(update_settings_text, "n")
            if save_settings_in_channel_config == "y":
                if default_max_res != limit_resolution_to:
                    update_json_config(ytchannel_path + channel_config_path, "c_max_resolution", limit_resolution_to)
                if default_ignore_min_duration != ignore_min_duration:
                    update_json_config(ytchannel_path + channel_config_path, "c_ignore_min_duration",
                                       ignore_min_duration)
                if default_ignore_max_duration != ignore_max_duration:
                    update_json_config(ytchannel_path + channel_config_path, "c_ignore_max_duration",
                                       ignore_max_duration)
                if default_minimum_year != min_year:
                    update_json_config(ytchannel_path + channel_config_path, "c_minimum_year", min_year)
                if default_maximum_year != max_year:
                    update_json_config(ytchannel_path + channel_config_path, "c_maximum_year", max_year)
                if default_only_restricted != only_restricted_videos:
                    update_json_config(ytchannel_path + channel_config_path, "c_only_restricted",
                                       only_restricted_videos)
                if default_skip_restricted != skip_restricted:
                    update_json_config(ytchannel_path + channel_config_path, "c_skip_restricted", skip_restricted)
                if default_minimum_views != min_video_views:
                    update_json_config(ytchannel_path + channel_config_path, "c_minimum_views", min_video_views)
                if default_year_subfolders != year_subfolders_temp:
                    update_json_config(ytchannel_path + channel_config_path, "c_year_subfolders", year_subfolders_temp)
                if default_exclude_videos != exclude_video_ids:
                    update_json_config(ytchannel_path + channel_config_path, "c_exclude_video_ids", exclude_video_ids)
                if default_include_videos != include_video_ids:
                    update_json_config(ytchannel_path + channel_config_path, "c_include_video_ids", include_video_ids)
                if default_filter_words != video_name_filter:
                    update_json_config(ytchannel_path + channel_config_path, "c_filter_words", video_name_filter)
    else:
        if (default_max_res != limit_resolution_to or default_ignore_min_duration != ignore_min_duration or
                default_ignore_max_duration != ignore_max_duration or default_minimum_year != min_year or
                default_maximum_year != max_year or default_only_restricted != only_restricted_videos or
                default_skip_restricted != skip_restricted or default_minimum_views != min_video_views or
                default_year_subfolders != year_subfolders_temp or default_exclude_videos != exclude_video_ids or
                default_include_videos != include_video_ids or default_filter_words != video_name_filter):
            create_text = print_colored_text("Create channel config file?  Y/n", BCOLORS.BLUE)
            create_channel_config_file = smart_input(create_text, "n")
            if create_channel_config_file == "y":
                json_max_res = ""
                if default_max_res != limit_resolution_to:
                    json_max_res = limit_resolution_to
                json_ignore_min_duration = ""
                if default_ignore_min_duration != ignore_min_duration:
                    json_ignore_min_duration = ignore_min_duration
                json_ignore_max_duration = ""
                if default_ignore_max_duration != ignore_max_duration:
                    json_ignore_max_duration = ignore_max_duration
                json_min_year = 0
                if default_minimum_year != min_year:
                    json_min_year = min_year
                json_max_year = 0
                if default_maximum_year != max_year:
                    json_max_year = max_year
                json_only_restricted_videos = ""
                if default_only_restricted != only_restricted_videos:
                    json_only_restricted_videos = only_restricted_videos
                json_skip_restricted = ""
                if default_skip_restricted != skip_restricted:
                    json_skip_restricted = skip_restricted
                json_min_video_views = 0
                if default_minimum_views != min_video_views:
                    json_min_video_views = min_video_views
                json_year_subfolders_temp = ""
                if default_year_subfolders != year_subfolders_temp:
                    json_year_subfolders_temp = year_subfolders_temp
                json_exclude_video_ids = ""
                if default_exclude_videos != exclude_video_ids:
                    json_exclude_video_ids = exclude_video_ids
                json_include_video_ids = ""
                if default_include_videos != include_video_ids:
                    json_include_video_ids = include_video_ids
                json_video_name_filter = ""
                if default_filter_words != video_name_filter:
                    json_video_name_filter = video_name_filter
                custom_values = {
                    "c_max_resolution": json_max_res,
                    "c_ignore_min_duration": json_ignore_min_duration,
                    "c_ignore_max_duration": json_ignore_max_duration,
                    "c_minimum_year": json_min_year,
                    "c_maximum_year": json_max_year,
                    "c_only_restricted": json_only_restricted_videos,
                    "c_skip_restricted": json_skip_restricted,
                    "c_minimum_views": json_min_video_views,
                    "c_year_subfolders": json_year_subfolders_temp,
                    "c_exclude_video_ids": json_exclude_video_ids,
                    "c_include_video_ids": json_include_video_ids,
                    "c_filter_words": json_video_name_filter
                }
                create_json_config(ytchannel_path + channel_config_path, custom_values)

    """ END OF CHANNEL CONFIG CONTROL """

def check_channels_txt(filename: str, c_url: str) -> bool:
    try:
        # Read existing URLs and remove empty lines
        with open(filename, "r", encoding="utf-8") as file:
            urls = sorted(set(line.strip() for line in file if line.strip()))  # Remove duplicates and sort

        # Check if the URL already exists
        if c_url in urls:
            # print("✅ URL already exists in the file.")
            return True
        else:
            return False
    except FileNotFoundError:
        # print("⚠️ File not found. Creating a new one and adding the URL.")
        # with open(filename, "w", encoding="utf-8") as file:
        #     file.write(url + "\n")
        return False


def add_url_in_order(filename: str, a_url: str) -> None:
    try:
        # Read existing URLs and remove empty lines
        with open(filename, "r", encoding="utf-8") as file:
            urls = sorted(set(line.strip() for line in file if line.strip()))  # Remove duplicates and sort

        # Check if the URL already exists
        if a_url in urls:
            # print("✅ URL already exists in the file.")
            return

        # Insert the new URL and sort again
        urls.append(a_url)
        urls.sort()

        # Write back the sorted list
        with open(filename, "w", encoding="utf-8") as file:
            file.write("\n".join(urls) + "\n")

        print("✅ URL added to channels.txt.")

    except FileNotFoundError:
        print("⚠️ File not found. Creating a new one and adding the URL.")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(url + "\n")


def create_json_config(file_path, config_values=None):
    """
    Creates a JSON config file at the specified path with default or custom values.

    Args:
        file_path (str): The path where the JSON file will be created.
        config_values (dict, optional): A dictionary containing key-value pairs for the config.
                                        If None, default values are used.

    Returns:
        bool: True if the file was created successfully, False otherwise.
    """

    # Merge default config with user-defined values
    if config_values:
        REQUIRED_VIDEO_CHANNEL_CONFIG.update(config_values)  # Override defaults if provided

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(REQUIRED_VIDEO_CHANNEL_CONFIG, f, indent=4)

        # print(f"✅ JSON config file created at: {file_path}")
        return True

    except Exception as json_e:
        print(f"❌ Error creating JSON file: {json_e}")
        return False


def organize_files_by_year(base_directory: str) -> None:
    if not os.path.exists(base_directory):
        print(f"Error: The directory '{base_directory}' does not exist.")
        return

    for file_name in os.listdir(base_directory):
        file_path = os.path.join(base_directory, file_name)

        # Ensure it's a file (not a folder)
        if os.path.isfile(file_path):
            # Extract year from filename (expects format: YYYY-...)
            parts = file_name.split("-")
            if parts[0].isdigit() and len(parts[0]) == 4:
                year = parts[0]
                year_folder = os.path.join(base_directory, year)

                # Create the year folder if it doesn't exist
                os.makedirs(year_folder, exist_ok=True)

                # Move the file to the corresponding year folder
                shutil.move(file_path, os.path.join(year_folder, file_name))
                # print(f"Moved: {file_name} → {year}/")
    print(print_colored_text("Created year sub folder structure!", BCOLORS.ORANGE))


def contains_folder_starting_with_2(path: str) -> bool:
    if os.path.exists(path):
        return any(name.startswith("2") and os.path.isdir(os.path.join(path, name)) for name in os.listdir(path))
    else:
        return False


def make_year_subfolder_structure(path: str) -> None:
    if os.path.exists(path):
        if (not contains_folder_starting_with_2(path) and
                any(file.endswith((".mp4", ".mp3")) for file in os.listdir(path)
                    if os.path.isfile(os.path.join(path, file)))):
            organize_files_by_year(path)


def update_json_config(file_path: str, parameter: str, new_value) -> bool:
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return False

    try:
        # Load existing JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            json_config = json.load(f)

        # Handle nested keys (e.g., "settings.database.host")
        keys = parameter.split(".")
        temp = json_config
        for key in keys[:-1]:  # Traverse to the second last key
            temp = temp.setdefault(key, {})  # Create dict if key doesn't exist

        # Update the final key
        temp[keys[-1]] = new_value

        # Save back to JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_config, f, indent=4)

        # print(f"✅ Updated '{parameter}' to '{new_value}' in '{file_path}'")
        return True

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'")
    except Exception as ujson_e:
        print(f"Error: {ujson_e}")

    return False


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

def cc_check_and_update_json_config(cc_file_path: str, cc_required_config: dict) -> None:
    """Ensures all required keys exist in the config file, adding missing ones."""
    cc_config = cc_load_config(cc_file_path)  # Load existing or empty config

    # Check for missing keys and add them
    missing_keys = []
    for key, default_value in cc_required_config.items():
        if key not in cc_config:
            cc_config[key] = default_value
            missing_keys.append(key)

    if missing_keys:
        cc_save_config(cc_file_path, cc_config)  # Save only if changes were made


def smart_input(prompt: str, default_value: str):
    user_input = input(f"{prompt} [{default_value}]: ").strip()
    return user_input if user_input else default_value


def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def load_config(c_file: str):
    with open(c_file, "r") as file:
        l_config = json.load(file)
    return l_config


def print_asteriks_line() -> None:
    now = datetime.now()
    free_space = print_colored_text(" " + get_free_space(output_dir) + " free | "
                                    + now.strftime(date_time_format) + " ", BCOLORS.BLACK)
    print(f"{free_space.center(header_width_global + 9, '*')}")

def print_colored_text(message_text: str, color: str) -> str:
    return f"{color}{message_text}{BCOLORS.ENDC}"


def extract_number(res: str):
    return int(''.join(filter(str.isdigit, res)))  # Extracts only numbers and converts to int


def clean_youtube_urls(to_clean_video_list: list) -> list[str]:
    prefix = youtube_watch_url
    return [to_clean_video.replace(prefix, "") for to_clean_video in to_clean_video_list]


def clean_string_regex(text: str) -> str:
    new_text = text.replace(":", "")
    pattern = r"[^a-zA-Z0-9 ]"
    return re.sub(pattern, "", new_text)


def string_to_list(input_string: str) -> list[str]:
    return [item.strip() for item in input_string.split(",")]


def print_configuration() -> None:
    print("Configuration (" + os.path.abspath("config.json") + "):")
    print_asteriks_line()
    print_configuration_line("Output directory:", output_dir, BCOLORS.CYAN)
    print_configuration_line("Minimum Video duration in Minutes:", min_duration, BCOLORS.CYAN)
    print_configuration_line("Maximum Video duration in Minutes:", max_duration, BCOLORS.CYAN)
    video_listing_color = BCOLORS.RED
    if video_listing:
        video_listing_color = BCOLORS.GREEN
    print_configuration_line("Video listing:", video_listing, video_listing_color)
    show_latest_video_date_color = BCOLORS.RED
    if show_latest_video_date:
        show_latest_video_date_color = BCOLORS.GREEN
    print_configuration_line("Show latest Video date:", show_latest_video_date, show_latest_video_date_color)
    default_audio_mp3_color = BCOLORS.RED
    default_filters_on_color = BCOLORS.RED
    if default_filters_on:
        default_filters_on_color = BCOLORS.GREEN
    print_configuration_line("Default Filters on channels list:", default_filters_on, default_filters_on_color)
    if default_audio_mp3:
        default_audio_mp3_color = BCOLORS.GREEN
    print_configuration_line("Default audio/MP3:", default_audio_mp3, default_audio_mp3_color)
    print_asteriks_line()
    print("")

def print_configuration_line(config_desc_text: str, config_value: str, config_value_color: str) -> None:
    print(print_colored_text(config_desc_text + " " * (first_column_width_wide - len(config_desc_text)), BCOLORS.BLACK),
          print_colored_text(config_value, config_value_color))


def format_header(counter: str, width: int) -> str:
    counter_split = counter.split(" - ")
    counter_str = ("*" * 2 + " " + counter_split[0] + " " + "*" * 2 +
                   print_colored_text(f" {counter_split[1]} ", BCOLORS.CYAN) +
                   "| " + counter_split[2] + " (" + get_free_space(output_dir) + " free) ")
    total_length = width - 2  # Exclude parentheses ()
    # Center the counter with asterisks
    formatted = f"{counter_str.ljust(total_length, '*')}"
    return formatted


def print_video_infos(yt: YouTube, res: str, video_views: int) -> None:
    print(print_colored_text("Title:" + " " * (first_column_width - len("Title:")), BCOLORS.BLACK),
          print_colored_text(print_colored_text(yt.title, BCOLORS.WHITE), BCOLORS.BOLD))

    views_title = print_colored_text("Views:" + " " * (first_column_width - len("Views:")), BCOLORS.BLACK)
    if min_video_views_bool:
        print(views_title, format_view_count(video_views), " (> " + format_view_count(min_video_views) + ")")
    else:
        print(views_title, format_view_count(video_views))

    year_title = print_colored_text("Date: " + " " * (first_column_width - len("Date:")), BCOLORS.BLACK)
    try:
        year_title_value = year_title + yt.publish_date.strftime(date_format_display)
    except Exception as eee:
        year_title_value = year_title + " " + str(eee)
    if min_year_bool and max_year_bool:
        print(year_title_value, print_colored_text("  (" + str(min_year) + " - " + str(max_year) + ")", BCOLORS.BLACK))
    elif min_year_bool:
        print(year_title_value, print_colored_text("  (" + str(min_year) + " - )", BCOLORS.BLACK))
    elif max_year_bool:
        print(year_title_value, print_colored_text("  ( - " + str(max_year) + ")", BCOLORS.BLACK))
    else:
        print(year_title_value)

    length_title = print_colored_text("Length: " + " " * (first_column_width - len("Length:")), BCOLORS.BLACK)
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
        print(print_colored_text("Resolution:" + " " * (first_column_width - len("Resolution:")), BCOLORS.BLACK),
              print_colored_text(res, BCOLORS.YELLOW),
              print_colored_text("  (" + limit_resolution_to + ")", BCOLORS.BLACK))
        print(" " * first_column_width, print_colored_text(str(print_resolutions(yt)), BCOLORS.BLACK))


def format_time(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}m{seconds}s"


def get_free_space(path: str) -> str:
    total, used, free = shutil.disk_usage(path)  # Get disk space (in bytes)
    # Convert bytes to GB or MB for readability
    if free >= 1_000_000_000:  # If space is at least 1GB
        formatted_space = f"{free / 1_073_741_824:.1f} GB"
    else:
        formatted_space = f"{free / 1_048_576:.0f} MB"  # Otherwise, use MB
    return formatted_space


def format_view_count(number: int) -> str:
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
    try:
        with open(filename, "r", encoding="utf-8") as file:
            rc_lines = [line.strip() for line in file if not line.lstrip().startswith("#")]  # Ignore commented lines
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
        for _ in range(12):     # 7 config line, 3 header/footer, 3 spaces = 13
            sys.stdout.write(BCOLORS.MOVES1UP)  # Move cursor up
            sys.stdout.write(BCOLORS.CLRLINE)  # Clear the line
        print("")
        print_asteriks_line()

    if temp_disable == "y":
        u_show_latest_video_date = False

    print("Select channel:")
    for u_index, line in enumerate(u_lines, start=1):
        if not line == u_lines[(len(u_lines) - 1)]:
            spaces = (header_width_global - 54)
            ytchannel_info = Channel(line)
            if u_show_latest_video_date:
                ytchannel_info_channel_name = ytchannel_info.channel_name
                ytchannel_info_videos = ytchannel_info.videos

                c_year_active = print_colored_text(".", BCOLORS.BLACK)
                c_restricted_active = print_colored_text(".", BCOLORS.BLACK)
                c_resolution_active = print_colored_text(".", BCOLORS.BLACK)
                c_filter_words_active = print_colored_text("." * 13, BCOLORS.BLACK)

                if os.path.exists(output_dir + "/" + clean_string_regex(ytchannel_info_channel_name).rstrip() + channel_config_path):
                    c_year_active = print_colored_text("-", BCOLORS.DARK_GREEN)
                    c_restricted_active = print_colored_text("-", BCOLORS.RED)
                    c_resolution_active = print_colored_text("-", BCOLORS.YELLOW)
                    c_filter_words_active = print_colored_text("---".center(13)[:13], BCOLORS.DARK_CYAN)

                    ch_config = load_config(
                        output_dir + "/" + clean_string_regex(ytchannel_info_channel_name).rstrip() + channel_config_path)

                    if ch_config["c_year_subfolders"]=="y":
                        c_year_active = print_colored_text("Y", BCOLORS.DARK_GREEN)

                    if ch_config["c_only_restricted"]=="y":
                        c_restricted_active = print_colored_text("R", BCOLORS.RED)

                    if ch_config["c_max_resolution"]=="max":
                        c_resolution_active = print_colored_text("M", BCOLORS.YELLOW)
                    elif ch_config["c_max_resolution"]=="1080p":
                        c_resolution_active = print_colored_text("1", BCOLORS.YELLOW)
                    elif ch_config["c_max_resolution"]=="720p":
                        c_resolution_active = print_colored_text("7", BCOLORS.YELLOW)
                    elif ch_config["c_max_resolution"]=="2160p":
                        c_resolution_active = print_colored_text("2", BCOLORS.YELLOW)

                    if ch_config["c_filter_words"]!="":
                        c_filter_words_active = print_colored_text(ch_config["c_filter_words"].center(13)[:13], BCOLORS.DARK_CYAN)

                combined_settings = c_resolution_active + c_restricted_active + c_year_active + c_filter_words_active

                line = line.replace(youtube_url, "")[1:]
                got_it = False
                main_config = load_config("config.json")
                try:
                    ch_config_filter_words = ""
                    config_min_duration = 0
                    config_max_duration = 999
                    ch_config_restricted = { True, False }
                    ch_config_min_views = 0
                    ch_config_exclude_list = string_to_list("")

                    if os.path.exists(output_dir + "/" + clean_string_regex(ytchannel_info_channel_name).rstrip() + channel_config_path)\
                            and default_filters_on:
                        ch_config = load_config(output_dir + "/" + clean_string_regex(ytchannel_info_channel_name).rstrip() + channel_config_path)

                        ch_config_filter_words = ch_config["c_filter_words"]
                        # if int(main_config["min_duration_in_minutes"]) > 0:
                        if str(main_config["min_duration_in_minutes"]).strip():
                            config_min_duration = int(main_config["min_duration_in_minutes"])
                        if str(main_config["max_duration_in_minutes"]).strip():
                            config_max_duration = int(main_config["max_duration_in_minutes"])
                        if str(ch_config["c_minimum_views"]).strip():
                            ch_config_min_views = int(ch_config["c_minimum_views"])
                        if ch_config["c_only_restricted"]=="y":
                            ch_config_restricted.remove(False)
                        ch_config_exclude_list = string_to_list(ch_config["c_exclude_video_ids"])



                    print(print_colored_text(f"\r" + " " * (len(str(u_index)) + 2) + "Scanning channel... ", BCOLORS.DARK_GREEN) +
                                print_colored_text(print_colored_text(ytchannel_info_channel_name, BCOLORS.BOLD), BCOLORS.GREEN), end="", flush=True)
                    all_channel_videos = list(ytchannel_info_videos)



                    for i in range(len(all_channel_videos)):
                        youtube_video_object = all_channel_videos[i]
                        youtube_vo_video_id = youtube_video_object.video_id
                        youtube_vo_author = youtube_video_object.author
                        youtube_vo_title = youtube_video_object.title
                        youtube_vo_vid_info = youtube_video_object.vid_info
                        youtube_vo_length = youtube_video_object.length
                        youtube_vo_views = youtube_video_object.views
                        youtube_vo_age_restricted = youtube_video_object.age_restricted
                        youtube_vo_publish_date = youtube_video_object.publish_date

                        print(print_colored_text(f"\r" + " " * (len(str(u_index)) + 2) + "Find match: ", BCOLORS.DARK_GREEN) +
                                print_colored_text(print_colored_text(str(i + 1) + "/" + str(len(all_channel_videos)) + " | " +
                                youtube_vo_video_id, BCOLORS.GREEN), BCOLORS.BOLD) +
                                print_colored_text(" | " + str(str(youtube_vo_author)[:22] + " | "
                                                   + youtube_vo_title).ljust(57, " ")[:57], BCOLORS.DARK_GREEN), end="", flush=True)
                        if (youtube_vo_vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE' and
                                youtube_vo_vid_info.get('playabilityStatus', {}).get('status') != 'LIVE_STREAM_OFFLINE' and
                                any(word.lower() in youtube_vo_title.lower() for word in string_to_list(ch_config_filter_words))
                                and youtube_vo_video_id not in ch_config_exclude_list
                                and config_min_duration <= int(youtube_vo_length / 60) <= config_max_duration
                                and youtube_vo_views >= ch_config_min_views
                                and youtube_vo_age_restricted in ch_config_restricted):

                            latest_video_name_text = youtube_vo_title
                            latest_date_math = youtube_vo_publish_date.strftime(date_format_math)
                            latest_date = youtube_vo_publish_date.strftime(date_format_display)
                            channel_total_videos = " " + str(len(all_channel_videos)).rjust(5)[:5] + " | "
                            latest_video_id_text = youtube_vo_video_id
                            if youtube_vo_age_restricted:
                                latest_video_id_text = print_colored_text(latest_video_id_text, BCOLORS.DARK_RED)
                            latest_id_and_name = " | " + latest_video_id_text + print_colored_text(" | " + latest_video_name_text[:15], BCOLORS.BLACK)

                            got_it = find_file_by_string(output_dir + "/" +
                                        clean_string_regex(ytchannel_info_channel_name).rstrip(), latest_date_math, "", False)
                            if not got_it:
                                latest_date = print_colored_text(latest_date, BCOLORS.RED)
                                latest_id_and_name = (print_colored_text(" | " + latest_video_id_text + " | " +
                                                      latest_video_name_text[:15], BCOLORS.DARK_WHITE))
                                channel_total_videos = print_colored_text(channel_total_videos, BCOLORS.DARK_WHITE)

                            latest_date_formated = (
                                    " " + print_colored_text("." * ((spaces - len(str(u_index)) - len(line)) - 16), BCOLORS.BLACK)
                                    + combined_settings + print_colored_text(channel_total_videos, BCOLORS.BLACK)
                                    + print_colored_text(latest_date, BCOLORS.BLACK)
                                     + print_colored_text(latest_id_and_name, BCOLORS.BLACK))
                            break

                    if got_it:
                        line = print_colored_text(line, BCOLORS.BLACK)
                except Exception as eee:
                    latest_date_formated = (" " + print_colored_text("." * ((spaces - len(str(u_index)) - len(line)) - 2), BCOLORS.BLACK)
                                            + " " + print_colored_text(str(eee), BCOLORS.RED))
            else:
                latest_video_from_channel = ytchannel_info.last_updated.strftime(date_format_display)
                latest_date_formated = (" " + print_colored_text("." * ((spaces - len(str(u_index)) - len(line)) - 16), BCOLORS.BLACK)
                                        + print_colored_text(latest_video_from_channel, BCOLORS.BLACK))

        print(f"\r{u_index}. {line}{latest_date_formated}", flush=True)
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
    video_file, audio_file = find_media_files(".")
    # Check if files exist before deleting
    if video_file and os.path.exists(video_file):
        os.remove(video_file)
    if audio_file and os.path.exists(audio_file):
        os.remove(audio_file)


def find_media_files(fmf_path: str) -> tuple[str | None, str | None]:
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
    if resolution=="max":
        resolution = ""
    if mp3:
        resolution = "mp3"

    if not os.path.exists(directory):
        return None

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

def find_json_files(directory: str) -> list[str]:
    """Searches a directory and its subdirectories for JSON files and returns their full paths."""
    return [str(file) for file in Path(directory).rglob("*.json")]


def download_video(channel_name: str, video_id: str, counter_id: int, video_total_count: int,
                   video_views: int, restricted: bool) -> None:
    restricted_path_snippet = ""
    colored_video_id = video_id
    header_width = (header_width_global + 11)
    if restricted:
        y_tube = YouTube(youtube_watch_url + video_id, use_oauth=True, allow_oauth_cache=True,
                     on_progress_callback=on_progress)
        restricted_path_snippet = "restricted/"
        colored_video_id = print_colored_text(video_id, BCOLORS.RED)
        header_width = (header_width_global + 20)
    else:
        y_tube = YouTube(youtube_watch_url + video_id, on_progress_callback=on_progress)

    y_tube_publish_date = y_tube.publish_date
    y_tube_title = y_tube.title

    print("\n")
    print(format_header(colored_video_id + " - " + channel_name
                         + " - " + str(counter_id) + "/" + str(video_total_count), header_width))

    try:
        publishing_date = y_tube_publish_date.strftime(date_format_math)
    except Exception as eee:
        publishing_date = eee

    # print(yt.vid_info.get('playabilityStatus'))

    if year_subfolders:
        year = "/" + str(y_tube_publish_date.strftime("%Y"))
    else:
        year = ""

    res = max(print_resolutions(y_tube), key=lambda x: int(x.rstrip('p')))
    if limit_resolution_to != "max":
        res = limit_resolution(res, limit_resolution_to)

    print_video_infos(y_tube, res, video_views)

    if os.path.exists(
            ytchannel_path + year + "/" + restricted_path_snippet + str(publishing_date) + " - " + res + " - " +
            clean_string_regex(y_tube_title) + " - " + video_id + ".mp4") and not audio_or_video_bool:
        print(print_colored_text("\nVideo already downloaded\n", BCOLORS.GREEN))
    else:
        if audio_or_video_bool:
            if os.path.exists(ytchannel_path + year + "/" + restricted_path_snippet +
                        str(publishing_date) + " - " + clean_string_regex(y_tube_title) + " - " + video_id + ".mp3"):
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
                download_video_process(y_tube, res, more_than1080p, publishing_date, year, restricted)
        else:
            download_video_process(y_tube, res, more_than1080p, publishing_date, year, restricted)


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
    print(print_colored_text("\nConvert M4A audio to Opus format (WebM compatible)...", BCOLORS.BLACK))
    command = [
        "ffmpeg", "-loglevel", "quiet", "-stats", "-i", audio_file, "-c:a", "libopus", "audio.opus"
    ]
    subprocess.run(command, check=True)
    merge_webm_opus(video_id, publish_date, video_resolution, year, restricted)


def merge_webm_opus(video_id: str, publish_date: str, video_resolution: str, year: str, restricted: bool) -> None:
    video_file, audio_file = find_media_files(".")
    output_file = "tmp/" + video_file
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
            youtube_watch_url = config["youtube_watch_url"]
            min_duration = config["min_duration_in_minutes"]
            max_duration = config["max_duration_in_minutes"]
            video_listing = config["video_listing"]
            show_latest_video_date = config["show_latest_video_date"]
            default_filters_on = config["filters_on_in_channels_list"]
            default_audio_mp3 = config["default_audioMP3"]
        except Exception as e:
            print("An error occurred, incomplete config file:", str(e))
            cc_check_and_update_json_config("config.json", REQUIRED_APP_CONFIG)
            continue

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create empty lists
        video_list = []
        video_list_restricted = []

        clear_screen()
        print(print_colored_text("\nYTDL " + str(version), BCOLORS.YELLOW))
        print(print_colored_text("*" * len(str("YTDL " + str(version))), BCOLORS.YELLOW))
        print(print_colored_text("YouTube Channel Downloader (Exit with Ctrl + C)", BCOLORS.BLACK))
        print("")
        delete_temp_files()
        print_configuration()

        lines = read_channel_txt_lines("channels.txt")
        if lines and len(lines) > 1:
            YTchannel = user_selection(lines, show_latest_video_date)
        else:
            YTchannel = input("\nYouTube Channel, Video-, or Playlist URL:  ")
        if "- Enter YouTube Channel or Video URL -" in YTchannel:
            YTchannel = input("\nYouTube Channel, Video-, or Playlist URL:  ")

        print("")
        print_asteriks_line()

        video_id_from_single_video = ""
        if youtube_watch_url in YTchannel:
            ytv = YouTube(YTchannel)
            YTchannel = ytv.channel_url
            video_id_from_single_video = ytv.video_id
        elif "https://" not in YTchannel:
            ytv = YouTube(youtube_watch_url + YTchannel)
            YTchannel = ytv.channel_url
            video_id_from_single_video = ytv.video_id
        elif "list=" in YTchannel:
            playlist = Playlist(YTchannel)
            YTchannel = playlist.owner_url
            for p_video in playlist.videos:
                video_id_from_single_video += p_video.video_id + ","
            video_id_from_single_video = video_id_from_single_video[:-1]

        channelYT = Channel(YTchannel)
        channelYT_name = channelYT.channel_name
        channelYT_url = channelYT.channel_url
        channelYT_video_urls = channelYT.video_urls
        channelYT_videos = channelYT.videos

        print("\n" + print_colored_text(print_colored_text(str(channelYT_name), BCOLORS.BOLD), BCOLORS.CYAN))
        print(print_colored_text(print_colored_text("*" * len(str(channelYT_name)), BCOLORS.BOLD), BCOLORS.CYAN))
        print(print_colored_text(channelYT_url, BCOLORS.CYAN))

        # check if channels.txt has this url, if not, add it
        if not check_channels_txt("channels.txt", channelYT_url):
            add_url_to_channels_txt = smart_input("Add chanel to channels.txt?  Y/n", "n")
            if add_url_to_channels_txt=="y":
                add_url_in_order("channels.txt", channelYT_url)

        selected_video_ids = []

        if video_listing:
            more_than = ""
            if len(channelYT_video_urls) > 50:
                more_than = " This can take a while..."

            list_all_videos = smart_input("\nList all " + str(len(channelYT_video_urls)) + " Videos?" + more_than + " (Restricted videos in "
                                          + print_colored_text("red", BCOLORS.RED) + ")  Y/n", "y")
            if list_all_videos == "y":
                print("")
                # Display the video list with numbers
                video_list = list(channelYT_videos)  # Convert to a list if not already
                for index, v_video in enumerate(video_list, start=1):
                    video_date_formated = print_colored_text(str(v_video.publish_date.strftime(date_format_display)), BCOLORS.BLACK)
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

        ytchannel_path = smart_input("\nDownload Path:" + " " * (first_column_width - len("Download Path:")),
                                     output_dir + "/" + clean_string_regex(channelYT_name).rstrip())
        default_max_res = "max"
        default_ignore_min_duration = "y"
        default_ignore_max_duration = "y"
        default_minimum_year = 0
        default_maximum_year = 0
        default_only_restricted = "n"
        default_skip_restricted = "n"
        default_minimum_views = 0
        default_year_subfolders = "n"
        default_exclude_videos = ""
        default_include_videos = ""
        default_filter_words = ""

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

            if "c_minimum_year" in channel_config:
                if channel_config["c_minimum_year"] != "":
                    default_minimum_year = channel_config["c_minimum_year"]
            else:
                incomplete_config = True
                incomplete_string.append("c_minimum_year")

            if "c_maximum_year" in channel_config:
                if channel_config["c_maximum_year"] != "":
                    default_maximum_year = channel_config["c_maximum_year"]
            else:
                incomplete_config = True
                incomplete_string.append("c_maximum_year")

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

            if "c_exclude_video_ids" in channel_config:
                if channel_config["c_exclude_video_ids"] != "":
                    default_exclude_videos = channel_config["c_exclude_video_ids"]
            else:
                incomplete_config = True
                incomplete_string.append("c_exclude_video_ids")

            if "c_include_video_ids" in channel_config:
                if channel_config["c_include_video_ids"] != "":
                    default_include_videos = channel_config["c_include_video_ids"]
            else:
                incomplete_config = True
                incomplete_string.append("c_include_video_ids")

            if "c_filter_words" in channel_config:
                if channel_config["c_filter_words"] != "":
                    default_filter_words = channel_config["c_filter_words"]
            else:
                incomplete_config = True
                incomplete_string.append("c_filter_words")

            if incomplete_config:
                print(print_colored_text("\nIncomplete ", BCOLORS.DARK_YELLOW)
                      + print_colored_text("channel config file! --> Adding missing key(s) to file ", BCOLORS.BLUE)
                      + print_colored_text(str(incomplete_string), BCOLORS.DARK_YELLOW))
                cc_check_and_update_json_config(ytchannel_path + channel_config_path, REQUIRED_VIDEO_CHANNEL_CONFIG)
            else:
                print(print_colored_text("\nChannel config file found! ", BCOLORS.BLUE) +
                      print_colored_text("\n" + ytchannel_path + channel_config_path, BCOLORS.BLACK))

        if video_id_from_single_video != "":
            default_include_videos = video_id_from_single_video

        default_value_mp3 = "v"
        if default_audio_mp3:
            default_value_mp3 = "a"

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

        min_year = smart_input("Minimum Year (0=disabled):  ", default_minimum_year)
        min_year_bool = False
        if str(min_year).isdigit() and 1900 <= int(min_year) <= 2100 and int(min_year)!=0:
            min_year_bool = True

        max_year = smart_input("Maximum Year (0=disabled):  ", default_maximum_year)
        max_year_bool = False
        if str(max_year).isdigit() and 1900 <= int(max_year) <= 2100 and int(max_year)!=0:
            max_year_bool = True

        only_restricted_videos = smart_input("Only restricted video(s)?  Y/n", default_only_restricted)
        only_restricted_videos_bool = False
        if only_restricted_videos == "y":
            only_restricted_videos_bool = True
            print(print_colored_text("Downloading only restricted Video(s)!", BCOLORS.RED))

        skip_restricted = default_skip_restricted
        skip_restricted_bool = False
        if not only_restricted_videos_bool:
            skip_restricted = smart_input("Skip restricted Video(s)?  Y/n", default_skip_restricted)
            if skip_restricted == "y":
                skip_restricted_bool = True
                print(print_colored_text("Skipping restricted Video(s)!", BCOLORS.RED))

        min_video_views = int(smart_input("Minimum Views (0=disabled): ", default_minimum_views))
        min_video_views_bool = False
        if min_video_views > 0:
            min_video_views_bool = True

        year_subfolders = False
        year_subfolders_temp = smart_input("Year sub folder structure?  Y/n", default_year_subfolders)
        if year_subfolders_temp == "y":
            year_subfolders = True
            print(print_colored_text("Year sub folder structure active!", BCOLORS.RED))
            make_year_subfolder_structure(ytchannel_path)
        else:
            if contains_folder_starting_with_2(ytchannel_path) and os.path.exists(ytchannel_path + channel_config_path):
                print(print_colored_text("Year sub folder structure found!", BCOLORS.RED))
                update_channel_config = smart_input("Update selection and channel config?  Y/n", "y")
                if update_channel_config == "y":
                    update_json_config(ytchannel_path + channel_config_path, "c_year_subfolders", "y")
                    year_subfolders = True

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

        channel_config_control()

        count_total_videos = 0
        count_restricted_videos = 0
        count_ok_videos = 0
        count_this_run = 0
        count_skipped = 0

        video_watch_urls = []

        if len(include_list) > 0:
            for include in include_list:
                video_watch_urls.append(youtube_watch_url + include)
        else:
            print()
            for url in channelYT_video_urls:
                count_total_videos += 1
                if url.video_id not in exclude_list:
                    if len(include_list) > 0:
                        if url.video_id in include_list:
                            video_watch_urls.append(url.watch_url)
                    # else:
                    video_watch_urls.append(url.watch_url)
                print(f"\rFetching " + str(count_total_videos) + " videos", end="", flush=True)
            print(f"\rTotal {count_total_videos} Video(s) by: \033[96m{channelYT_name}\033[0m", end="", flush=True)
            print("\n")

        for url in video_watch_urls:
            only_video_id = pytubefix.extract.video_id(url)
            if find_file_by_string(ytchannel_path, only_video_id, limit_resolution_to, audio_or_video_bool) is not None:
                count_ok_videos += 1
                count_skipped += 1
                print(print_colored_text(f"\rSkipping {count_skipped} Videos", BCOLORS.MAGENTA), end="", flush=True)
            else:
                do_not_download = 0
                video = YouTube(youtube_watch_url + only_video_id)

                if video_name_filter == "" or any(
                        word.lower() in video.title.lower() for word in video_name_filter_list):
                    if not ignore_min_duration_bool:
                        video_duration = int(video.length / 60)
                        if video_duration <= int(min_duration):
                            do_not_download = 1

                    if not ignore_max_duration_bool:
                        video_duration = int(video.length / 60)
                        if video_duration >= int(max_duration):
                            do_not_download = 1

                    if int(min_year) > 0:
                        if int(video.publish_date.strftime("%Y")) <= int(min_year):
                            do_not_download = 1
                            break

                    if int(max_year) > 0:
                        if int(video.publish_date.strftime("%Y")) >= int(max_year):
                            do_not_download = 1

                    if min_video_views > 0:
                        if video.views <= min_video_views:
                            do_not_download = 1

                    if (not video.age_restricted and
                            video.vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE' and
                            video.vid_info.get('playabilityStatus', {}).get('status') != 'LIVE_STREAM_OFFLINE' and
                            do_not_download == 0 and not only_restricted_videos_bool):
                        count_ok_videos += 1
                        count_this_run += 1
                        count_skipped = 0
                        video_list.append(video.video_id)
                        download_video(clean_string_regex(channelYT_name).rstrip(), video.video_id,
                                       count_ok_videos, len(video_watch_urls), video.views, False)
                    else:
                        if not skip_restricted_bool:
                            if (video.age_restricted and video.vid_info.get('playabilityStatus', {}).get('status') != 'UNPLAYABLE' and
                                    video.vid_info.get('playabilityStatus', {}).get('status') != 'LIVE_STREAM_OFFLINE' and
                                    do_not_download == 0):
                                count_restricted_videos += 1
                                count_ok_videos += 1
                                count_this_run += 1
                                video_list_restricted.append(video.video_id)
                                download_video(clean_string_regex(channelYT_name).rstrip(), video.video_id,
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
