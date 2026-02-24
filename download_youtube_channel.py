"""
Download all videos from a YouTube channel to a local folder.
Requires: pip install yt-dlp
"""

import argparse
import os
import sys

try:
    import yt_dlp
except ImportError:
    print("yt-dlp is not installed. Install it with:\n  pip install yt-dlp")
    sys.exit(1)


def download_channel(channel_url: str, output_folder: str) -> None:
    os.makedirs(output_folder, exist_ok=True)

    ydl_opts = {
        # Save as: OutputFolder/VideoTitle.mp4
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        # Best video+audio merged into mp4
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        # Explicit path to ffmpeg so yt-dlp can find it
        "ffmpeg_location": r"C:\Program Files\ShareX",
        # Skip already-downloaded videos
        "download_archive": os.path.join(output_folder, ".downloaded_archive.txt"),
        # Retry on errors and continue past unavailable videos
        "ignoreerrors": True,
        "retries": 5,
        "fragment_retries": 5,
        # No thumbnails, no metadata embedding — just the MP4
        "writethumbnail": False,
        "postprocessors": [],
        # Progress display
        "progress_hooks": [_progress_hook],
    }

    print(f"Downloading channel: {channel_url}")
    print(f"Saving to:           {output_folder}\n")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([channel_url])

    print("\nDone!")


def _progress_hook(d: dict) -> None:
    if d["status"] == "downloading":
        pct = d.get("_percent_str", "?%")
        speed = d.get("_speed_str", "?")
        eta = d.get("_eta_str", "?")
        print(f"\r  {pct}  {speed}  ETA {eta}   ", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\n  Finished: {os.path.basename(d['filename'])}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download all videos from a YouTube channel."
    )
    parser.add_argument("channel_url", help="URL of the YouTube channel (e.g. https://www.youtube.com/@ChannelName)")
    parser.add_argument("output_folder", help="Local folder to save videos into")
    args = parser.parse_args()

    download_channel(args.channel_url, args.output_folder)
