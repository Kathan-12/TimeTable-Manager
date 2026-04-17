"""Timetable entry model definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class TimetableEntry:
    """Represents one scheduled lecture in the generated timetable.

    Attributes:
        course_id: Associated course ID.
        faculty_id: Assigned faculty ID.
        batch_id: Assigned batch ID.
        room_id: Assigned room ID.
        time_slot_id: Assigned timeslot ID.
    """

    course_id: int
    faculty_id: int
    batch_id: int
    room_id: int
    time_slot_id: int
