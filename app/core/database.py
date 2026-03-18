from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from core.config import settings

# Используем URL из конфиг
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    from models import user, item
    Base.metadata.create_all(bind=engine)
