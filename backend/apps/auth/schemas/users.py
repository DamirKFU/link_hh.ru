from typing import Self

from pydantic import EmailStr, model_validator

from backend.common.resources import strings
from backend.common.schemas import BaseSchema, BaseSelectSchema


class UserBase(BaseSchema):
    email: EmailStr


class SetPassword(BaseSchema):
    password: str
    repeat_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.repeat_password:
            raise ValueError(strings.REPEAT_PASWWORD_ERROR)
        return self


class UserRegister(UserBase, SetPassword):
    pass


class UserLogin(UserBase):
    password: str


class UserPublic(UserBase, BaseSelectSchema):
    pass
