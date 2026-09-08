from telegram import User as TelegramUser
from sqlalchemy.orm import Session

from app.models import User


def get_or_create_user(
    db: Session,
    telegram_user: TelegramUser,
):
    user = (
        db.query(User)
        .filter(
            User.telegram_user_id == telegram_user.id
        )
        .first()
    )

    if user is None:
        user = User(
            name=telegram_user.first_name or "Telegram User",
            age=0,
            telegram_user_id=telegram_user.id,
            username=telegram_user.username,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    else:
        user.username = telegram_user.username

        if telegram_user.first_name:
            user.name = telegram_user.first_name

        db.commit()
        db.refresh(user)

    return user


def get_user_info(
    db: Session,
    user_id: int,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )