from datetime import datetime, time

from pydantic import BaseModel, Field


class ShiftSchema(BaseModel):
    id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)
    place_id: int = Field(..., ge=1)
    start_datetime: datetime
    end_datetime: datetime
    break_time: time
    place: str = Field(..., min_length=1)
    wage: int = Field(..., ge=0)
    has_night_wage: bool
    closing_day: int = Field(..., ge=1, le=31)
    amount: int = Field(..., ge=0)


class InsertShiftSchema(BaseModel):
    user_id: int = Field(..., ge=1)
    place_id: int = Field(..., ge=1)
    start_datetime: str
    end_datetime: str
    break_time: str
    is_update: bool = Field(False, exclude=True)
