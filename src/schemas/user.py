from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    full_name: str | None = None
    age: int | None = Field(None, ge=10, le=120)
    weight: float | None = Field(None, gt=0, le=500)
    height: float | None = Field(None, gt=0, le=300)
    gender: str | None = Field(None, pattern=r"^(male|female|other)$")


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = None
    age: int | None = Field(None, ge=10, le=120)
    weight: float | None = Field(None, gt=0, le=500)
    height: float | None = Field(None, gt=0, le=300)
    gender: str | None = Field(None, pattern=r"^(male|female|other)$")
    password: str | None = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
