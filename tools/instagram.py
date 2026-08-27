import yt_dlp
import os
import shutil

def download_instagram_video(url):

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "ffmpeg_location": shutil.which("ffmpeg"),
        "outtmpl": "downloads/%(title)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)
        
        if os.path.exists(filename):
            print("download complete")
            return filename
        
        return None
    