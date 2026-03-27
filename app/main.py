from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models.user import User
from core.config import settings
from core.database import init_db
from api.api_v1.api import api_router
from core.security import get_current_user
# Инициализация базы данных
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def read_root():
    return {"message": "FastAPI Clean Architecture", "version": settings.APP_VERSION}

@app.get("/protected")
def protected_endpoint(current_user: User = Depends(get_current_user)):
    """
    Только для аутентифицированных пользователей
    """
    return {"message": f"Hello {current_user.username}"}


@app.get("/health")
def health():
    from core.database import engine
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}
