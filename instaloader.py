import subprocess
import platform
import os
from pathlib import Path
import signal
import sys

# Detect if the OS is Windows
def is_windows():
    return platform.system().lower() == "windows"

# Function to run instaloader with graceful handling of interruptions
def instaloader_init(*args):
    args = list(args)
    instaloader_dir = rhqArchive / "Data" / "Self" / "Media" / "Photos and Videos" / "latest" / "Bulk" / "Pictures" / "instaloader"
    user_names = []
    remaining_args = []
    full_update_arg = False

    try:
        os.chdir(instaloader_dir)  # Change to the instaloader directory

        # Handle Login arguments
        if "login_arg" in args:
            remaining_args.append("--login=entropy.observed")
        else:
            print("No login argument passed by default inside the script; expect access errors.")

        # Check for full update argument
        if "full_update_arg" in args:
            
            print("\nFull update mode. This will update the whole library in your instaloader folder!")
            user_names = [f.name for f in Path(instaloader_dir).iterdir() if f.is_dir()]
            print(f"\nFolders or usernames found: {user_names}")
            full_update_arg = True

        # Extract usernames from args
        if isinstance(args, list):
            usernames = [item.split("/")[-1].split("?")[0] for item in args if "http" in item]
            user_names.extend(usernames)
        elif isinstance(args, str) and "http" in args:
            usernames = args.split("/")[-1].split("?")[0]
            if usernames:
                user_names.append(usernames)
        elif args:
            # Collect any remaining arguments not considered as URLs
            print("\nNo Instagram link detected. Using the last argument as the username.")
            user_names.append(args[-1])

        # Remove the last argument if not needed
        if args:
            args.pop()

        for username in user_names:
            print(f"\nCurrently working for: {username}")
            if full_update_arg:
                current_directory = instaloader_dir / username
                remaining_args_to_remove = ["--fast-update", "--no-videos", "--no-pictures"]
                remaining_args = [arg for arg in remaining_args if arg not in remaining_args_to_remove]
                is_video_present = False
                is_image_present = False
                is_video_present = any(f.suffix == '.mp4' for f in current_directory.iterdir())
                is_image_present = any(f.suffix == '.jpg' for f in current_directory.iterdir())
                if is_image_present and is_video_present:
                    remaining_args.append("--fast-update")
                else:
                    if is_image_present:
                        remaining_args.append("--no-videos")
                        remaining_args.append("--fast-update")
                    if is_video_present:
                        remaining_args.append("--no-pictures")

            args_to_remove = ["full_update_arg", "login_arg"]
            remaining_master_args = [arg for arg in args if arg not in args_to_remove]

            # Construct instaloader command
            instaloader_cmd = ['instaloader', '--no-video-thumbnails', '--no-metadata-json', '--no-captions'] + remaining_args + remaining_master_args + [username]
            subprocess.run(instaloader_cmd, shell=is_windows())  # Run the command
            
            # Ask about EXIF handling
            if not full_update_arg:
                set_exif = input("Do you want to set date EXIF(s) from filename(s)? (yes/No): ").lower()
                if set_exif in ["y", "yes"]:
                    try:
                        os.chdir(username)
                        print(f"Setting date EXIF(s) from filename(s) for {username}...")
                        for file_name in os.listdir():
                            if file_name.endswith(('.jpg', '.jpeg', '.png')):
                                date_part = file_name[:10]  # Assuming 'YYYY-MM-DD' at the beginning
                                time_part = file_name[11:19].replace('-', ':')  # 'HH-MM-SS' in filename
                                datetime = f"{date_part} {time_part}"
                                subprocess.run(['exiftool', '-q', '-overwrite_original', f'-AllDates={datetime}', file_name], stdout=subprocess.DEVNULL)
                        print(f"EXIF setting complete for {username}.")
                    except FileNotFoundError:
                        print(f"Directory for {username} not found. Skipping EXIF setting.")
                    os.chdir(instaloader_dir)  # Go back to the instaloader directory
                else:
                    print("Operation canceled.")
            else:
                print("\nSetting EXIF has been canceled automatically due to full update mode.")
            print("\nComplete!\n\n")

    except KeyboardInterrupt:
        print("\nOperation interrupted by user. Exiting gracefully...")
        sys.exit(1)  # Exit the program after graceful handling
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function that handles the instaloader mode selection
def main(*args):
    global user_names
    global instaloader_dir
    try:
        if args[0] in ["instl", "instal", "instaloader"]:
            mode = args[1] if len(args) > 1 else ""
            if mode in ["i", "img", "image", "images", "r", "reg", "regular"]:
                instaloader_init("login_arg", "--no-videos", *args[2:])
            elif mode in ["v", "vid", "video", "videos"]:
                instaloader_init("login_arg", "--no-pictures", *args[2:])
            elif mode in ["iv", "i_v", "imgvid", "imgvids", "imgsvids", "img_vid", "imagevideo", "image_video"]:
                instaloader_init("login_arg", *args[2:])
            elif mode in ["a", "adv", "advance", "advanced"]:
                instaloader_init(*args[2:])
            elif mode in ["u", "fu", "update", "fastupdate", "fast_update"]:
                instaloader_init("login_arg", "fast_update_arg", *args[2:])
            elif mode in ["fullupdate", "full_update"]:
                instaloader_init("login_arg", "full_update_arg", *args[2:])
            else:
                print("Invalid input for instaloader mode!")
        else:
            print(f"Invalid command: {args[0]}")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(0)  # Graceful exit on interruption

if is_windows():
    rhqArchive = Path("J:\\")
else:
    rhqArchive = Path("/path/to/unix/folder")  # Set appropriate path for Unix-based systems

if __name__ == "__main__":
    main(*sys.argv[1:])
