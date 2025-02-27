import os
import glob
import cv2
import json


def load_config():
    """Load settings from config.json."""
    with open("config.json", "r") as file:
        config = json.load(file)
    return config


def smart_input(prompt, default_value):
    user_input = input(f"{prompt} [{default_value}]: ").strip()
    return user_input if user_input else default_value


def get_video_resolution(video_path):
    """Returns the resolution (width x height) of a given video file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return f"{width}x{height}"


def rename_videos_in_folder(folder_path):
    """Scans the given folder for .mp4 files, retrieves resolution, and renames files."""
    mp4_files = glob.glob(os.path.join(folder_path, "*.mp4"))

    for file_path in mp4_files:
        resolution = get_video_resolution(file_path)
        if resolution:
            print(resolution)
            #directory, filename = os.path.split(file_path)
            #name, ext = os.path.splitext(filename)
            #new_filename = f"{name}_{resolution}{ext}"
            #new_file_path = os.path.join(directory, new_filename)

            # Rename the file if the new name is different
            #if file_path != new_file_path:
            #    os.rename(file_path, new_file_path)
            #    print(f"Renamed: {filename} → {new_filename}")
            #else:
            #    print(f"Skipped (already renamed): {filename}")


if __name__ == "__main__":
    # Load config
    config = load_config()
    # Access settings
    output_dir = config["output_directory"]

    folder = smart_input("\nFolder Path:  ", output_dir)
    if os.path.exists(folder):
        rename_videos_in_folder(folder)
    else:
        print("Invalid folder path. Please try again.")

