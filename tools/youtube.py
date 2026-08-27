import os
import yt_dlp
import shutil

DOWNLOAD_DIR = os.path.abspath("downloads")

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)

def download_youtube_video(video_url):  

    ydl_opts = {
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",

        "outtmpl": "downloads/%(title)s.%(ext)s",

        "merge_output_format": "mp4",

        "cookiefile": "cookies/youtube.txt",

        "js_runtimes": {
            "node": {}
        },

        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            video_url,
            download=True
        )

        filename = ydl.prepare_filename(info)

        filename = (
            os.path.splitext(filename)[0]
            + ".mp4"
        )

        if os.path.isfile(filename):
            return filename

        return None