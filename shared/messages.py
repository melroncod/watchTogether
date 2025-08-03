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


class Chat(BaseModel):
    type: Literal["chat"] = "chat"
    user: str = Field(..., description="Имя отправителя")
    text: str = Field(..., description="Текст сообщения")


class ChatHistory(BaseModel):
    type: Literal["chat_history"] = "chat_history"
    messages: list[Chat]

class ClearChat(BaseModel):
    type: Literal["clear_chat"] = "clear_chat"
