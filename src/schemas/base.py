from typing import Any, Self, Type, TypeVar

from pydantic import BaseModel
from db import Base


T = TypeVar('T', bound=Base)

class BaseSchema(BaseModel):
    pass

    def to_orm(self, model: Type[Base]) -> T:
        return model(**self.model_dump())

    @classmethod
    def from_orm(cls, obj: Any) -> Self:
        cls.model_validate(obj)