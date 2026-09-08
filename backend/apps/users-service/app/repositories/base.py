from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class AbstractRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: CreateSchemaType) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity_id: str, data: UpdateSchemaType) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        raise NotImplementedError
