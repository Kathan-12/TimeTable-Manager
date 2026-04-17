"""Mock data factories for all timetable generator models."""

from __future__ import annotations

from typing import Dict, List

from timetable_generator.models.batch import Batch
from timetable_generator.models.conflict import Conflict
from timetable_generator.models.course import Course
from timetable_generator.models.faculty import Faculty
from timetable_generator.models.room import Room
from timetable_generator.models.timetable_entry import TimetableEntry
from timetable_generator.models.timeslot import TimeSlot

DAYS: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SLOT_WINDOWS: List[tuple[str, str]] = [
    ("09:00", "10:00"),
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
]


def get_timeslot_list() -> List[TimeSlot]:
    """Return mock timeslots for all weekdays.

    Returns:
        List of 25 timeslot records (5 days x 5 slots).
    """

    slots: List[TimeSlot] = []
    slot_id = 1
    for day in DAYS:
        for start, end in SLOT_WINDOWS:
            slots.append(TimeSlot(id=slot_id, day=day, start_time=start, end_time=end))
            slot_id += 1
    return slots


def get_course_list() -> List[Course]:
    """Return a realistic mix of lecture and lab courses.

    Returns:
        List of 10 course records.
    """

    return [
        Course(1, "Data Structures", "CS201", 3, False, 1.0),
        Course(2, "Operating Systems", "CS301", 3, False, 1.0),
        Course(3, "Database Systems", "CS305", 3, False, 1.0),
        Course(4, "Machine Learning", "CS401", 2, False, 1.0),
        Course(5, "Computer Networks", "CS303", 3, False, 1.0),
        Course(6, "Physics Lab", "PHL110", 2, True, 2.0),
        Course(7, "Electronics Lab", "ECL210", 2, True, 2.0),
        Course(8, "Web Engineering", "CS350", 2, False, 1.0),
        Course(9, "Compiler Design", "CS450", 2, False, 1.0),
        Course(10, "Cloud Computing", "CS470", 2, True, 3.0),
    ]


def get_batch_list() -> List[Batch]:
    """Return mock student batches.

    Returns:
        List of 6 batch records.
    """

    return [
        Batch(1, "CSE-A", 72, 2, [1, 3, 6, 8]),
        Batch(2, "CSE-B", 68, 2, [1, 5, 7, 8]),
        Batch(3, "IT-A", 56, 4, [2, 3, 5, 9]),
        Batch(4, "ECE-A", 84, 4, [3, 7, 2, 6]),
        Batch(5, "AIML-A", 48, 6, [4, 8, 10, 9]),
        Batch(6, "CSE-Research", 40, 8, [4, 9, 10, 2]),
    ]


def get_room_list() -> List[Room]:
    """Return mock room inventory.

    Returns:
        List of 8 rooms with labs and lecture halls.
    """

    return [
        Room(1, "LH-101", 120, False, "Main Block"),
        Room(2, "LH-102", 90, False, "Main Block"),
        Room(3, "LH-201", 80, False, "Science Block"),
        Room(4, "LH-301", 200, False, "Auditorium Wing"),
        Room(5, "LAB-CS1", 60, True, "CS Block"),
        Room(6, "LAB-CS2", 50, True, "CS Block"),
        Room(7, "LAB-EC1", 45, True, "Electronics Block"),
        Room(8, "LH-205", 70, False, "Science Block"),
    ]


def get_faculty_list() -> List[Faculty]:
    """Return mock faculty with assignments and availability.

    Returns:
        List of 8 faculty records.
    """

    return [
        Faculty(1, "Dr. Aisha Khan", "Computer Science", "aisha.khan@univ.edu", list(range(1, 21)), [1, 8]),
        Faculty(2, "Dr. Rohan Mehta", "Computer Science", "rohan.mehta@univ.edu", list(range(6, 26)), [2, 9]),
        Faculty(3, "Prof. Neha Verma", "Information Technology", "neha.verma@univ.edu", [1, 2, 3, 6, 7, 8, 11, 12, 13, 16, 17, 18], [3]),
        Faculty(4, "Dr. Farhan Ali", "AI & DS", "farhan.ali@univ.edu", [4, 5, 9, 10, 14, 15, 19, 20, 24, 25], [4, 10]),
        Faculty(5, "Prof. Meera Iyer", "Computer Science", "meera.iyer@univ.edu", list(range(1, 26, 2)), [5]),
        Faculty(6, "Dr. Sandeep Rao", "Physics", "sandeep.rao@univ.edu", list(range(1, 16)), [6]),
        Faculty(7, "Prof. Arjun Das", "Electronics", "arjun.das@univ.edu", list(range(8, 26)), [7]),
        Faculty(8, "Dr. Kavita Nair", "Computer Science", "kavita.nair@univ.edu", [2, 3, 4, 7, 8, 9, 12, 13, 14, 17, 18, 19, 22, 23, 24], [8, 9]),
    ]


def get_timetable_entries() -> List[TimetableEntry]:
    """Return mock generated timetable entries.

    Returns:
        List of 30 scheduled timetable entries.
    """

    return [
        TimetableEntry(1, 1, 1, 1, 1), TimetableEntry(3, 3, 1, 2, 2), TimetableEntry(6, 6, 1, 5, 4),
        TimetableEntry(8, 1, 1, 8, 6), TimetableEntry(1, 1, 2, 1, 7), TimetableEntry(5, 5, 2, 2, 8),
        TimetableEntry(7, 7, 2, 7, 9), TimetableEntry(8, 8, 2, 8, 11), TimetableEntry(2, 2, 3, 3, 12),
        TimetableEntry(3, 3, 3, 2, 13), TimetableEntry(5, 5, 3, 1, 14), TimetableEntry(9, 2, 3, 3, 16),
        TimetableEntry(3, 3, 4, 2, 17), TimetableEntry(7, 7, 4, 7, 18), TimetableEntry(2, 2, 4, 1, 19),
        TimetableEntry(6, 6, 4, 5, 21), TimetableEntry(4, 4, 5, 4, 22), TimetableEntry(8, 8, 5, 8, 23),
        TimetableEntry(10, 4, 5, 6, 24), TimetableEntry(9, 2, 5, 3, 25), TimetableEntry(4, 4, 6, 4, 3),
        TimetableEntry(9, 2, 6, 3, 5), TimetableEntry(10, 4, 6, 6, 10), TimetableEntry(2, 2, 6, 1, 15),
        TimetableEntry(1, 1, 1, 1, 20), TimetableEntry(5, 5, 2, 2, 5), TimetableEntry(3, 3, 3, 3, 9),
        TimetableEntry(7, 7, 4, 7, 14), TimetableEntry(8, 8, 5, 8, 18), TimetableEntry(2, 2, 6, 1, 21),
    ]


def get_conflicts() -> List[Conflict]:
    """Return mock conflict records.

    Returns:
        List of 5 conflict entries.
    """

    return [
        Conflict("FACULTY_OVERLAP", "Dr. Rohan Mehta assigned to CS301 and CS450 at Tuesday 10:00.", "HIGH"),
        Conflict("ROOM_OVERLAP", "Room LH-101 assigned to two batches on Wednesday 11:00.", "HIGH"),
        Conflict("BATCH_OVERLAP", "Batch IT-A has CS305 and CS303 at the same slot.", "MEDIUM"),
        Conflict("UNSCHEDULED_LECTURE", "Cloud Computing requires one additional 3-hour lab block.", "MEDIUM"),
        Conflict("CONSTRAINT_VIOLATION", "Faculty compactness score below configured threshold for CSE-B.", "LOW"),
    ]


def get_recent_activity() -> List[str]:
    """Return recent user/system activity logs.

    Returns:
        List of 5 log entry strings.
    """

    return [
        "Imported 8 faculty records from faculty_seed.csv",
        "Updated room capacity for LH-201 to 80",
        "Constraint weights modified by Admin",
        "Generated timetable run #14",
        "Conflict report exported as conflicts_2026_04_18.csv",
    ]


def get_soft_constraint_weights() -> Dict[str, int]:
    """Return default soft constraint weights.

    Returns:
        Dictionary of named soft constraints and weights.
    """

    return {
        "Minimize Idle Time": 7,
        "Minimize Gaps Between Classes": 6,
        "Improve Schedule Compactness": 8,
        "Lab Priority Scheduling": 5,
    }
