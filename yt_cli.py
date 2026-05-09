from datetime import datetime, timedelta
import glob
import os
import requests
from rich.console import Console
from rich.table import Table
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

def help_menu():
    print(f"\n=== YT-CLI Version {VERSION} ===")
    for x, y in commands.items():
        print(f"{x}\t{y[0]}")
    print()

def quit_program():
    exit()

commands = {
    "/h": ("Show the help menu", help_menu),
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

def get_selection(max_index):
    selection = input("> ").strip()
    if selection == "/b":
        return None
    elif selection in commands:
        # Execute special command if provided
        commands[selection][1]()
    else:
        try:
            sel_index = int(selection)
            if sel_index < 1 or sel_index > max_index:
                print(f"Please enter a valid integer in the range 1 to {max_index}.")
                return get_selection(max_index)
            return sel_index
        except:
            print("Could not parse integer. Try again.")
            return get_selection(max_index)

CACHE_DIR = "/tmp/yt_cli"

if __name__ == "__main__":
    print("Welcome to YT-CLI!")
    print("Enter a search term below, or use /h for a list of commands.")
    while True:
        userinput = input("> ").strip()
        if userinput in commands:
            # Execute special command if provided
            commands[userinput][1]()
        elif userinput:
            # Otherwise, do a search
            vids = top_videos(userinput)
            show_videos(vids)
            print("Enter the number of the video you want to play, or /b to go back:")
            sel = get_selection(len(vids))
            if sel is not None:
                v = vids[sel - 1]
                path_no_ext = f"{CACHE_DIR}/{v.id}"
                paths = glob.glob(f"{path_no_ext}.*")
                if not paths:
                    print(f"Downloading video {v.title}...")
                    os.makedirs(CACHE_DIR, exist_ok=True)
                    yt_dlp_opts = {
                        "format": "bestvideo+bestaudio/best",
                        "outtmpl": path_no_ext,
                    }
                    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
                        ydl.download(f"https://www.youtube.com/watch?v={v.id}")
                print(f"Searching for {path_no_ext}...")
                paths = glob.glob(f"{path_no_ext}.*")
                if not paths:
                    print("Error: Failed to download video!")
                else:
                    path = paths[0]
                    # Play video
                    subprocess.run(["mpv", "--vo=wlshm,x11,tct", r"--autofit-larger=50%x50%", path])

