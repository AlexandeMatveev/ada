from sqlalchemy.orm import Session
from fastapi import HTTPException
from core.security import verify_password, get_password_hash, create_access_token
from models.user import User
from schemas.user import UserCreate


class AuthService:
    def register(self, db: Session, data: UserCreate):
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(400, "Email already registered")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(401, "Invalid credentials")
        return user


auth_service = AuthService()