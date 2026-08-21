from fastapi import FastAPI

from app.database import Base, engine
from app import models

from app.routers import users
from app.routers import message


# =========================
# Database
# =========================

Base.metadata.create_all(
    bind=engine
)


# =========================
# FastAPI
# =========================

app = FastAPI(
    title="Telegram AI Assistant",
    description="Backend for Telegram AI Automation",
    version="1.0.0",
)


# =========================
# Root
# =========================

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Welcome to Telegram AI Assistant",
    }


# =========================
# Health
# =========================

@app.get("/health")
def health():
    return {
        "server": "running",
        "database": "connected",
    }


# =========================
# Routers
# =========================

app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

app.include_router(
    message.router,
    prefix="/messages",
    tags=["Messages"],
)