from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.item import Item
from schemas.item import ItemCreate, ItemUpdate
from crud.item import crud_item



class ItemService:
    def __init__(self):
        self.crud = crud_item

    def get(self, db: Session, id: int) -> Optional[Item]:
        return self.crud.get(db, id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
        return self.crud.get_multi(db, skip=skip, limit=limit)

    def get_by_name(self, db: Session, name: str) -> Optional[Item]:
        return self.crud.get_by_name(db, name)

    def get_by_price_range(self, db: Session, min_price: float, max_price: float) -> List[Item]:
        if min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_price cannot be greater than max_price"
            )
        return db.query(Item).filter(Item.price >= min_price, Item.price <= max_price).all()

    def search(self, db: Session, query: str) -> List[Item]:
        return db.query(Item).filter(Item.name.ilike(f"%{query}%")).all()

    def create(self, db: Session, obj_in: ItemCreate) -> Item:
        return self.crud.create(db, obj_in)

    def update(self, db: Session, id: int, obj_in: ItemUpdate) -> Optional[Item]:
        return self.crud.update(db, id, obj_in)

    def delete(self, db: Session, id: int) -> Optional[Item]:
        return self.crud.delete(db, id)


item_service = ItemService()
