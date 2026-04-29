from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declared_attr
from sqlmodel import (
    TIMESTAMP,
    Column,
    Field,
    SQLModel,
    func,
)


class MappedBase(AsyncAttrs, SQLModel):
    @declared_attr.directive
    def __tablename__(self) -> str:
        return self.__name__.lower()

    @declared_attr.directive
    def __table_args__(self) -> dict[str, str]:
        return {"comment": self.__doc__ or ""}


class TimestampMixin:
    created_at: Optional[datetime] = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=True,
        ),
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            onupdate=func.now(),
            nullable=True,
        ),
    )
