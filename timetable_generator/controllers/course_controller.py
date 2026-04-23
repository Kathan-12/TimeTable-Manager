"""Course controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.controllers.api_client import ApiClient
from timetable_generator.models.course import Course


class CourseController:
    """Controller handling course CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock course data."""

        self._api = ApiClient()

    def get_all(self) -> List[Course]:
        """Fetch all course records.

        Returns:
            List of Course objects.
        """

        payload = self._api.get("/course")
        items = payload.get("items", [])
        return [
            Course(
                id=item["id"],
                code=item.get("code", ""),
                name=item.get("name", ""),
                lectures_per_week=item.get("lectures_per_week", 1),
                is_lab=item.get("is_lab", False),
                duration_hours=item.get("duration_hours", 1.0),
            )
            for item in items
        ]

    def get_by_id(self, item_id: int) -> Course | None:
        """Find a course by id.

        Args:
            item_id: Course identifier.

        Returns:
            Matching Course or None.
        """

        return next((item for item in self.get_all() if item.id == item_id), None)

    def add(self, course: Course) -> bool:
        """Add a course record.

        Args:
            course: Course model.

        Returns:
            True on success; False when duplicate id exists.
        """

        payload = {
            "name": course.name,
            "code": course.code,
            "lectures_per_week": course.lectures_per_week,
            "is_lab": course.is_lab,
            "duration_hours": course.duration_hours,
        }
        self._api.post("/course", json_body=payload)
        return True

    def update(self, item_id: int, course: Course) -> bool:
        """Update an existing course.

        Args:
            item_id: Existing course id.
            course: Updated course model.

        Returns:
            True on success, False if not found.
        """

        payload = {
            "name": course.name,
            "code": course.code,
            "lectures_per_week": course.lectures_per_week,
            "is_lab": course.is_lab,
            "duration_hours": course.duration_hours,
        }
        self._api.put(f"/course/{item_id}", json_body=payload)
        return True

    def delete(self, item_id: int) -> bool:
        """Delete a course record.

        Args:
            item_id: Course identifier.

        Returns:
            True if removed else False.
        """

        self._api.delete(f"/course/{item_id}")
        return True

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
                files = {"file": (filepath, handle, "text/csv")}
                data = {"entity": "course"}
                result = self._api.post("/import-csv", files=files, data=data)
                success_count = result.get("inserted", 0)
                errors = result.get("errors", [])
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
