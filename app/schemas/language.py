from pydantic import BaseModel, ConfigDict


class LanguageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iso_code: str
    name: str
    region: str
    family: str
