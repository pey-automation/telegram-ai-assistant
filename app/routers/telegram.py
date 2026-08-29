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
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Conversation, Message
from app.services.ai_service import generate_ai_response


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# =========================
# User
# =========================

def get_or_create_user(telegram_user):
    db: Session = SessionLocal()

    try:
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

    finally:
        db.close()


# =========================
# Conversation
# =========================

def get_or_create_conversation(user_id: int):
    db: Session = SessionLocal()

    try:
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

    finally:
        db.close()


# =========================
# Save Message
# =========================

def save_message(
    user_id: int,
    conversation_id: int,
    text: str,
    role: str,
):
    db: Session = SessionLocal()

    try:
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

    finally:
        db.close()


# =========================
# Get Conversation History
# =========================

def get_conversation_messages(
    conversation_id: int,
):
    db: Session = SessionLocal()

    try:
        messages = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.id.asc())
            .all()
        )

        return messages

    finally:
        db.close()


# =========================
# Format History for AI
# =========================

def format_conversation_history(messages):
    return [
        {
            "role": message.role,
            "content": message.text,
        }
        for message in messages
    ]


# =========================
# /start
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if (
        update.message is None
        or update.effective_user is None
    ):
        return

    telegram_user = update.effective_user

    user = get_or_create_user(telegram_user)

    get_or_create_conversation(user.id)

    await update.message.reply_text(
        "سلام 👋\n"
        "من آماده‌ام. پیامت رو بفرست."
    )


# =========================
# Handle Messages
# =========================

async def echo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if (
        update.message is None
        or update.message.text is None
        or update.effective_user is None
    ):
        return

    text = update.message.text

    telegram_user = update.effective_user

    # 1. Find/Create User
    user = get_or_create_user(telegram_user)

    # 2. Find/Create Conversation
    conversation = get_or_create_conversation(user.id)

    # 3. Save User Message
    save_message(
        user_id=user.id,
        conversation_id=conversation.id,
        text=text,
        role="user",
    )

    # 4. Get Conversation History
    messages = get_conversation_messages(
        conversation.id
    )

    # 5. Format History for AI
    history = format_conversation_history(
        messages
    )

    # 6. Generate AI Response
    try:
        ai_response = generate_ai_response(
            history
        )

    except Exception as error:
        print("AI ERROR:", error)

        await update.message.reply_text(
            "متأسفانه در ارتباط با سرویس هوش مصنوعی مشکلی پیش اومد."
        )

        return

    # 7. Save AI Response
    save_message(
        user_id=user.id,
        conversation_id=conversation.id,
        text=ai_response,
        role="assistant",
    )

    # 8. Send AI Response to Telegram
    await update.message.reply_text(
        ai_response
    )


# =========================
# Create Bot
# =========================

def create_bot():
    if not BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN not found in .env"
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