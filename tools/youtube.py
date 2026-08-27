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
        "format": "bestvideo+bestaudio/best",
        "ffmpeg_location": shutil.which("ffmpeg"),
        "outtmpl": "downloads/%(title)s.%(ext)s",
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