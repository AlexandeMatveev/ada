from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from core.database import get_db  # <-- прямой импорт
from schemas.item import Item, ItemCreate, ItemUpdate
from services.item_service import item_service

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_items(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_price: float = None,
    max_price: float = None,
    search: str = None
):
    if min_price and max_price:
        return item_service.get_by_price_range(db, min_price, max_price)
    if search:
        return item_service.search(db, search)
    return item_service.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db)
):
    return item_service.create(db, obj_in=item_in)

@router.get("/statistics", response_model=dict)
def get_statistics(
    db: Session = Depends(get_db)
):
    return item_service.get_statistics(db)

@router.get("/{item_id}", response_model=Item)
def read_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    return item_service.get(db, id=item_id)

@router.put("/{item_id}", response_model=Item)
def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db)
):
    return item_service.update(db, id=item_id, obj_in=item_in)

@router.delete("/{item_id}", response_model=Item)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    return item_service.delete(db, id=item_id)