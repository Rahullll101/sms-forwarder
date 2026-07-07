"""
Database Repository

Responsible only for database operations.

No business logic.
No HTTP requests.
"""

from datetime import datetime

from app.database import get_connection
from app.models import SMS, RetryQueue


class SMSRepository:

    # ======================================================
    # Inbox
    # ======================================================

    def get_sms(self, inbox_id: int) -> SMS | None:
        """
        Fetch an SMS from Gammu inbox using its ID.
        """

        query = """
            SELECT
                "ID",
                "SenderNumber",
                "TextDecoded",
                "ReceivingDateTime"
            FROM inbox
            WHERE "ID" = %s;
        """

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(query, (inbox_id,))
                row = cursor.fetchone()

                if row is None:
                    return None

                return SMS(
                    inbox_id=row[0],
                    sender=row[1],
                    message=row[2],
                    received_at=row[3],
                )

    # ======================================================
    # Archive + Delete (Single Transaction)
    # ======================================================

    def archive_and_delete(
        self,
        sms: SMS,
        http_status: int,
        retry_count: int,
    ) -> None:
        """
        Archive the SMS and remove it from Gammu inbox.

        Both operations execute inside one transaction.
        """

        archive_query = """
            INSERT INTO forwarded_messages (

                inbox_id,
                sender,
                message,
                received_at,
                forwarded_at,
                http_status,
                retry_count

            )
            VALUES (

                %s,
                %s,
                %s,
                %s,
                NOW(),
                %s,
                %s

            );
        """

        delete_query = """
            DELETE FROM inbox
            WHERE "ID" = %s;
        """

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    archive_query,
                    (
                        sms.inbox_id,
                        sms.sender,
                        sms.message,
                        sms.received_at,
                        http_status,
                        retry_count,
                    ),
                )

                cursor.execute(
                    delete_query,
                    (sms.inbox_id,),
                )

            conn.commit()

    # ======================================================
    # Retry Queue
    # ======================================================

    def add_retry(
        self,
        inbox_id: int,
        retry_count: int,
        next_retry_time: datetime,
        last_error: str,
    ) -> None:
        """
        Insert or update a retry entry.
        """

        query = """
            INSERT INTO retry_queue (

                inbox_id,
                retry_count,
                status,
                next_retry_time,
                last_error

            )
            VALUES (

                %s,
                %s,
                'RETRY',
                %s,
                %s

            )

            ON CONFLICT (inbox_id)

            DO UPDATE SET

                retry_count = EXCLUDED.retry_count,
                status = 'RETRY',
                next_retry_time = EXCLUDED.next_retry_time,
                last_error = EXCLUDED.last_error;
        """

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    query,
                    (
                        inbox_id,
                        retry_count,
                        next_retry_time,
                        last_error,
                    ),
                )

            conn.commit()

    def get_pending_retries(self) -> list[RetryQueue]:
        """
        Fetch retries that are ready for processing.
        """

        query = """
            SELECT

                id,
                inbox_id,
                retry_count,
                status,
                next_retry_time,
                last_error,
                created_at

            FROM retry_queue

            WHERE
                status IN ('PENDING', 'RETRY')
                AND (
                    next_retry_time IS NULL
                    OR next_retry_time <= NOW()
                )

            ORDER BY created_at;
        """

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(query)

                rows = cursor.fetchall()

                return [
                    RetryQueue(
                        id=row[0],
                        inbox_id=row[1],
                        retry_count=row[2],
                        status=row[3],
                        next_retry_time=row[4],
                        last_error=row[5],
                        created_at=row[6],
                    )
                    for row in rows
                ]

    def mark_failed(self, inbox_id: int) -> None:
        """
        Mark a retry as permanently failed.
        """

        query = """
            UPDATE retry_queue

            SET status = 'FAILED'

            WHERE inbox_id = %s;
        """

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(query, (inbox_id,))

            conn.commit()

    def delete_retry(self, inbox_id: int) -> None:
        """
        Remove a retry entry after successful forwarding.
        """

        query = """
            DELETE FROM retry_queue
            WHERE inbox_id = %s;
        """

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(query, (inbox_id,))

            conn.commit()