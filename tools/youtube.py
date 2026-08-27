import os
import yt_dlp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
COOKIE_FILE = os.path.join(BASE_DIR, "..", "cookies", "youtube.txt")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def build_opts(use_cookies: bool = False, verbose: bool = False) -> dict:
    opts = {
        "format": (
            "bv*[vcodec^=avc1]+ba[acodec^=mp4a]/"
            "bv*+ba/"
            "b"
        ),
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title).150B [%(id)s].%(ext)s"),
        "merge_output_format": "mp4",

        "js_runtimes": {"deno": {}, "node": {}},

        "remote_components": ["ejs:github"],

        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "ignoreerrors": False,
        "verbose": verbose,

    }

    if use_cookies:
        if not os.path.isfile(COOKIE_FILE):
            raise FileNotFoundError(f"cookie file not found: {COOKIE_FILE}")
        opts["cookiefile"] = COOKIE_FILE

    return opts


def list_formats(video_url: str, use_cookies: bool = False) -> None:
    opts = build_opts(use_cookies=use_cookies, verbose=True)
    opts["listformats"] = True
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(video_url, download=False)


def download_youtube_video(video_url: str, use_cookies: bool = False) -> str | None:
    opts = build_opts(use_cookies=use_cookies)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(video_url, download=True)

        downloads = info.get("requested_downloads") or []
        if downloads:
            path = downloads[0].get("filepath")
            if path and os.path.isfile(path):
                return path

        return None


if __name__ == "__main__":
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=YWtZD6DjkZE"

    if "--list" in sys.argv:
        list_formats(url, use_cookies="--cookies" in sys.argv)
    else:
        print(download_youtube_video(url, use_cookies="--cookies" in sys.argv))
