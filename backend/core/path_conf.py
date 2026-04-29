from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent

ENV_FILE_PATH = BASE_PATH / ".env"

APP_FILE_PATH = BASE_PATH / "apps"

ENV_PROD_FILE_PATH = BASE_PATH / "prod.env"

ALEMBIC_VERSION_DIR = BASE_PATH / "alembic" / "versions"

LOG_DIR = BASE_PATH / "log"

STATIC_DIR = BASE_PATH / "static"

UPLOAD_DIR = STATIC_DIR / "upload"

PLUGIN_DIR = BASE_PATH / "plugin"

LOCALE_DIR = BASE_PATH / "locale"

MYSQL_SCRIPT_DIR = BASE_PATH / "sql" / "mysql"

POSTGRESQL_SCRIPT_DIR = BASE_PATH / "sql" / "postgresql"

RELOAD_LOCK_FILE = BASE_PATH / ".reload.lock"

PYCACHE_DIR_NAME = "__pycache__"

TEMPLATE_DIR_NAME = "templates"

BABEL_DIR_NAME = "lang"
