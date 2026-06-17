import logging
import sys
from contextlib import suppress
from datetime import UTC
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.core.config import settings


def setup_logging() -> None:
    with suppress(OSError):
        Path("logs").mkdir(exist_ok=True)

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.LOG_FORMAT == "json":
        formatter: logging.Formatter = _JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    with suppress(OSError):
        file_handler = RotatingFileHandler(
            Path("logs/app.log"),
            encoding="utf-8",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime

        log_entry: dict[str, str] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
        return json.dumps(log_entry, ensure_ascii=False)
