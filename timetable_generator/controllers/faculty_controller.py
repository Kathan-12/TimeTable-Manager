"""Faculty controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.controllers.api_client import ApiClient
from timetable_generator.models.faculty import Faculty


class FacultyController:
    """Controller handling faculty CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock faculty data."""

        self._api = ApiClient()

    def get_all(self) -> List[Faculty]:
        """Fetch all faculty records.

        Returns:
            List of Faculty objects.
        """

        payload = self._api.get("/faculty")
        items = payload.get("items", [])
        return [
            Faculty(
                id=item["id"],
                name=item["name"],
                department=item.get("department", ""),
                email=item.get("email", ""),
                available_slots=item.get("available_slots", []),
                assigned_courses=item.get("assigned_courses", []),
            )
            for item in items
        ]

    def get_by_id(self, item_id: int) -> Faculty | None:
        """Find a faculty record by identifier.

        Args:
            item_id: Faculty identifier.

        Returns:
            Matching Faculty object or None.
        """

        return next((item for item in self.get_all() if item.id == item_id), None)

    def add(self, faculty: Faculty) -> bool:
        """Add a faculty record.

        Args:
            faculty: Faculty model to add.

        Returns:
            True if added; False when duplicate id exists.
        """

        payload = {
            "name": faculty.name,
            "department": faculty.department,
            "email": faculty.email,
            "assigned_courses": faculty.assigned_courses,
        }
        self._api.post("/faculty", json_body=payload)
        return True

    def update(self, item_id: int, faculty: Faculty) -> bool:
        """Update an existing faculty record.

        Args:
            item_id: Existing faculty identifier.
            faculty: Updated faculty payload.

        Returns:
            True on success, False if item not found.
        """

        payload = {
            "name": faculty.name,
            "department": faculty.department,
            "email": faculty.email,
            "assigned_courses": faculty.assigned_courses,
        }
        self._api.put(f"/faculty/{item_id}", json_body=payload)
        return True

    def delete(self, item_id: int) -> bool:
        """Delete a faculty record by id.

        Args:
            item_id: Faculty identifier.

        Returns:
            True if removed, False otherwise.
        """

        self._api.delete(f"/faculty/{item_id}")
        return True

    def import_csv(self, filepath: str) -> Tuple[int, List[str]]:
        """Import faculty records from CSV file.

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
                data = {"entity": "faculty"}
                result = self._api.post("/import-csv", files=files, data=data)
                success_count = result.get("inserted", 0)
                errors = result.get("errors", [])
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
