from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginData(BaseModel):
    email: EmailStr
    password: str

class ContactBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    extra: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactOut(ContactBase):
    id: int
    owner_id: int

    model_config = {"from_attributes": True}

class RefreshTokenRequest(BaseModel):
    refresh_token: str
