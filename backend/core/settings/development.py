import logging
from typing import Any

from backend.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    def model_post_init(self, context: Any) -> None:
        self.core.debug = True
        self.logging.level = logging.DEBUG
        self.api.title = "Dev FastAPI example application"

    model_config = AppSettings.model_config
