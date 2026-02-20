from pydantic import BaseModel, Field
from typing import Literal, List


class MentorChatIn(BaseModel):
    message: str = Field(min_length=1)
    feature: Literal["writing", "speaking", "dialect", "fillers"]


class MentorChatOut(BaseModel):
    reply: str
    ads: List[str] | None = None


class MentorDetectIn(BaseModel):
    text: str = Field(min_length=1)


class MentorDetectOut(BaseModel):
    iso_code: str
    name: str
