from fastapi import APIRouter


router = APIRouter()


@router.post("/webhook")
def telegram_webhook(update: dict):
    return {
        "received": True,
        "update": update
    }