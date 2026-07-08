"""
Health Check Script

Checks the availability of all critical
application dependencies.
"""

from pathlib import Path
import shutil

import requests

from app.config import settings
from app.database import (
    get_connection,
    initialize_database,
    close_database,
)


def check_database() -> bool:
    """
    Check PostgreSQL connectivity.
    """

    try:

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("SELECT 1;")

                cursor.fetchone()

        return True

    except Exception:
        import traceback

        print("\nDatabase Health Check Failed")
        traceback.print_exc()

        return False


def check_endpoint() -> bool:
    """
    Check whether the configured endpoint
    is reachable.
    """

    try:

        response = requests.head(
            settings.endpoint_url,
            timeout=5,
            allow_redirects=True,
        )

        return response.status_code < 500

    except Exception:

        return False


def check_logs() -> bool:
    """
    Verify that the logs directory exists.
    """

    return Path("logs").exists()


def check_disk_space() -> bool:
    """
    Verify sufficient disk space is available.

    Returns False if free space
    is less than 500 MB.
    """

    _, _, free = shutil.disk_usage("/")

    return free > (500 * 1024 * 1024)


# ==========================================================
# Hardware Checks
# Enable these after Raspberry Pi deployment
# ==========================================================

# def check_gammu_service() -> bool:
#     """
#     Check whether Gammu SMSD service is running.
#     Example:
#
#         systemctl is-active gammu-smsd
#     """
#
#     pass


# def check_modem() -> bool:
#     """
#     Verify SIM7600 modem is detected.
#     Example:
#
#         lsusb
#
#     or
#
#         /dev/ttyUSB*
#     """
#
#     pass


# def check_sim_registration() -> bool:
#     """
#     Verify SIM is registered
#     on the mobile network.
#     Example:
#
#         AT+CREG?
#     """
#
#     pass


# def check_signal_strength() -> bool:
#     """
#     Verify modem signal quality.
#     Example:
#
#         AT+CSQ
#     """
#
#     pass


def main() -> None:
    """
    Execute all health checks.
    """

    initialize_database()

    try:

        checks = {

            "Database": check_database(),

            "Endpoint": check_endpoint(),

            "Logs Directory": check_logs(),

            "Disk Space": check_disk_space(),

            # ==================================================
            # Enable after hardware deployment
            # ==================================================

            # "Gammu SMSD": check_gammu_service(),
            #
            # "SIM7600 Modem": check_modem(),
            #
            # "SIM Registration": check_sim_registration(),
            #
            # "Signal Strength": check_signal_strength(),

        }

        print("\n========== Health Check ==========\n")

        overall = True

        for component, status in checks.items():

            symbol = "✓" if status else "✗"

            print(f"{symbol} {component}")

            overall &= status

        print("\n==================================")

        if overall:

            print("Overall Status : HEALTHY")

        else:

            print("Overall Status : UNHEALTHY")

    finally:

        close_database()


if __name__ == "__main__":
    main()