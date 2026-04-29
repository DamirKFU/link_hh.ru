import importlib
import inspect
import pathlib
from functools import lru_cache
from types import ModuleType
from typing import Any, Type

from sqlmodel import SQLModel

from backend.core.path_conf import APP_FILE_PATH, PYCACHE_DIR_NAME, TEMPLATE_DIR_NAME


@lru_cache(maxsize=128)
def import_module_cached(
    module_path: str,
) -> ModuleType:
    return importlib.import_module(module_path)


def get_model_objects(
    module_path: str,
) -> list[Type[Any] | SQLModel] | None:
    try:
        module = import_module_cached(module_path)
    except ModuleNotFoundError:
        return None
    except Exception as e:
        raise e from None

    classes = []
    for _, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) and module_path in obj.__module__) or (
            isinstance(obj, SQLModel) and obj.metadata is not None
        ):
            classes.append(obj)
    return classes


def get_all_models() -> list[Type[Any] | SQLModel]:
    app_path = APP_FILE_PATH
    list_dirs = pathlib.Path.iterdir(app_path)

    apps = [
        d
        for d in list_dirs
        if pathlib.Path(app_path / d).is_dir() and d.name != PYCACHE_DIR_NAME
    ]

    objs = []
    for app in apps:
        module_path = f"backend.{app_path.name}.{app.name}.models"
        model_objs = get_model_objects(module_path)
        if model_objs:
            objs.extend(model_objs)

    return objs


def get_all_templates() -> list[pathlib.Path]:
    app_path = APP_FILE_PATH
    templates_dirs: list[pathlib.Path] = []

    for item in pathlib.Path.iterdir(app_path):
        if not item.is_dir() or item.name == PYCACHE_DIR_NAME:
            continue

        templates_path = item / TEMPLATE_DIR_NAME

        if templates_path.exists() and templates_path.is_dir():
            templates_dirs.append(templates_path)

    return templates_dirs
