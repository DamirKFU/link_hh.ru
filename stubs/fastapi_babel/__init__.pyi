from __future__ import annotations

import pathlib
import re
import typing
from dataclasses import dataclass, field
from typing import Callable, NoReturn, Optional

from fastapi import Request, Response
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
)
from starlette.types import ASGIApp

@dataclass
class BabelConfigs:
    ROOT_DIR: typing.Union[str, pathlib.Path]
    BABEL_DEFAULT_LOCALE: str
    BABEL_TRANSLATION_DIRECTORY: str
    BABEL_DOMAIN: str = "messages.pot"
    BABEL_CONFIG_FILE: str = "babel.cfg"
    BABEL_MESSAGE_POT_FILE: str = field(init=False)

    def __post_init__(self) -> None: ...

class Babel:
    def __init__(self, configs: BabelConfigs) -> None: ...
    @staticmethod
    def raise_context_error() -> NoReturn: ...
    @property
    def domain(self) -> str: ...
    @property
    def default_locale(self) -> str: ...
    @property
    def locale(self) -> str: ...
    @locale.setter
    def locale(self, value: str) -> None: ...
    @property
    def gettext(self) -> Callable[[str], str]: ...
    def install_jinja(self, templates: Jinja2Templates) -> None: ...
    def run_cli(self) -> None: ...

class BabelCli:
    __module_name__ = "pybabel"

    def __init__(self, babel: Babel) -> None: ...
    def extract(self, watch_dir: str) -> None: ...
    def init(self, lang: Optional[str] = None) -> None: ...
    def update(self, watch_dir: Optional[str] = None) -> None: ...
    def compile(self) -> None: ...
    def run(self) -> None: ...

def _(message: str) -> str: ...

LANGUAGES_PATTERN = re.compile(r"([a-z]{2})-?([A-Z]{2})?(;q=\d.\d{1,3})?")

class BabelMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        babel_configs: BabelConfigs,
        locale_selector: Optional[Callable[[Request], Optional[str]]] = None,
        jinja2_templates: Optional[Jinja2Templates] = None,
        dispatch: Optional[DispatchFunction] = None,
    ) -> None: ...
    def _default_locale_selector(self, request: Request) -> str | None: ...
    def get_language(self, babel: Babel, lang_code: Optional[str] = None) -> str: ...
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response: ...


class LaxyTextMeta(type):
    def __call__(cls, *args: typing.Any, **kwds: typing.Any) -> str:
        ...


class LazyText(metaclass=LaxyTextMeta):
    message: str
    def __init__(self, message: str):
        ...

    def __repr__(self) -> str:
        ...

lazy_gettext = LazyText