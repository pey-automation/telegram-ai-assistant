from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class TelegramMessage(BaseModel):
    message: dict


@router.post("/webhook")
def telegram_webhook(data: TelegramMessage):
    return {
        "message": data.message
    }