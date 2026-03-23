from typing import Generic, TypeVar, List, Optional, Any, Union, Type
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import HTTPException, status
import logging

from core.database import Base
from crud.base import CRUDBase

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый сервис с общей бизнес-логикой.

    Наследуется для конкретных моделей.
    Предоставляет стандартные CRUD операции с проверками и валидацией.
    """

    def __init__(self, crud: CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
        self.crud = crud
        self.model_name = crud.model.__name__

    def get(self, db: Session, id: int) -> ModelType:
        """
        Получить объект по ID с проверкой существования.

        Args:
            db: Сессия базы данных
            id: ID объекта

        Returns:
            Объект модели

        Raises:
            HTTPException 404: Если объект не найден
        """
        obj = self.crud.get(db, id=id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model_name} with id {id} not found"
            )
        return obj

    def get_multi(
            self,
            db: Session,
            *,
            skip: int = 0,
            limit: int = 100,
            **filters
    ) -> List[ModelType]:
        """
        Получить список объектов с пагинацией.

        Args:
            db: Сессия базы данных
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            **filters: Дополнительные фильтры

        Returns:
            Список объектов
        """
        return self.crud.get_multi(db, skip=skip, limit=limit)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Создать новый объект.

        Args:
            db: Сессия базы данных
            obj_in: Данные для создания

        Returns:
            Созданный объект
        """
        self._validate_create(db, obj_in)
        logger.info(f"Creating {self.model_name}: {obj_in.model_dump()}")
        obj = self.crud.create(db, obj_in=obj_in)
        self._after_create(db, obj)
        return obj

    def update(
            self,
            db: Session,
            *,
            id: int,
            obj_in: Union[UpdateSchemaType, dict]
    ) -> ModelType:
        """
        Обновить существующий объект.

        Args:
            db: Сессия базы данных
            id: ID объекта
            obj_in: Данные для обновления

        Returns:
            Обновлённый объект
        """
        obj = self.get(db, id=id)
        self._validate_update(db, obj, obj_in)
        logger.info(f"Updating {self.model_name} {id}: {obj_in}")
        obj = self.crud.update(db, db_obj=obj, obj_in=obj_in)
        return obj

    def delete(self, db: Session, *, id: int) -> ModelType:
        """
        Удалить объект.

        Args:
            db: Сессия базы данных
            id: ID объекта

        Returns:
            Удалённый объект
        """
        obj = self.get(db, id=id)
        self._validate_delete(db, obj)
        logger.info(f"Deleting {self.model_name} {id}")
        return self.crud.remove(db, id=id)

    def exists(self, db: Session, *, id: int) -> bool:
        """
        Проверить существование объекта.

        Args:
            db: Сессия базы данных
            id: ID объекта

        Returns:
            True если объект существует, иначе False
        """
        return self.crud.get(db, id=id) is not None

    def count(self, db: Session, **filters) -> int:
        """
        Получить количество объектов.

        Args:
            db: Сессия базы данных
            **filters: Фильтры

        Returns:
            Количество объектов
        """
        from sqlalchemy import func
        query = db.query(self.crud.model)
        return query.count()

    # Методы для переопределения в дочерних классах

    def _validate_create(self, db: Session, obj_in: CreateSchemaType) -> None:
        """
        Валидация перед созданием. Переопределяется в наследниках.
        """
        pass

    def _validate_update(
            self,
            db: Session,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, dict]
    ) -> None:
        """
        Валидация перед обновлением. Переопределяется в наследниках.
        """
        pass

    def _validate_delete(self, db: Session, db_obj: ModelType) -> None:
        """
        Валидация перед удалением. Переопределяется в наследниках.
        """
        pass

    def _after_create(self, db: Session, db_obj: ModelType) -> None:
        """
        Действия после создания. Переопределяется в наследниках.
        """
        pass