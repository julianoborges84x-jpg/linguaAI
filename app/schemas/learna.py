from datetime import datetime

from pydantic import BaseModel


class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    correction: str
    explanation: str
    corrected_text: str


class TopicOut(BaseModel):
    id: int
    name: str
    category: str

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: int
    message: str
    corrected: str
    explanation: str
    created_at: datetime

    class Config:
        from_attributes = True


class VocabularyOut(BaseModel):
    id: int
    word: str
    definition: str
    example: str

    class Config:
        from_attributes = True


class ProgressOut(BaseModel):
    streak: int
    hours_spoken: float
    words_learned: int


class ProgressUpdate(BaseModel):
    streak: int | None = None
    hours_spoken: float | None = None
    words_learned: int | None = None
