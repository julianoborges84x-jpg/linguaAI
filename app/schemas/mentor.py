from pydantic import BaseModel, Field
from typing import Literal, List
from datetime import date


class MentorChatIn(BaseModel):
    message: str = Field(min_length=1)
    feature: Literal["writing", "speaking", "dialect", "fillers"]


class MentorChatOut(BaseModel):
    message: str
    reply: str
    correction: str | None = None
    explanation: str | None = None
    suggestion: str | None = None
    detected_errors: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    micro_intervention: str | None = None
    micro_drill_questions: list[str] = Field(default_factory=list)
    fallback_reason: str | None = None
    ads: List[str] | None = None


class MentorDetectIn(BaseModel):
    text: str = Field(min_length=1)


class MentorDetectOut(BaseModel):
    iso_code: str
    name: str


class VoiceMentorOut(BaseModel):
    id: str
    name: str
    avatar: str
    description: str
    speaking_style: str
    pedagogical_focus: str


class VoiceChatIn(BaseModel):
    mentor_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class VoiceUsageOut(BaseModel):
    plan: Literal["FREE", "PRO"]
    used: int
    limit: int | None = None
    remaining: int | None = None
    blocked: bool = False
    reset_on: date | None = None


class VoiceChatOut(BaseModel):
    mentor_id: str
    mentor_name: str
    transcript: str
    reply: str
    tts_text: str
    audio_available: bool = True
    voice_usage: VoiceUsageOut
