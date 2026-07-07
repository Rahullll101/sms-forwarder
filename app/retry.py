"""
Retry Utilities

Contains helper functions related to retry scheduling.
"""

from datetime import datetime, timedelta

from app.config import settings


RETRY_DELAYS = {
    1: 15,
    2: 30,
    3: 60,
    4: 120,
    5: 300,
}


def calculate_next_retry(retry_count: int) -> datetime:
    """
    Calculate the next retry timestamp.
    """

    delay = RETRY_DELAYS.get(retry_count, 300)

    return datetime.now() + timedelta(seconds=delay)


def is_max_retry(retry_count: int) -> bool:
    """
    Check whether the retry limit has been reached.
    """

    return retry_count > settings.max_retry