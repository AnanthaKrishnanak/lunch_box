from datetime import date

from pydantic import BaseModel, ConfigDict


class HolidayBase(BaseModel):
    date: date
    name: str

    model_config = ConfigDict(from_attributes=True)
