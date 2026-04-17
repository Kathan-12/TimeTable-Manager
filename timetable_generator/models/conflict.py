"""Conflict model definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class Conflict:
    """Represents a scheduling conflict detected by the system.

    Attributes:
        type: Conflict category string.
        description: Human readable detail.
        severity: Priority level (HIGH, MEDIUM, LOW).
    """

    type: str
    description: str
    severity: str
