from datetime import time

from pydantic import BaseModel, Field


class TemplateSchema(BaseModel):
    id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)
    place_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=8)
    start_time: time
    end_time: time
    break_time: time
    place: str = Field(..., min_length=1)


class InsertTemplateSchema(BaseModel):
    user_id: int = Field(..., ge=1)
    place_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=8)
    start_time: str
    end_time: str
    break_time: str
