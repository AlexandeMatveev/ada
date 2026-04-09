from typing import List, Optional
from sqlalchemy.orm import Session
from models.item import Item
from schemas.item import ItemCreate, ItemUpdate


class CRUDItem:
    def get(self, db: Session, id: int) -> Optional[Item]:
        return db.query(Item).filter(Item.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
        return db.query(Item).offset(skip).limit(limit).all()

    def get_by_name(self, db: Session, name: str) -> Optional[Item]:
        return db.query(Item).filter(Item.name == name).first()

    def create(self, db: Session, obj_in: ItemCreate) -> Item:
        db_item = Item(**obj_in.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def update(self, db: Session, id: int, obj_in: ItemUpdate) -> Optional[Item]:
        db_item = self.get(db, id)
        if db_item:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():

                setattr(db_item, field, value)
            db.commit()
            db.refresh(db_item)
        return db_item

    def delete(self, db: Session, id: int) -> Optional[Item]:
        db_item = self.get(db, id)
        if db_item:
            db.delete(db_item)
            db.commit()
        return db_item


crud_item = CRUDItem()
