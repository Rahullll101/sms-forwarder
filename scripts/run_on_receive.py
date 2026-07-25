"""
RunOnReceive Entry Point

This script is executed by Gammu SMSD whenever
a new SMS is received.

Usage:
    python run_on_receive.py <INBOX_ID>
"""

import sys

from app.database import initialize_database, close_database
from app.logger import application_logger, error_logger
from app.processor import SMSProcessor


def main() -> None:

    if len(sys.argv) != 2:

        error_logger.error(
            "Usage: python run_on_receive.py <INBOX_ID>"
        )

        sys.exit(1)

    try:

        inbox_id = int(sys.argv[1])

    except ValueError:

        error_logger.error(
            "Invalid inbox ID: %s",
            sys.argv[1],
        )

        sys.exit(1)

    initialize_database()

    try:

        application_logger.info(
            "RunOnReceive triggered for SMS ID %s",
            inbox_id,
        )
        processor = SMSProcessor()
        processor.process_sms(inbox_id)

        application_logger.info(
            "Finished processing SMS ID %s",
            inbox_id,
        )

    except Exception:

        error_logger.exception(
            "Unexpected error while processing SMS ID %s",
            inbox_id,
        )

        sys.exit(1)

    finally:

        close_database()


if __name__ == "__main__":
    main()