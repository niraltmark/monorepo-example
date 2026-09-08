from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

ModelType = TypeVar("ModelType")
CreateDataType = TypeVar("CreateDataType")
UpdateDataType = TypeVar("UpdateDataType")

class AbstractRepository(ABC, Generic[ModelType, CreateDataType, UpdateDataType]):

    @abstractmethod
    def get_by_id(self, entity_id: Any) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        raise NotImplementedError

    @abstractmethod
    def create(self, data: CreateDataType) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity_id: Any, data: UpdateDataType) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: Any) -> bool:
        raise NotImplementedError
