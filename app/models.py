"""
Application Models

These dataclasses represent the application's domain objects.

No database logic.
No business logic.
No HTTP logic.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ==========================================================
# Gammu Inbox SMS
# ==========================================================

@dataclass(slots=True)
class SMS:
    """
    Represents one SMS from Gammu's inbox table.
    """

    inbox_id: int
    sender: str
    message: str
    received_at: datetime


# ==========================================================
# Retry Queue
# ==========================================================

@dataclass(slots=True)
class RetryQueue:

    id: Optional[int]

    inbox_id: int

    retry_count: int

    status: str

    next_retry_time: Optional[datetime]

    last_error: Optional[str]

    created_at: datetime


# ==========================================================
# Forwarded Messages
# ==========================================================

@dataclass(slots=True)
class ForwardedMessage:

    id: Optional[int]

    inbox_id: int

    sender: str

    message: str

    received_at: datetime

    forwarded_at: datetime

    http_status: Optional[int]

    retry_count: int

    created_at: datetime