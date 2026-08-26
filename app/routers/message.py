from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Message, Conversation
from app.schemas import MessageCreate, MessageResponse


router = APIRouter()


# =========================
# Health Check
# =========================

@router.get("/health")
def health_check():
    return {
        "status": "ok",
    }


# =========================
# Get All Messages
# =========================

@router.get(
    "/",
    response_model=list[MessageResponse],
)
def get_messages(
    db: Session = Depends(get_db),
):
    messages = (
        db.query(Message)
        .order_by(Message.id.asc())
        .all()
    )

    return messages


# =========================
# Get Messages By Conversation
# =========================

@router.get(
    "/conversation/{conversation_id}",
    response_model=list[MessageResponse],
)
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.asc())
        .all()
    )

    return messages


# =========================
# Create Message
# =========================

@router.post(
    "/",
    response_model=MessageResponse,
)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
):
    new_message = Message(
        text=message.text,
        user_id=message.user_id,
        conversation_id=message.conversation_id,
        role=message.role,
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message