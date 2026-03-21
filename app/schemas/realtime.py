from datetime import datetime
from pydantic import BaseModel, Field


class RealtimeSessionStartIn(BaseModel):
    mentor_id: str = Field(min_length=1)
    mode: str = Field(default="voice_video")


class RealtimeIceServerOut(BaseModel):
    urls: list[str]
    username: str | None = None
    credential: str | None = None


class RealtimeSessionStartOut(BaseModel):
    session_id: str
    status: str
    created_at: datetime
    expires_at: datetime
    signaling_path: str
    ice_servers: list[RealtimeIceServerOut]
    beta: bool = True


class RealtimeSessionSignalIn(BaseModel):
    signal_type: str = Field(min_length=1, description="offer|answer|ice")
    payload: dict = Field(default_factory=dict)


class RealtimeSessionSignalOut(BaseModel):
    session_id: str
    accepted: bool
    status: str


class RealtimeSessionStopOut(BaseModel):
    session_id: str
    status: str
    ended_at: datetime
