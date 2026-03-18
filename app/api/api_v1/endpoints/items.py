from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from schemas.item import Item, ItemCreate, ItemUpdate
from services.item_service import item_service

router = APIRouter()


@router.post("/", response_model=Item)
def create_item(item_in: ItemCreate, db: Session = Depends(get_db)):
    return item_service.create(db, obj_in=item_in)


@router.get("/", response_model=List[Item])
def read_items(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_price: float = None,
    max_price: float = None,
    search: str = None
):
    if min_price is not None and max_price is not None:
        return item_service.get_by_price_range(db, min_price, max_price)
    if search:
        return item_service.search(db, search)
    return item_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = item_service.get(db, id=item_id)
    if item is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=Item)
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    item = item_service.update(db, id=item_id, obj_in=item_in)
    if item is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = item_service.delete(db, id=item_id)
    if item is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
