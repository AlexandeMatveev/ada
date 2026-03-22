from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from schemas.user import UserInDB, UserCreate, UserUpdate  # Исправлено: UserInDB вместо User
from services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=UserInDB)  # Исправлено
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.create(db, obj_in=user_in)


@router.get("/", response_model=List[UserInDB])  # Исправлено
def read_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),

):
    if active_only:
        return user_service.get_active(db)
    return user_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserInDB)  # Исправлено
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserInDB)  # Исправлено
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
):
    user = user_service.update(db, id=user_id, obj_in=user_in)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.delete(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/activate", response_model=UserInDB)  # Исправлено
def activate_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.toggle_active(db, user_id, True)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/deactivate", response_model=UserInDB)  # Исправлено
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.toggle_active(db, user_id, False)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user