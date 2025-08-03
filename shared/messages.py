# shared/messages.py
from typing import Literal
from pydantic import BaseModel, Field

class BaseMessage(BaseModel):
    type: str = Field(..., description="Тип сообщения")

class TimeUpdate(BaseMessage):
    type: Literal["time_update"] = "time_update"
    time: float = Field(..., description="Текущее время воспроизведения в секундах")

class Play(BaseMessage):
    type: Literal["play"] = "play"

class Pause(BaseMessage):
    type: Literal["pause"] = "pause"

class Seek(BaseMessage):
    type: Literal["seek"] = "seek"
    time: float = Field(..., description="Время для перемотки в секундах")

class Load(BaseMessage):
    type: Literal["load"] = "load"
    url: str = Field(..., description="URL или имя файла для загрузки у клиентов")
