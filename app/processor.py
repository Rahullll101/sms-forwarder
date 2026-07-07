"""
SMS Processing Service

Coordinates the complete SMS forwarding workflow.

Business Logic Only.
"""

from requests import RequestException

from app.endpoint import EndpointClient
from app.logger import (
    application_logger,
    error_logger,
    retry_logger,
)
from app.repository import SMSRepository
from app.retry import (
    calculate_next_retry,
    is_max_retry,
)


class SMSProcessor:
    """
    Orchestrates the SMS forwarding workflow.

    Responsibilities:
    - Read SMS from Gammu inbox
    - Forward to HTTP endpoint
    - Archive successful messages
    - Schedule retries on failure
    """

    def __init__(self):

        self.repository = SMSRepository()
        self.endpoint = EndpointClient()

    def process_sms(self, inbox_id: int) -> None:
        """
        Process a single SMS using its Gammu inbox ID.
        """

        application_logger.info(
            "Processing SMS ID %s",
            inbox_id,
        )

        sms = self.repository.get_sms(inbox_id)

        if sms is None:

            application_logger.warning(
                "SMS ID %s not found in inbox.",
                inbox_id,
            )

            return

        # Fetch retry information once
        retry = self.repository.get_retry(inbox_id)

        retry_count = 0 if retry is None else retry.retry_count

        try:

            response = self.endpoint.send(sms)

            self.repository.archive_and_delete(
                sms=sms,
                http_status=response.status_code,
                retry_count=retry_count,
            )

            if retry is not None:
                self.repository.delete_retry(inbox_id)

            application_logger.info(
                "SMS ID %s forwarded successfully.",
                inbox_id,
            )

        except RequestException as exc:

            error_logger.exception(
                "Failed to forward SMS ID %s",
                inbox_id,
            )

            retry_count += 1

            if is_max_retry(retry_count):

                self.repository.mark_failed(inbox_id)

                error_logger.error(
                    "SMS ID %s marked as FAILED after %s retries.",
                    inbox_id,
                    retry_count,
                )

                return

            retry_time = calculate_next_retry(retry_count)

            self.repository.add_retry(
                inbox_id=inbox_id,
                retry_count=retry_count,
                next_retry_time=retry_time,
                last_error=str(exc),
            )

            retry_logger.info(
                "Retry #%s scheduled for SMS ID %s at %s",
                retry_count,
                inbox_id,
                retry_time,
            )