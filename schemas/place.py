from pydantic import BaseModel, Field


class PlaceSchema(BaseModel):
    id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    wage: int = Field(..., ge=0)
    closing_day: int = Field(..., ge=1, le=31)
    has_night_wage: bool
    is_valid: bool


class InsertPlaceSchema(BaseModel):
    user_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    wage: int = Field(..., ge=0)
    closing_day: int = Field(..., ge=1, le=31)
    has_night_wage: bool
