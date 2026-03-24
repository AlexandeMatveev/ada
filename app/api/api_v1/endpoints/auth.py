from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.user import UserCreate
from schemas.token import LoginRequest
from services.auth_service import auth_service
from core.security import create_access_token, get_current_user

router = APIRouter( tags=["auth"])

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    user = auth_service.register(db, data)
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.login(db, data.email, data.password)
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}

@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user