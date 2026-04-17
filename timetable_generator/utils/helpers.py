"""Shared helper functions used across the timetable generator application."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
TIME_PATTERN = "%H:%M"


def is_valid_email(email: str) -> bool:
    """Validate whether an email has a basic valid format.

    Args:
        email: Email string to validate.

    Returns:
        True if the email matches expected format, otherwise False.
    """

    return bool(EMAIL_PATTERN.match(email.strip()))


def parse_time(value: str) -> datetime:
    """Parse HH:MM formatted string into a datetime object.

    Args:
        value: Time string in 24-hour format.

    Returns:
        Parsed datetime object using a neutral date.

    Raises:
        ValueError: If time format is invalid.
    """

    return datetime.strptime(value, TIME_PATTERN)


def is_valid_time_range(start: str, end: str) -> bool:
    """Validate that the end time occurs after start time.

    Args:
        start: Start time in HH:MM format.
        end: End time in HH:MM format.

    Returns:
        True when end is greater than start.
    """

    return parse_time(end) > parse_time(start)


def format_timestamp() -> str:
    """Return a human-readable current timestamp.

    Returns:
        Timestamp formatted for status labels and logs.
    """

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_query(value: str) -> str:
    """Normalize search text for case-insensitive filtering.

    Args:
        value: Free text query.

    Returns:
        Lower-cased and stripped search query.
    """

    return value.strip().lower()


def safe_int(value: Any, default: int = 0) -> int:
    """Convert a value into int with fallback.

    Args:
        value: Value to convert.
        default: Fallback if conversion fails.

    Returns:
        Converted integer or fallback value.
    """

    try:
        return int(value)
    except (TypeError, ValueError):
        return default
