from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    media_dir: str = "media"
    ws_path: str = "/ws"
    http_media_path: str = "/media"

    class Config:
        env_prefix = "SYNC_"

settings = Settings()
