from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from core.database import get_db  # <-- прямой импорт
from schemas.user import User, UserCreate
from core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user
)
from crud.user import crud_user
from models.user import User as UserModel

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User)
def register_user(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    existing_user = crud_user.get_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    existing_username = crud_user.get_by_username(db, username=user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="User with this username already exists")

    hashed_password = get_password_hash(user_data.password)

    db_user = UserModel(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,

    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login")
def login_user(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("access_token", access_token, httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
def get_me(
        current_user: UserModel = Depends(get_current_user)
):
    return current_user