"""
HTTP Endpoint Client

Responsible only for sending SMS data
to the configured HTTP endpoint.
"""

import requests

from app.config import settings
from app.models import SMS


class EndpointClient:
    """
    Simple HTTP client for forwarding SMS.
    """

    def send(self, sms: SMS) -> requests.Response:
        """
        Send SMS data to the configured endpoint.

        Raises:
            requests.RequestException
                if the request fails.
        """

        payload = {
            "inbox_id": sms.inbox_id,
            "From": sms.sender,
            "To": settings.sim_number,
            "Body": sms.message,
            "received_at": sms.received_at.isoformat(),
        }

        response = requests.post(
            url=settings.endpoint_url,
            json=payload,
            timeout=settings.request_timeout,
        )

        response.raise_for_status()

        return response