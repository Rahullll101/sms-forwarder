"""
Application Logger

Centralized logging configuration.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def create_handler(filename: str) -> RotatingFileHandler:
    """
    Create a rotating log file handler.
    """

    handler = RotatingFileHandler(
        LOG_DIR / filename,
        maxBytes=10 * 1024 * 1024,   # 10 MB
        backupCount=5,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)

    return handler


# ======================================================
# Application Logger
# ======================================================

application_logger = logging.getLogger("application")

application_logger.setLevel(settings.log_level)

application_logger.addHandler(
    create_handler("application.log")
)

application_logger.propagate = False


# ======================================================
# Error Logger
# ======================================================

error_logger = logging.getLogger("error")

error_logger.setLevel(logging.ERROR)

error_logger.addHandler(
    create_handler("error.log")
)

error_logger.propagate = False


# ======================================================
# Retry Logger
# ======================================================

retry_logger = logging.getLogger("retry")

retry_logger.setLevel(logging.INFO)

retry_logger.addHandler(
    create_handler("retry.log")
)

retry_logger.propagate = False