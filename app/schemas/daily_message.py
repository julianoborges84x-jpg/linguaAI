from datetime import date
from pydantic import BaseModel, ConfigDict


class DailyMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    day: date
    reference: str
    text: str
