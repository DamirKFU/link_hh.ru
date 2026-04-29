import logging
import sys
from types import FrameType
from typing import Any, Callable, cast

import loguru
from loguru import logger

from backend.core.config import settings
from backend.utils.trace_id import get_request_trace_id


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def extra_filter(
    key: str, value: Any, *, exclude: bool = False
) -> Callable[["loguru.Record"], bool]:
    def _filter(record: "loguru.Record") -> bool:
        current = record["extra"].get(key)
        if exclude:
            return bool(current != value)
        return bool(current == value)

    return _filter


def add_request_id(record: "loguru.Record") -> None:
    rid = get_request_trace_id()
    record["extra"]["request_id"] = rid[: settings.trace_id.log_len]


def setup_logging() -> None:
    logger.remove()

    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in settings.logging.loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler(level=settings.logging.level)]

    logger.configure(patcher=add_request_id)

    logger.add(
        sys.stdout,
        level=settings.logging.level,
        filter=extra_filter("destination", None),
    )


log = logger
