from pydantic import BaseModel


class ReservationResponse(BaseModel):
    message: str
