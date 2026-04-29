from pydantic import EmailStr

from backend.apps.auth.schemas.users import SetPassword, UserBase
from backend.common.schemas import BaseSchema


class ForgotPassword(UserBase):
    pass


class TokenSchema(BaseSchema):
    token: str


class ResetPassword(SetPassword, TokenSchema):
    pass


class VerifyEmail(UserBase):
    email: EmailStr
