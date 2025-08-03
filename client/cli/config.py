from pydantic_settings import BaseSettings

class CLISettings(BaseSettings):
    ws_host: str = "ws://localhost:8000/ws"
    http_host: str = "http://localhost:8000/media/"

settings = CLISettings()
