# yt-cli

Play YouTube videos from the CLI, designed to support extremely low-end devices.

Tested on Windows 10, WSL, and Ubuntu 26.04.

## Requirements

Use your Python package manager of choice to install the required packages from `requirements.txt`.

In addition, make sure the following packages are present on your system:
* `python3` (to run the script)
* `ffmpeg` (for audio/video processing)
* `mpv` (for video playback)
* `yt-dlp` (for YouTube scraping)

To be able to download material that is marked for kids, you also must install `deno`.
You may do this with the following command:
```bash
curl -fsSL https://deno.land/install.sh | sh
```

## How to Run

Once the prerequisites are installed, simply run `yt_cli.py` and start searching for videos.

After making a search, a sorted table of the top results will appear. Then, enter the row number of the video you wish to download/play and the rest will proceed automatically. Use the video controls or type `q` to exit playback.

Video quality can be dictated using the `-f`/`--format` and `-S`/`--format-sort` arguments, which are aliases for the same arguments in [yt-dlp](https://github.com/yt-dlp/yt-dlp#video-format-options). The default is to fetch the highest-quality video/audio combination available that is smaller than 100 MB.

Note that videos are stored in a cache in `/tmp/yt_cli` by default, allowing the download to be skipped if the same video is watched more than once. To change the cache location, pass the `--cache-dir` argument at launch. To clear the cache, enter `/clear` while in the program.

If you need to change the `mpv` executable path, pass the argument `--mpv`. The `mpv` settings are set to defaults that should work well for most platforms, but in case you do need to change any of the settings for `mpv` itself, any arguments after `--` are passed through directly.
