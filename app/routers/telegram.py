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
from app.services.ai_service import generate_ai_response
from app.services.user_service import get_or_create_user
from app.services.conversation_service import get_or_create_conversation
from app.services.message_service import (
    save_message,
    get_conversation_messages,
)


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


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

    # 1. Find/Create User
    db: Session = SessionLocal()

    try:
        user = get_or_create_user(
            db,
            telegram_user,
        )
    finally:
        db.close()

    # 2. Find/Create Conversation
    db: Session = SessionLocal()

    try:
        get_or_create_conversation(
            db,
            user.id,
        )
    finally:
        db.close()

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
    db: Session = SessionLocal()

    try:
        user = get_or_create_user(
            db,
            telegram_user,
        )
    finally:
        db.close()

    # 2. Find/Create Conversation
    db: Session = SessionLocal()

    try:
        conversation = get_or_create_conversation(
            db,
            user.id,
        )
    finally:
        db.close()

    # 3. Save User Message
    db: Session = SessionLocal()

    try:
        save_message(
            db=db,
            user_id=user.id,
            conversation_id=conversation.id,
            text=text,
            role="user",
        )
    finally:
        db.close()

    # 4. Get Conversation History
    db: Session = SessionLocal()

    try:
        messages = get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
        )
    finally:
        db.close()

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
    db: Session = SessionLocal()

    try:
        save_message(
            db=db,
            user_id=user.id,
            conversation_id=conversation.id,
            text=ai_response,
            role="assistant",
        )
    finally:
        db.close()

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