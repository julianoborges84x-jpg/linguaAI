from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    correction: str
    explanation: str
    corrected_text: str


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    corrected: str
    explanation: str
    created_at: datetime


class VocabularyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    word: str
    definition: str
    example: str


class ProgressOut(BaseModel):
    streak: int
    hours_spoken: float
    words_learned: int


class ProgressUpdate(BaseModel):
    streak: int | None = None
    hours_spoken: float | None = None
    words_learned: int | None = None
