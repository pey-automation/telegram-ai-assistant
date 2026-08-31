from sqlalchemy.orm import Session

from app.models import Conversation


def get_or_create_conversation(
    db: Session,
    user_id: int,
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user_id
        )
        .order_by(Conversation.id.desc())
        .first()
    )

    if conversation is None:
        conversation = Conversation(
            user_id=user_id
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    return conversation