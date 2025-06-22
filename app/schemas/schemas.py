from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
class SignupRequest(BaseModel):
    email: EmailStr
    username: str=Field(min_length=3, max_length=40)
    password: str=Field(min_length=6)
    confirm_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str 
class ChatRequest(BaseModel):
    query: str=Field(min_length=1, max_length=7000)
    conversation_id: Optional[UUID]
