import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import User, Message


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# =========================
# /start
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    await update.message.reply_text(
        "سلام پیمان 👋\n"
        "بات روشنه و آماده دریافت پیامه."
    )


# =========================
# Receive Telegram Message
# =========================

async def echo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    if not update.message.text:
        return

    telegram_user = update.effective_user

    if telegram_user is None:
        return

    db = SessionLocal()

    try:
        telegram_user_id = telegram_user.id

        username = telegram_user.username

        first_name = telegram_user.first_name

        # =========================
        # Find User
        # =========================

        user = (
            db.query(User)
            .filter(
                User.telegram_user_id
                == telegram_user_id
            )
            .first()
        )

        # =========================
        # Create User
        # =========================

        if user is None:

            user = User(
                telegram_user_id=telegram_user_id,
                username=username,
                name=first_name or "Telegram User",
                age=0,
            )

            db.add(user)

            db.flush()

        # =========================
        # Update User Info
        # =========================

        else:

            user.username = username

            if first_name:
                user.name = first_name

        # =========================
        # Save Message
        # =========================

        new_message = Message(
            text=update.message.text,
            user_id=user.id,
        )

        db.add(new_message)

        db.commit()

        db.refresh(new_message)

        message_id = new_message.id

    except SQLAlchemyError:

        db.rollback()

        await update.message.reply_text(
            "متأسفانه هنگام ذخیره پیام مشکلی پیش اومد."
        )

        return

    finally:

        db.close()

    # =========================
    # Telegram Response
    # =========================

    await update.message.reply_text(
        f"پیامت دریافت و ذخیره شد ✅\n\n"
        f"Message ID: {message_id}\n"
        f"User ID: {telegram_user_id}\n\n"
        f"پیام:\n"
        f"{update.message.text}"
    )


# =========================
# Create Telegram Bot
# =========================

def create_bot():

    if not BOT_TOKEN:

        raise ValueError(
            "TELEGRAM_BOT_TOKEN در فایل .env پیدا نشد."
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            echo,
        )
    )

    return application