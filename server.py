import os
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse


app = FastAPI()

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

PUBLIC_URL = os.getenv(
    "PUBLIC_URL",
    "http://127.0.0.1:8000"
)

files = {}


@app.get("/download/{file_id}")
def download_file(file_id: str):

    data = files.get(file_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Link not found or expired"
        )

    filename = Path(data["filename"])
    expires_at = data["expires_at"]

    if time.time() > expires_at:

        files.pop(file_id, None)

        if filename.exists():
            try:
                filename.unlink()
            except Exception:
                pass

        raise HTTPException(
            status_code=410,
            detail="Link expired"
        )

    if not filename.exists():
        files.pop(file_id, None)

        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        path=filename,
        filename=filename.name,
        media_type="video/mp4"
    )


def create_download_link(filename: str, expire_seconds: int = 300):

    file_id = uuid.uuid4().hex

    files[file_id] = {
        "filename": str(Path(filename).resolve()),
        "expires_at": time.time() + expire_seconds
    }

    return f"{PUBLIC_URL}/download/{file_id}"