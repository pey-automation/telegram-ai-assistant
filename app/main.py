from fastapi import FastAPI
from app.routers import message, users, telegram

from app.routers import message, users
from app.database import engine, Base
from app import models


Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Welcome to Telegram AI Assistant"
    }


@app.get("/health")
def health():
    return {
        "server": "running",
        "database": "connected"
    }


app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    message.router,
    prefix="/messages",
    tags=["Messages"]
)

app.include_router(
    telegram.router,
    prefix="/telegram",
    tags=["Telegram"]
)
from fastapi import FastAPI

from app.routers import message, users, telegram

app = FastAPI()

app.include_router(message.router)
app.include_router(users.router)
app.include_router(telegram.router)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }