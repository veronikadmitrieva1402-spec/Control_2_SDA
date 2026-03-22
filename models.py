# 3.1

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re

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

#5.4

class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")

    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Accept-Language header cannot be empty')
        
        allowed_pattern = r'^[a-zA-Z\-;,=*0-9. ]+$'
        if not re.match(allowed_pattern, v):
            raise ValueError('Invalid Accept-Language format')
        
        parts = [p.strip() for p in v.split(',')]
        for part in parts:
            if part == '*':
                continue
            
            if ';' in part:
                lang_part, q_part = part.split(';', 1)
                lang_part = lang_part.strip()
                q_part = q_part.strip()
                
                if not re.match(r'^[a-zA-Z]{2}(-[a-zA-Z]{2})?$', lang_part):
                    raise ValueError(f'Invalid language code: {lang_part}')
                
                if not re.match(r'^q=0(\.\d+)?$|^q=1(\.0+)?$', q_part):
                    raise ValueError(f'Invalid quality value: {q_part}')
            else:
                if not re.match(r'^[a-zA-Z]{2}(-[a-zA-Z]{2})?$', part):
                    raise ValueError(f'Invalid language code: {part}')
        
        return v
    
    class Config:
        populate_by_name = True


