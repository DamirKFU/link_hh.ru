from fastapi_babel import Babel, BabelConfigs

from backend.core.config import settings
from backend.core.path_conf import BABEL_DIR_NAME, BASE_PATH

babel_config = BabelConfigs(
    ROOT_DIR=BASE_PATH,
    BABEL_DEFAULT_LOCALE=settings.i18n.default_language,
    BABEL_TRANSLATION_DIRECTORY=BABEL_DIR_NAME,
)

babel = Babel(configs=babel_config)
