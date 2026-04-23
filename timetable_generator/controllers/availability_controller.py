"""Availability controller for faculty availability management."""

from __future__ import annotations

from typing import Dict, List, Tuple

from timetable_generator.controllers.api_client import ApiClient
from timetable_generator.models.faculty import Faculty


class AvailabilityController:
    """Controller handling faculty availability assignments."""

    def __init__(self) -> None:
        """Initialize controller and load mock faculty data."""

        self._api = ApiClient()

    def get_all(self) -> List[Faculty]:
        """Return all faculty with availability values.

        Returns:
            List of Faculty models.
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
        """Get one faculty by identifier.

        Args:
            item_id: Faculty identifier.

        Returns:
            Matching Faculty or None.
        """

        return next((item for item in self.get_all() if item.id == item_id), None)

    def add(self, faculty: Faculty) -> bool:
        """Add a faculty availability profile.

        Args:
            faculty: Faculty model.

        Returns:
            True if added, otherwise False.
        """

        return False

    def update(self, item_id: int, faculty: Faculty) -> bool:
        """Update an existing faculty profile.

        Args:
            item_id: Faculty identifier.
            faculty: Updated Faculty payload.

        Returns:
            True on success, otherwise False.
        """

        return False

    def delete(self, item_id: int) -> bool:
        """Delete faculty availability profile.

        Args:
            item_id: Faculty identifier.

        Returns:
            True on success, otherwise False.
        """

        return False

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

        self._api.put(f"/availability/{faculty_id}", json_body=slot_ids)
        return True

    def as_mapping(self) -> Dict[int, List[int]]:
        """Return availability map keyed by faculty id.

        Returns:
            Mapping of faculty id to available slot IDs.
        """

        return {faculty.id: list(faculty.available_slots) for faculty in self.get_all()}
