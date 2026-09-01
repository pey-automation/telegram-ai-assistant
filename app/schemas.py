from typing import Optional

from pydantic import BaseModel, Field


# =========================
# User Schemas
# =========================

class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    age: int = Field(
        ...,
        ge=0,
        le=120,
    )

    telegram_user_id: Optional[int] = None

    username: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=120,
    )

    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    telegram_user_id: Optional[int] = None
    username: Optional[str] = None
    name: str
    age: int

    class Config:
        from_attributes = True


# =========================
# Conversation Schemas
# =========================

class ConversationResponse(BaseModel):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# =========================
# Message Schemas
# =========================

class MessageCreate(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )

    user_id: int

    conversation_id: Optional[int] = None

    role: str = "user"


class MessageResponse(BaseModel):
    id: int
    text: str
    user_id: int
    conversation_id: Optional[int] = None
    role: str

    class Config:
        from_attributes = True


# =========================
# Telegram Schema
# =========================

class TelegramMessage(BaseModel):
    message: dict