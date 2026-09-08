import logging
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
from app.services.ai_service import (
    generate_ai_response,
    format_conversation_history,
)
from app.services.user_service import get_or_create_user
from app.services.conversation_service import get_or_create_conversation
from app.services.message_service import (
    save_message,
    get_conversation_messages,
)

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (
        update.message is None
        or update.effective_user is None
    ):
        return

    telegram_user = update.effective_user

    try:
        db: Session = SessionLocal()
        try:
            user = get_or_create_user(
                db,
                telegram_user,
            )
        finally:
            db.close()

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

        logger.info(
            "User started bot: telegram_user_id=%s",
            telegram_user.id,
        )

    except Exception:
        logger.exception(
            "Error in /start: telegram_user_id=%s",
            telegram_user.id,
        )

        await update.message.reply_text(
            "متأسفانه مشکلی پیش اومد. لطفاً دوباره تلاش کن."
        )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (
        update.message is None
        or update.message.text is None
        or update.effective_user is None
    ):
        return

    text = update.message.text
    telegram_user = update.effective_user

    try:
        # 1. Get or create user
        db: Session = SessionLocal()
        try:
            user = get_or_create_user(
                db,
                telegram_user,
            )
        finally:
            db.close()

        # 2. Get or create conversation
        db: Session = SessionLocal()
        try:
            conversation = get_or_create_conversation(
                db,
                user.id,
            )
        finally:
            db.close()

        # 3. Save user message
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

        # 4. Get conversation history
        db: Session = SessionLocal()
        try:
            messages = get_conversation_messages(
                db=db,
                conversation_id=conversation.id,
            )
        finally:
            db.close()

        history = format_conversation_history(
            messages
        )

        # 5. Generate AI response
        try:
            ai_response = generate_ai_response(
                history=history,
                user_id=user.id,
            )

        except Exception:
            logger.exception(
                "AI service error: telegram_user_id=%s conversation_id=%s",
                telegram_user.id,
                conversation.id,
            )

            await update.message.reply_text(
                "متأسفانه در ارتباط با سرویس هوش مصنوعی مشکلی پیش اومد."
            )
            return

        # 6. Save assistant message
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

        # 7. Send response to Telegram
        await update.message.reply_text(
            ai_response
        )

        logger.info(
            "Message processed successfully: telegram_user_id=%s conversation_id=%s",
            telegram_user.id,
            conversation.id,
        )

    except Exception:
        logger.exception(
            "Unexpected error while processing message: telegram_user_id=%s",
            telegram_user.id,
        )

        await update.message.reply_text(
            "متأسفانه مشکلی در پردازش پیام پیش اومد. لطفاً دوباره تلاش کن."
        )


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