from fastapi import APIRouter
from api.api_v1.endpoints import items, users,auth,order

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])


api_router.include_router(order.router,prefix="/orders", tags=["orders"])