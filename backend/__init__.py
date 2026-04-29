from typing import Callable

from sqlmodel import SQLModel

from backend.utils.dynamic_import import get_all_models

for cls in get_all_models():
    if isinstance(cls, type) and issubclass(cls, SQLModel):
        table_name: str | Callable[..., str] = cls.__tablename__
        if callable(table_name):
            table_name = table_name()
        if table_name not in globals():
            globals()[table_name] = cls
    else:
        class_name: str = cls.__name__
        if class_name not in globals():
            globals()[class_name] = cls


__version__ = "1.0.0"
