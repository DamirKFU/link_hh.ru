from enum import Enum
from functools import cache
from typing import Dict, Type

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from backend.core.path_conf import ENV_FILE_PATH
from backend.core.settings.app import AppSettings
from backend.core.settings.development import DevAppSettings
from backend.core.settings.production import ProdAppSettings


class AppEnvTypes(str, Enum):
    prod = "prod"
    dev = "dev"


class InitSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.prod

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="allow",
    )


environments: Dict[AppEnvTypes, Type[AppSettings]] = {
    AppEnvTypes.dev: DevAppSettings,
    AppEnvTypes.prod: ProdAppSettings,
}


@cache
def get_app_settings() -> AppSettings:
    app_env = InitSettings().app_env
    config = environments[app_env]
    return config()


settings = get_app_settings()
