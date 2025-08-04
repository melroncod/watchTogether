import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from server.config import settings

router = APIRouter(prefix=settings.http_media_path)

@router.get("/list")
async def list_media():
    """
    Возвращает список файлов в папке media.
    """
    try:
        files = [
            fn for fn in os.listdir(settings.media_dir)
            if os.path.isfile(os.path.join(settings.media_dir, fn))
        ]
    except FileNotFoundError:
        files = []
    return files

@router.get("/{filename}")
async def get_media(filename: str):
    """
    Отдаёт файл по имени из media_dir.
    """
    file_path = os.path.join(settings.media_dir, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4")
