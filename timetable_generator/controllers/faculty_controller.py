"""Faculty controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.models.faculty import Faculty
from timetable_generator.utils import mock_data


class FacultyController:
    """Controller handling faculty CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock faculty data."""

        self.data: List[Faculty] = mock_data.get_faculty_list()

    def get_all(self) -> List[Faculty]:
        """Fetch all faculty records.

        Returns:
            List of Faculty objects.
        """

        return list(self.data)

    def get_by_id(self, item_id: int) -> Faculty | None:
        """Find a faculty record by identifier.

        Args:
            item_id: Faculty identifier.

        Returns:
            Matching Faculty object or None.
        """

        return next((item for item in self.data if item.id == item_id), None)

    def add(self, faculty: Faculty) -> bool:
        """Add a faculty record.

        Args:
            faculty: Faculty model to add.

        Returns:
            True if added; False when duplicate id exists.
        """

        if self.get_by_id(faculty.id) is not None:
            return False
        self.data.append(faculty)
        return True

    def update(self, item_id: int, faculty: Faculty) -> bool:
        """Update an existing faculty record.

        Args:
            item_id: Existing faculty identifier.
            faculty: Updated faculty payload.

        Returns:
            True on success, False if item not found.
        """

        for idx, item in enumerate(self.data):
            if item.id == item_id:
                self.data[idx] = faculty
                return True
        return False

    def delete(self, item_id: int) -> bool:
        """Delete a faculty record by id.

        Args:
            item_id: Faculty identifier.

        Returns:
            True if removed, False otherwise.
        """

        before = len(self.data)
        self.data = [item for item in self.data if item.id != item_id]
        return len(self.data) < before

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
                reader = csv.DictReader(handle)
                for row_no, row in enumerate(reader, start=2):
                    try:
                        new_id = max((item.id for item in self.data), default=0) + 1
                        record = Faculty(
                            id=new_id,
                            name=row.get("name", "").strip(),
                            department=row.get("department", "").strip(),
                            email=row.get("email", "").strip(),
                            available_slots=[],
                            assigned_courses=[],
                        )
                        if not record.name or not record.department or not record.email:
                            raise ValueError("Missing required columns: name/department/email")
                        self.data.append(record)
                        success_count += 1
                    except Exception as exc:
                        errors.append(f"Row {row_no}: {exc}")
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
