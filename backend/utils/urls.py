from typing import Any
from urllib.parse import urlencode

from sqlalchemy import URL
from sqlalchemy.engine.url import make_url

from backend.core.config import settings


def create_database_url(test_db_name: str) -> str:
    url = str(settings.db.url)
    return replace_db_name(url, test_db_name)


def replace_db_name(db_url: str | URL, new_db_name: str) -> str:
    url = make_url(db_url)
    url = url.set(database=new_db_name)
    return str(url)


def build_frontend_url(path: str, **query: Any) -> str:
    base = str(settings.frontend_route.frontend_url).rstrip("/")
    url = f"{base}{path}"

    if query:
        url += f"?{urlencode(query)}"

    return url
