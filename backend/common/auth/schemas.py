from pydantic import UUID4, EmailStr

from backend.common.schemas import BaseSchema


class BasePayload(BaseSchema):
    sub: UUID4

    @property
    def user_id_str(self) -> str:
        return str(self.sub)


class TokenPayload(BasePayload):
    session_uuid: UUID4

    @property
    def as_str_tuple(self) -> tuple[str, str]:
        return str(self.sub), str(self.session_uuid)


class PasswordResetPayload(BasePayload):
    pass


class EmailVerificationPayload(BaseSchema):
    sub: EmailStr
