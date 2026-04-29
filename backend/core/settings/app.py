import logging
import re
from datetime import timedelta
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

from pydantic import Field, HttpUrl, PostgresDsn, SecretStr, model_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from backend.common.settings import (
    BaseSubSettings,
)
from backend.core.path_conf import ENV_FILE_PATH


class TimezoneSubSettings(BaseSubSettings):
    datetime_timezone: str = "UTC"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"


class FrontendRoutesSubSettings(BaseSubSettings):
    frontend_url: HttpUrl = HttpUrl("http://localhost:3000")
    success_login_path: str = "/login-success"
    verify_path: str = "/verify"
    reset_password_path: str = "/reset-password"


class CoreSubSettings(BaseSubSettings):
    debug: bool = False
    secret_key: SecretStr
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"])


class DatabaseSubSettings(BaseSubSettings):
    url: PostgresDsn
    database_echo: bool = False
    database_pool_echo: bool = False


class RedisTokenSubSettings(BaseSubSettings):
    lifetime_seconds: int = int(timedelta(days=7).total_seconds())


class APISubSettings(BaseSubSettings):
    api_prefix: str = "/api"
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    token_url: str = "api/auth/v1/login"
    redoc_url: str = "/redoc"
    title: str = "FastAPI example application"
    description: str = "Example description"
    version: str = "0.0.0"

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }


class LoggingSubSettings(BaseSubSettings):
    level: int = logging.INFO
    loggers: Tuple[str, str] = (
        "uvicorn.asgi",
        "uvicorn.access",
    )


class RedisSubSettings(BaseSubSettings):
    host: str = "localhost"
    port: int = 6379
    password: SecretStr = SecretStr("")
    cache_db: str = "0"
    auth_db: str = "1"

    timeout: int = 5


class AuthJWTSettings(BaseSubSettings):
    access_token_expire_seconds: int = int(timedelta(days=1).total_seconds())
    refresh_token_expire_seconds: int = int(timedelta(days=30).total_seconds())
    password_reset_expire_seconds: int = int(timedelta(minutes=10).total_seconds())
    email_verification_expire_seconds: int = int(timedelta(minutes=10).total_seconds())

    token_algorithm: str = "HS256"

    access_cookie_name: str = "access_token"
    refresh_cookie_name: str = "refresh_token"
    cookie_domain: Optional[str] = None
    cookie_secure: bool = False
    cookie_httponly: bool = True
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"


class SMTPSettings(BaseSubSettings):
    backend: Literal["smtp"]

    username: str
    password: SecretStr
    from_email: str
    server: str

    port: int = 587
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True
    timeout: int = 10


class FileMailSettings(BaseSubSettings):
    backend: Literal["file"]


class GoogleOAuthSubSettings(BaseSubSettings):
    secret: SecretStr
    client_id: SecretStr


class I18NSubSettings(BaseSubSettings):
    default_language: str = "en"


class TraceIDSubSettings(BaseSubSettings):
    header: str = "X-Request-ID"
    log_len: int = 32
    default_value: str = "-"


class CSRFSubSettings(BaseSubSettings):
    cookie_samesite: Literal["lax", "strict", "none"] = "strict"
    cookie_secure: bool = False
    exempt_urls: list[str] = [
        r"^/api/auth/[^/]+/register$",
    ]
    allow_all: bool = False

    @property
    def compiled_exempt_urls(self) -> list[re.Pattern[str]]:
        if self.allow_all:
            return [re.compile(r".*")]
        return [re.compile(p) for p in self.exempt_urls]


class AppSettings(BaseSettings):
    core: CoreSubSettings
    db: DatabaseSubSettings
    api: APISubSettings = APISubSettings()
    logging: LoggingSubSettings = LoggingSubSettings()
    timezone: TimezoneSubSettings = TimezoneSubSettings()
    redis: RedisSubSettings = RedisSubSettings()
    auth: AuthJWTSettings = AuthJWTSettings()
    frontend_route: FrontendRoutesSubSettings = FrontendRoutesSubSettings()
    redis_token: RedisTokenSubSettings = RedisTokenSubSettings()
    i18n: I18NSubSettings = I18NSubSettings()
    trace_id: TraceIDSubSettings = TraceIDSubSettings()
    csrf: CSRFSubSettings = CSRFSubSettings()
    google: GoogleOAuthSubSettings
    mail: Union[SMTPSettings, FileMailSettings] = Field(discriminator="backend")

    @model_validator(mode="before")
    @classmethod
    def drop_init_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        values.pop("app_env", None)
        return values

    model_config = SettingsConfigDict(
        validate_assignment=True,
        env_file=ENV_FILE_PATH,
        env_prefix="APP__",
        extra="forbid",
        env_nested_delimiter="__",
    )
