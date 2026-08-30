from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, User


router = APIRouter()


# =========================
# Get User Conversations
# =========================

@router.get("/")
def get_conversations(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user_id
        )
        .order_by(Conversation.id.asc())
        .all()
    )

    return conversations


# =========================
# Get Conversation By ID
# =========================

@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation