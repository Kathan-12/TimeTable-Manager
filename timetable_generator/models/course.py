"""Course model definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class Course:
    """Represents a course that needs scheduling.

    Attributes:
        id: Unique course identifier.
        name: Course display name.
        code: Short alphanumeric code.
        lectures_per_week: Number of sessions per week.
        is_lab: Whether this course is a lab session.
        duration_hours: Session duration in hours.
    """

    id: int
    name: str
    code: str
    lectures_per_week: int
    is_lab: bool
    duration_hours: float
