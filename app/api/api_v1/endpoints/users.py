from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from schemas.user import User, UserCreate, UserUpdate
from services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=User)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.create(db, obj_in=user_in)


