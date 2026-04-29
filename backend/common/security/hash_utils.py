from pwdlib import PasswordHash

from backend.core.config import settings

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def get_password_hash(password: str) -> str:
    return password_hash.hash(
        password,
        salt=settings.core.secret_key.get_secret_value().encode(),
    )
