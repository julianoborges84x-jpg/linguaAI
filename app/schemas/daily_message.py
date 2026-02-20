from pydantic import BaseModel
from datetime import date


class DailyMessageOut(BaseModel):
    day: date
    reference: str
    text: str

    class Config:
        from_attributes = True
