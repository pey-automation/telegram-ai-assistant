from sqlalchemy.orm import Session

from app.models import Message


def save_message(
    db: Session,
    user_id: int,
    conversation_id: int,
    text: str,
    role: str,
):
    message = Message(
        text=text,
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: int,
):
    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.id.asc())
        .all()
    )

    return messages