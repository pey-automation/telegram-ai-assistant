from pydantic import BaseModel, Field
from typing import Optional


class Message(BaseModel):
    text: str = Field(..., min_length=3, max_length=100)
    age: int = Field(..., ge=0, le=120)


class MessageResponse(BaseModel):
    success: bool
    received_text: str


class UserResponse(BaseModel):
    id: int
    name: str
    age: int 



class UserCreate(BaseModel):
    name: str
    age: int

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=0, le=120)
class MessageCreate(BaseModel):
    text: str
    user_id: int


class MessageResponse(BaseModel):
    id: int
    text: str
    user_id: int