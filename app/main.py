from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from models.user import User
from core.config import settings
from core.database import init_db
from api.api_v1.api import api_router
from core.security import get_current_user
from core.rabbitmq import rabbit_client

# Инициализация базы данных (синхронно)
init_db()

# Определяем обработчики событий (до их использования)
async def handle_order_created(data: dict):
    print(f"Получен заказ: {data}")
    # Здесь можно отправить email, уведомление и т.д.

async def start_consumers():
    await rabbit_client.consume(
        routing_key="order.created",
        queue_name="order_created_queue",
        callback=handle_order_created
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск при старте
    await rabbit_client.connect()
    asyncio.create_task(start_consumers())
    yield
    # Остановка при выключении
    await rabbit_client.connection.close()

# Создаём приложение с lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan          # <-- ЭТО БЫЛО ПРОПУЩЕНО
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
    return {"message": f"Hello {current_user.username}"}

