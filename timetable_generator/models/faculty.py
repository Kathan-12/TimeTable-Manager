"""Faculty model definitions."""

from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class Faculty:
    """Represents a faculty member and their teaching availability.

    Attributes:
        id: Unique faculty identifier.
        name: Faculty full name.
        department: Department affiliation.
        email: Official email address.
        available_slots: List of available timeslot IDs.
        assigned_courses: List of course IDs assigned to this faculty.
    """

    id: int
    name: str
    department: str
    email: str
    available_slots: List[int]
    assigned_courses: List[int]
