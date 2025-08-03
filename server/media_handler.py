import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from server.config import settings

router = APIRouter(prefix=settings.http_media_path)

@router.get("/list")
async def list_media():
    """
    Возвращает JSON-массив с именами файлов в папке media.
    """
    files = []
    for fn in os.listdir(settings.media_dir):
        path = os.path.join(settings.media_dir, fn)
        if os.path.isfile(path):
            files.append(fn)
    return files


@router.get("/{filename}")
async def get_media(filename: str):
    file_path = os.path.join(settings.media_dir, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4")
