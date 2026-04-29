from pydantic import UUID4, BaseModel, EmailStr

from backend.common.schemas import BaseSelectSchema


class BaseUserSchemas(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False


class UserCreateInternal(BaseUserSchemas):
    hashed_password: str


class UserCreate(BaseUserSchemas):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None


class UserUpdateInternal(UserUpdate):
    hashed_password: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserDelete(BaseModel):
    pass


class UserSelect(BaseSelectSchema):
    id: UUID4
    email: EmailStr
    is_active: bool
    is_verified: bool
    is_superuser: bool
    hashed_password: str
