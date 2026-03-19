# services/overdrive_service.py

from datetime import date, timedelta
from services.telemetry_service import log_event


def activate_overdrive(user):
    """
    Activates overdrive for 2 days after debt is cleared.
    """

    user.overdrive_active = True
    user.overdrive_expires = date.today() + timedelta(days=2)

    log_event(user, "OVERDRIVE_ACTIVATED", {
        "expires_on": str(user.overdrive_expires)
    })


def check_overdrive(user):
    """
    Disables overdrive if expired.
    """

    if not user.overdrive_active:
        return

    if user.overdrive_expires and date.today() > user.overdrive_expires:
        user.overdrive_active = False

        log_event(user, "OVERDRIVE_EXPIRED", {})