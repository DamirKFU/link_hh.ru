import asyncio
import contextlib
import subprocess
from dataclasses import dataclass
from typing import Annotated

import cappa
from cappa.output import error_format
from fastapi_babel import BabelCli

from backend import __version__
from backend.common.babel import babel
from backend.core.path_conf import BASE_PATH

OUTPUT_HELP = "\nДля дополнительной информации попробуйте '[cyan]--help[/]'"

ERR_ALEMBIC_FAILED = "Не удалось выполнить команду Alembic"
ERR_UVICORN_FAILED = "Не удалось выполнить команду Uvicorn"

HELP_CLI = "Эффективный командный интерфейс FBA"

HELP_ALEMBIC = "Команды миграций"

HELP_REVISION = "Создать файл миграции базы данных"
HELP_REVISION_AUTOGENERATE = (
    "Автоматически определить изменения моделей и создать миграцию"
)
HELP_REVISION_MESSAGE = "Описание миграции"

HELP_UPGRADE = "Обновить базу данных до указанной версии"
HELP_UPGRADE_REVISION = "Целевая версия, по умолчанию последняя"

HELP_DOWNGRADE = "Откатить базу данных до указанной версии"
HELP_DOWNGRADE_REVISION = "Целевая версия, по умолчанию откат на одну версию"

HELP_CURRENT = "Показать текущую версию миграции базы данных"
HELP_VERBOSE = "Показать подробную информацию"

HELP_HISTORY = "Показать историю миграций"
HELP_HISTORY_RANGE = "Показать историю в указанном диапазоне, например -r base:head"

HELP_HEADS = "Показать все версии-головы"

HELP_UVICORN = "Запустить API через Uvicorn"
HELP_UVICORN_HOST = "Хост сервера"
HELP_UVICORN_PORT = "Порт сервера"
HELP_UVICORN_RELOAD = "Автоматическая перезагрузка при изменениях кода"

HELP_EXTRACT = "Извлечь переводы"
HELP_INIT = "Инициализировать переводы"
HELP_UPDATE = "Обновить переводы"
HELP_COMPILE = "Скомпилировать переводы"


babel_cli = BabelCli(
    babel=babel,
)


@cappa.command(help=HELP_REVISION, default_long=True)
@dataclass
class Revision:
    autogenerate: Annotated[
        bool,
        cappa.Arg(
            default=True,
            help=HELP_REVISION_AUTOGENERATE,
        ),
    ]
    message: Annotated[
        str,
        cappa.Arg(
            short="-m",
            default="",
            help=HELP_REVISION_MESSAGE,
        ),
    ]

    def __call__(self) -> None:
        args = ["revision"]
        if self.autogenerate:
            args.append("--autogenerate")
        if self.message:
            args.extend(["-m", self.message])
        run_alembic(*args)


@cappa.command(help=HELP_UPGRADE, default_long=True)
@dataclass
class Upgrade:
    revision: Annotated[
        str,
        cappa.Arg(
            default="head",
            help=HELP_UPGRADE_REVISION,
        ),
    ]

    def __call__(self) -> None:
        run_alembic("upgrade", self.revision)


@cappa.command(help=HELP_DOWNGRADE, default_long=True)
@dataclass
class Downgrade:
    revision: Annotated[
        str,
        cappa.Arg(
            default="-1",
            help=HELP_DOWNGRADE_REVISION,
        ),
    ]

    def __call__(self) -> None:
        run_alembic("downgrade", self.revision)


@cappa.command(help=HELP_CURRENT)
@dataclass
class Current:
    verbose: Annotated[
        bool,
        cappa.Arg(
            short="-v",
            default=False,
            help=HELP_VERBOSE,
        ),
    ]

    def __call__(self) -> None:
        args = ["current"]
        if self.verbose:
            args.append("-v")
        run_alembic(*args)


@cappa.command(help=HELP_HISTORY, default_long=True)
@dataclass
class History:
    verbose: Annotated[
        bool,
        cappa.Arg(
            short="-v",
            default=False,
            help=HELP_VERBOSE,
        ),
    ]
    range: Annotated[
        str,
        cappa.Arg(
            short="-r",
            default="",
            help=HELP_HISTORY_RANGE,
        ),
    ]

    def __call__(self) -> None:
        args = ["history"]
        if self.verbose:
            args.append("-v")
        if self.range:
            args.extend(["-r", self.range])
        run_alembic(*args)


@cappa.command(help=HELP_HEADS)
@dataclass
class Heads:
    verbose: Annotated[
        bool,
        cappa.Arg(
            short="-v",
            default=False,
            help=HELP_VERBOSE,
        ),
    ]

    def __call__(self) -> None:
        args = ["heads"]
        if self.verbose:
            args.append("-v")
        run_alembic(*args)


@cappa.command(help=HELP_ALEMBIC)
@dataclass
class Alembic:
    subcmd: cappa.Subcommands[
        Revision | Upgrade | Downgrade | Current | History | Heads
    ]


@cappa.command(help=HELP_UVICORN, default_long=True)
@dataclass
class Run:
    host: Annotated[
        str,
        cappa.Arg(
            default="127.0.0.1",
            help=HELP_UVICORN_HOST,
        ),
    ]
    port: Annotated[
        int,
        cappa.Arg(default=8000, help=HELP_UVICORN_PORT),
    ]
    reload: Annotated[
        bool,
        cappa.Arg(default=True, help=HELP_UVICORN_RELOAD),
    ]

    def __call__(self) -> None:
        args = ["backend.main:app"]

        args.extend(["--host", self.host])
        args.extend(["--port", str(self.port)])

        if self.reload:
            args.append("--reload")

        run_uvicorn(*args)


@cappa.command(help=HELP_EXTRACT)
@dataclass
class Extract:
    dir: Annotated[str, cappa.Arg(default=str(BASE_PATH), help=HELP_EXTRACT)]

    def __call__(self) -> None:
        babel_cli.extract(self.dir)


@cappa.command(help=HELP_INIT)
@dataclass
class Init:
    lang: Annotated[str, cappa.Arg(default=babel.default_locale, help=HELP_INIT)]

    def __call__(self) -> None:
        babel_cli.init(self.lang)


@cappa.command(help=HELP_UPDATE)
@dataclass
class Update:
    dir: Annotated[
        str,
        cappa.Arg(
            default=babel.config.BABEL_TRANSLATION_DIRECTORY,
            help=HELP_UPDATE,
        ),
    ]

    def __call__(self) -> None:
        babel_cli.update(self.dir)


@cappa.command(help=HELP_COMPILE)
@dataclass
class Compile:
    def __call__(self) -> None:
        babel_cli.compile()


@cappa.command(help="i18n commands")
@dataclass
class I18n:
    subcmd: cappa.Subcommands[Extract | Init | Update | Compile]


@cappa.command(help=HELP_CLI, default_long=True)
@dataclass
class FbaCli:
    subcmd: cappa.Subcommands[Alembic | Run | I18n]


def run_alembic(*args: str) -> None:
    try:
        subprocess.run(
            ["alembic", *args],
            cwd=BASE_PATH,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise cappa.Exit(ERR_ALEMBIC_FAILED, code=e.returncode)


def run_uvicorn(*args: str) -> None:
    try:
        subprocess.run(
            ["uvicorn", *args],
            cwd=BASE_PATH.parent,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise cappa.Exit(ERR_UVICORN_FAILED, code=e.returncode)


def main() -> None:
    output = cappa.Output(error_format=f"{error_format}\n{OUTPUT_HELP}")
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(
            cappa.invoke_async(
                FbaCli,
                version=__version__,
                output=output,
            ),
        )
