from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    email: EmailStr
    username: str=Field(min_length=3, max_length=40)
    password: str=Field(min_length=6)
    confirm_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str 
class ChatRequest(BaseModel):
    query: str
