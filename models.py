# 3.1 задание

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    age: Optional[int] = Field(None, ge=0, description="Возраст")
    is_subscribed: Optional[bool] = Field(False, description="Подписка на рассылку")

    @field_validator('age')
    def validate_age(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Age must be > 0')
        return v



