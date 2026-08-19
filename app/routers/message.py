from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Message, User
from app.schemas import MessageCreate, MessageResponse


router = APIRouter()


# Health Check
@router.get("/health")
def health_check():
    return {
        "status": "ok"
    }


# Create Message
@router.post("/", response_model=MessageResponse)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == message.user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    new_message = Message(
        text=message.text,
        user_id=message.user_id
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


# Get All Messages
@router.get("/", response_model=list[MessageResponse])
def get_messages(
    db: Session = Depends(get_db)
):
    messages = (
        db.query(Message)
        .all()
    )

    return messages


# Get Message By ID
@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    message = (
        db.query(Message)
        .filter(Message.id == message_id)
        .first()
    )

    if message is None:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    return message


# Delete Message
@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    message = (
        db.query(Message)
        .filter(Message.id == message_id)
        .first()
    )

    if message is None:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    db.delete(message)
    db.commit()

    return {
        "message": "Message deleted successfully"
    }