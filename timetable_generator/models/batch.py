"""Batch model definitions."""

from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class Batch:
    """Represents a student batch for timetable scheduling.

    Attributes:
        id: Unique batch identifier.
        name: Batch name.
        size: Total number of students.
        semester: Academic semester.
        courses: List of assigned course IDs.
    """

    id: int
    name: str
    size: int
    semester: int
    courses: List[int]
