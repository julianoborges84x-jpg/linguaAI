from pydantic import BaseModel


class LanguageOut(BaseModel):
    iso_code: str
    name: str
    region: str
    family: str

    class Config:
        from_attributes = True
