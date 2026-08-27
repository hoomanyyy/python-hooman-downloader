import os
import yt_dlp

DOWNLOAD_DIR = os.path.abspath("downloads")

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


def download_youtube_video(video_url):

    COOKIE_FILE = os.path.join(
        os.path.dirname(__file__),
        "../cookies/youtube.txt"
    )

    print("COOKIE:", COOKIE_FILE)
    print("EXISTS:", os.path.exists(COOKIE_FILE))

    ydl_opts = {
        "format": "best",

        "outtmpl": "downloads/%(title)s.%(ext)s",

        "cookiefile": COOKIE_FILE,

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