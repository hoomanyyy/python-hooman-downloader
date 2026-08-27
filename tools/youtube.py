import os
import yt_dlp


DOWNLOAD_DIR = os.path.abspath("downloads")

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True
)


def download_youtube_video(video_url):

    ffmpeg_path = (
        r"C:\Users\hooman\AppData\Local\Temp"
        r"\ffmpeg_extract\ffmpeg-9.0.1-essentials_build\bin"
    )

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",

        "outtmpl": os.path.join(
            DOWNLOAD_DIR,
            "%(title)s.%(ext)s"
        ),

        "ffmpeg_location": ffmpeg_path,

        "noplaylist": True,
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