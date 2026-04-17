"""Availability controller for faculty availability management."""

from __future__ import annotations

from typing import Dict, List, Tuple

from timetable_generator.models.faculty import Faculty
from timetable_generator.utils import mock_data


class AvailabilityController:
    """Controller handling faculty availability assignments."""

    def __init__(self) -> None:
        """Initialize controller and load mock faculty data."""

        self.data: List[Faculty] = mock_data.get_faculty_list()

    def get_all(self) -> List[Faculty]:
        """Return all faculty with availability values.

        Returns:
            List of Faculty models.
        """

        return list(self.data)

    def get_by_id(self, item_id: int) -> Faculty | None:
        """Get one faculty by identifier.

        Args:
            item_id: Faculty identifier.

        Returns:
            Matching Faculty or None.
        """

        return next((item for item in self.data if item.id == item_id), None)

    def add(self, faculty: Faculty) -> bool:
        """Add a faculty availability profile.

        Args:
            faculty: Faculty model.

        Returns:
            True if added, otherwise False.
        """

        if self.get_by_id(faculty.id) is not None:
            return False
        self.data.append(faculty)
        return True

    def update(self, item_id: int, faculty: Faculty) -> bool:
        """Update an existing faculty profile.

        Args:
            item_id: Faculty identifier.
            faculty: Updated Faculty payload.

        Returns:
            True on success, otherwise False.
        """

        for idx, item in enumerate(self.data):
            if item.id == item_id:
                self.data[idx] = faculty
                return True
        return False

    def delete(self, item_id: int) -> bool:
        """Delete faculty availability profile.

        Args:
            item_id: Faculty identifier.

        Returns:
            True on success, otherwise False.
        """

        before = len(self.data)
        self.data = [item for item in self.data if item.id != item_id]
        return len(self.data) < before

    def import_csv(self, filepath: str) -> Tuple[int, List[str]]:
        """Placeholder CSV import for availability.

        Args:
            filepath: Input CSV path.

        Returns:
            Tuple with zero imports and informational message.
        """

        return 0, [f"Availability CSV import is currently stubbed: {filepath}"]

    def set_faculty_availability(self, faculty_id: int, slot_ids: List[int]) -> bool:
        """Replace the selected faculty availability slots.

        Args:
            faculty_id: Target faculty id.
            slot_ids: List of selected timeslot IDs.

        Returns:
            True if faculty exists and was updated.
        """

        faculty = self.get_by_id(faculty_id)
        if faculty is None:
            return False
        faculty.available_slots = sorted(set(slot_ids))
        return True

    def as_mapping(self) -> Dict[int, List[int]]:
        """Return availability map keyed by faculty id.

        Returns:
            Mapping of faculty id to available slot IDs.
        """

        return {faculty.id: list(faculty.available_slots) for faculty in self.data}
