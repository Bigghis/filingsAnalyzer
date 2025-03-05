from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    disabled: Optional[bool] = None
    full_name: Optional[str] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str 