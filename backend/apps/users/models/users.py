import uuid
from typing import Optional

from pydantic import UUID4, EmailStr
from sqlmodel import Field, Relationship, SQLModel

from backend.common.models import (
    MappedBase,
    TimestampMixin,
)


class SQLModelBaseOAuthAccount(SQLModel):
    __tablename__ = "oauthaccount"

    id: UUID4 = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    user_id: UUID4 = Field(
        foreign_key="user.id",
        nullable=False,
    )
    oauth_name: str = Field(
        index=True,
        nullable=False,
    )
    access_token: str = Field(
        nullable=False,
    )
    expires_at: Optional[int] = Field(
        nullable=True,
    )
    refresh_token: Optional[str] = Field(
        nullable=True,
    )
    account_id: str = Field(
        index=True,
        nullable=False,
    )
    account_email: str = Field(
        nullable=False,
    )

    class Config:
        from_attributes = True


class SQLModelBaseUserDB(SQLModel):
    __tablename__ = "user"

    id: UUID4 = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    email: EmailStr = Field(
        nullable=False,
        unique=True,
        index=True,
    )
    hashed_password: str

    is_active: bool = Field(
        True,
        nullable=False,
    )
    is_superuser: bool = Field(
        False,
        nullable=False,
    )
    is_verified: bool = Field(
        False,
        nullable=False,
    )

    class Config:
        from_attributes = True


class OAuthAccount(
    SQLModelBaseOAuthAccount,
    MappedBase,
    table=True,
):
    user: Optional["User"] = Relationship(
        back_populates="oauth_accounts",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class User(
    TimestampMixin,
    SQLModelBaseUserDB,
    MappedBase,
    table=True,
):
    oauth_accounts: list["OAuthAccount"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
        },
    )
