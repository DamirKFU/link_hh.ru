from pydantic_settings import SettingsConfigDict

from backend.core.path_conf import ENV_PROD_FILE_PATH
from backend.core.settings.app import AppSettings


class ProdAppSettings(AppSettings):
    model_config = AppSettings.model_config | SettingsConfigDict(
        env_file=ENV_PROD_FILE_PATH
    )
