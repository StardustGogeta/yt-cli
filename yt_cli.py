#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
import glob
import os
import requests
from rich.console import Console
from rich.table import Table
import shutil
import subprocess
import yt_dlp

VERSION = 0.1

class Video:
    def __init__(self, title, id, author, views, length_seconds, published):
        self.title = title
        self.id = id
        self.author = author
        self.views = views
        self.length_seconds = length_seconds
        self.published = published

    def __repr__(self):
        return f"{self.title} by {self.author}"

def show_views(views):
    if views < 10**3:
        return str(views)
    if views < 10**6:
        return f"{views / 10**3 : .1f}K"
    if views < 10**9:
        return f"{views / 10**6 : .1f}M"
    if views < 10**12:
        return f"{views / 10**9 : .1f}B"
    return f"{views / 10**12 : .1f}T"

def show_length(length_seconds):
    return str(timedelta(seconds=length_seconds))

def show_timestamp(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%B %d, %Y")

def top_videos(query):
    r = requests.get("https://inv.thepixora.com/api/v1/search",
        params = {
            "q": query,
            "type": "video"
        },
        headers = {
            "User-Agent": "Dummy"
        }
    )
    j = r.json()
    return [Video(x["title"], x["videoId"], x["author"], x["viewCount"], x["lengthSeconds"], x["published"]) for x in j]

def help_menu(args):
    print(f"\n=== YT-CLI Version {VERSION} ===")
    for x, y in commands.items():
        print(f"{x}\t{y[0]}")
    print()

def clear_cache(args):
    if input("Are you SURE you want to clear the video cache?\n" +
             f"This will delete all files under {args.cache_dir}. (y/N) ").strip().lower() in ["yes", "y"]:
        shutil.rmtree(args.cache_dir, ignore_errors=True)
        print("Removed cache directory.")
    else:
        print("Did not clear cache.")

def quit_program(args):
    exit()

commands = {
    "/h": ("Show the help menu", help_menu),
    "/clear": ("Clear the saved video cache", clear_cache),
    "/q": ("Exit program", quit_program)
}

def show_videos(videos):
    table = Table(border_style="on blue")
    table.add_column("#")
    table.add_column("Title", justify="left", max_width=50, style="bold yellow")
    table.add_column("Author", justify="center")
    table.add_column("Views", justify="center")
    table.add_column("Length", justify="center")
    table.add_column("Publish Date", justify="center")
    for i, v in enumerate(videos):
        table.add_row(
            str(i + 1),
            v.title,
            v.author,
            show_views(v.views),
            show_length(v.length_seconds),
            show_timestamp(v.published)
        )
    console = Console()
    console.print(table)

def get_selection(max_index, args):
    selection = input("> ").strip()
    if selection == "/b":
        return None
    elif selection in commands:
        # Execute special command if provided
        commands[selection][1](args)
    else:
        try:
            sel_index = int(selection)
            if sel_index < 1 or sel_index > max_index:
                print(f"Please enter a valid integer in the range 1 to {max_index}.")
                return get_selection(max_index, args)
            return sel_index
        except:
            print("Could not parse integer. Try again.")
            return get_selection(max_index, args)

if __name__ == "__main__":
    # Allow flags for some configuration settings
    parser = argparse.ArgumentParser("yt-cli", "CLI browser for YouTube")
    parser.add_argument("--cache-dir", default="/tmp/yt_cli", help="path to store downloaded videos")
    parser.add_argument("-f", "--format", default="(bv+ba/best)[filesize<100M]", help="quality for downloaded videos (yt-dlp format)")
    parser.add_argument("-S", "--format-sort", default="", help="sort method for quality of downloaded videos (yt-dlp format-sort)")
    parser.add_argument("--mpv", default="mpv", help="path to MPV executable")

    # Allow passing through extra args to MPV
    args, extra_args = parser.parse_known_args()
    if extra_args and extra_args[0] != "--":
        print(f"Unrecognized argument: {extra_args[0]}")
        exit(1)

    print("Welcome to YT-CLI!")
    try:
        while True:
            print("Enter a search term below, or use /h for a list of commands.")
            userinput = input("> ").strip()
            if userinput in commands:
                # Execute special command if provided
                commands[userinput][1](args)
            elif userinput:
                # Otherwise, do a search
                vids = top_videos(userinput)
                show_videos(vids)
                print("Enter the number of the video you want to play, or /b to go back:")
                sel = get_selection(len(vids), args)
                if sel is not None:
                    v = vids[sel - 1]
                    path_no_ext = f"{args.cache_dir}/{v.id}"
                    paths = glob.glob(f"{path_no_ext}.*")
                    if not paths:
                        print(f"Downloading video {v.title}...")
                        os.makedirs(args.cache_dir, exist_ok=True)
                        yt_dlp_opts = {
                            "format": args.format,
                            "format_sort": [args.format_sort],
                            "remote_components": ["ejs:github"],
                            "outtmpl": path_no_ext,
                        }
                        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
                            try:
                                ydl.download(f"https://www.youtube.com/watch?v={v.id}")
                            except yt_dlp.utils.DownloadError:
                                print("Error: Could not download video. " +
                                      "Please note that if the target video is labeled as \"for kids\", then deno must be installed.")
                    print(f"Searching for {path_no_ext}...")
                    paths = glob.glob(f"{path_no_ext}.*")
                    if not paths:
                        print("Error: Failed to locate downloaded video!")
                    else:
                        path = paths[0]
                        # Play video
                        subprocess.run([
                            args.mpv,
                            f"--title={v.title}",
                            "--vo=wlshm,x11,gpu,tct",
                            "--vo-tct-buffering=frame",
                            "--profile=sw-fast",
                            "--volume=70",
                            r"--geometry=80%x80%",
                            "--keep-open",
                            *extra_args[1:],
                            path
                        ])
    except KeyboardInterrupt, EOFError:
        exit()

