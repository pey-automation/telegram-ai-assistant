from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
)


router = APIRouter()


# =========================
# Dependency Example
# =========================

def common_check():
    return "checked"


# =========================
# Search User
# =========================

@router.get("/search")
def search_user(
    name: Optional[str] = None,
    age: Optional[int] = None,
):
    return {
        "name": name,
        "age": age,
    }


# =========================
# Dependency Example
# =========================

@router.get("/check")
def check_user(
    status: str = Depends(common_check),
):
    return {
        "status": status,
    }


# =========================
# Get All Users
# =========================

@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .all()
    )

    return users


# =========================
# Get User By ID
# =========================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# =========================
# Create User
# =========================

@router.post(
    "/",
    response_model=UserResponse,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    # Check duplicate Telegram user
    if user_data.telegram_user_id is not None:

        existing_user = (
            db.query(User)
            .filter(
                User.telegram_user_id
                == user_data.telegram_user_id
            )
            .first()
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=400,
                detail="Telegram user already exists",
            )

    new_user = User(
        name=user_data.name,
        age=user_data.age,
        telegram_user_id=user_data.telegram_user_id,
        username=user_data.username,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# Update User
# =========================

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.age is not None:
        user.age = user_data.age

    if user_data.username is not None:
        user.username = user_data.username

    db.commit()
    db.refresh(user)

    return user


# =========================
# Delete User
# =========================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
    }