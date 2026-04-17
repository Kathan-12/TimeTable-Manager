"""TimeSlot model definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class TimeSlot:
    """Represents an available scheduling timeslot.

    Attributes:
        id: Unique timeslot identifier.
        day: Weekday name.
        start_time: Start time in HH:MM format.
        end_time: End time in HH:MM format.
    """

    id: int
    day: str
    start_time: str
    end_time: str
