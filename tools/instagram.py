import yt_dlp
import os
import shutil

def download_instagram_video(url):

    COOKIE_FILE = os.path.join(
        os.path.dirname(__file__),
        "../www.youtube.com_cookies.txt"
    )

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
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)
        
        if os.path.exists(filename):
            print("download complete")
            return filename
        
        return None
    