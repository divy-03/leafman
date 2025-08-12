# app/schemas/user_schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    department_id: Optional[int] = None

class UserCreate(UserBase):
    password: str
    join_date: date
    role: str = 'Employee'

class UserResponse(UserBase):
    user_id: int
    join_date: date
    role: str

    class Config:
        from_attributes = True