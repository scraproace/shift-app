from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id: int = Field(..., ge=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    goal_amount: int = Field(..., ge=0)
    is_valid: bool


class InsertUserSchema(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UpdateUserSchema(BaseModel):
    id: int = Field(..., ge=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    goal_amount: int = Field(..., ge=0)
