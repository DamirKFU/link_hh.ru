from uuid import UUID

from fastcrud import FastCRUD
from sqlalchemy.ext.asyncio import AsyncSession

from backend.apps.users.models import User
from backend.apps.users.schemas import (
    UserCreate,
    UserCreateInternal,
    UserDelete,
    UserSelect,
    UserUpdate,
    UserUpdateInternal,
)
from backend.common.security.hash_utils import get_password_hash


class UserCRUD(
    FastCRUD[
        User,
        UserCreateInternal,
        UserUpdate,
        UserUpdateInternal,
        UserDelete,
        UserSelect,
    ]
):
    async def create_user(
        self,
        session: AsyncSession,
        schema: UserCreate,
        commit: bool = True,
    ) -> UserSelect:
        internal = UserCreateInternal(
            email=schema.email,
            is_active=schema.is_active,
            is_verified=schema.is_verified,
            is_superuser=schema.is_superuser,
            hashed_password=get_password_hash(schema.password),
        )
        return await self.create(
            session,
            internal,
            return_as_model=True,
            schema_to_select=UserSelect,
            commit=commit,
        )

    async def change_password(
        self,
        session: AsyncSession,
        password: str,
        user_id: UUID,
        commit: bool = True,
    ) -> None:
        internal = UserUpdateInternal(
            hashed_password=get_password_hash(password),
        )
        await self.update(session, internal, commit=commit, id=user_id)

    async def set_verify(
        self,
        session: AsyncSession,
        user_id: UUID,
        commit: bool = True,
    ) -> None:
        internal = UserUpdateInternal(
            is_verified=True,
        )
        await self.update(session, internal, commit=commit, id=user_id)


users_crud = UserCRUD(User)
