"""
Retry Worker

Continuously processes messages waiting in the retry queue.
"""

import time

from app.database import initialize_database, close_database
from app.logger import (
    application_logger,
    error_logger,
    retry_logger,
)
from app.processor import SMSProcessor
from app.repository import SMSRepository


POLL_INTERVAL = 30  # seconds


def main() -> None:

    initialize_database()

    repository = SMSRepository()
    processor = SMSProcessor()

    application_logger.info(
        "Retry worker started."
    )

    try:

        while True:

            retries = repository.get_pending_retries()

            if retries:

                retry_logger.info(
                    "Found %s pending retries.",
                    len(retries),
                )

            for retry in retries:

                try:

                    retry_logger.info(
                        "Retrying SMS ID %s (Attempt %s)",
                        retry.inbox_id,
                        retry.retry_count,
                    )

                    processor.process_sms(
                        retry.inbox_id
                    )

                except Exception:

                    error_logger.exception(
                        "Retry worker failed for SMS ID %s",
                        retry.inbox_id,
                    )

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:

        application_logger.info(
            "Retry worker stopped."
        )

    finally:

        close_database()


if __name__ == "__main__":
    main()