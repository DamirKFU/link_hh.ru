from enum import Enum

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict


class BaseSubSettings(BaseModel):
    model_config = SettingsConfigDict(
        validate_default=True,
        extra="forbid",
    )


class AppEnvTypes(str, Enum):
    prod = "prod"
    dev = "dev"
    test = "test"
