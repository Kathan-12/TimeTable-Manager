"""Course controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.models.course import Course
from timetable_generator.utils import mock_data


class CourseController:
    """Controller handling course CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock course data."""

        self.data: List[Course] = mock_data.get_course_list()

    def get_all(self) -> List[Course]:
        """Fetch all course records.

        Returns:
            List of Course objects.
        """

        return list(self.data)

    def get_by_id(self, item_id: int) -> Course | None:
        """Find a course by id.

        Args:
            item_id: Course identifier.

        Returns:
            Matching Course or None.
        """

        return next((item for item in self.data if item.id == item_id), None)

    def add(self, course: Course) -> bool:
        """Add a course record.

        Args:
            course: Course model.

        Returns:
            True on success; False when duplicate id exists.
        """

        if self.get_by_id(course.id) is not None:
            return False
        self.data.append(course)
        return True

    def update(self, item_id: int, course: Course) -> bool:
        """Update an existing course.

        Args:
            item_id: Existing course id.
            course: Updated course model.

        Returns:
            True on success, False if not found.
        """

        for idx, item in enumerate(self.data):
            if item.id == item_id:
                self.data[idx] = course
                return True
        return False

    def delete(self, item_id: int) -> bool:
        """Delete a course record.

        Args:
            item_id: Course identifier.

        Returns:
            True if removed else False.
        """

        before = len(self.data)
        self.data = [item for item in self.data if item.id != item_id]
        return len(self.data) < before

    def import_csv(self, filepath: str) -> Tuple[int, List[str]]:
        """Import course records from CSV file.

        Args:
            filepath: CSV file path.

        Returns:
            Tuple of (success_count, error_messages).
        """

        success_count = 0
        errors: List[str] = []
        try:
            with open(filepath, newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row_no, row in enumerate(reader, start=2):
                    try:
                        new_id = max((item.id for item in self.data), default=0) + 1
                        model = Course(
                            id=new_id,
                            code=row.get("code", "").strip(),
                            name=row.get("name", "").strip(),
                            lectures_per_week=int(row.get("lectures_per_week", 1)),
                            is_lab=row.get("is_lab", "false").lower() == "true",
                            duration_hours=float(row.get("duration_hours", 1.0)),
                        )
                        if not model.code or not model.name:
                            raise ValueError("Missing required columns: code/name")
                        self.data.append(model)
                        success_count += 1
                    except Exception as exc:
                        errors.append(f"Row {row_no}: {exc}")
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
