# =========================================================
# CARELINE TELEMEDICINE SYSTEM
# Helper Functions
# =========================================================

from datetime import datetime
import re


def is_valid_email(email):
    """
    Checks whether an email address has a valid basic format.
    """

    if not email:
        return False

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(re.match(pattern, email))


def is_valid_phone(phone):
    """
    Checks whether a phone number contains 10 digits.
    """

    if not phone:
        return False

    digits = re.sub(r"\D", "", phone)

    return len(digits) == 10


def clean_text(value):
    """
    Removes unnecessary spaces from text.
    """

    if value is None:
        return ""

    return str(value).strip()


def safe_int(value, default=0):
    """
    Safely converts a value to an integer.
    """

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    """
    Safely converts a value to a float.
    """

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def current_timestamp():
    """
    Returns the current date and time.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )