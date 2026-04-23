"""TimeSlot controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.controllers.api_client import ApiClient
from timetable_generator.models.timeslot import TimeSlot


class TimeSlotController:
    """Controller handling timeslot CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock timeslot data."""

        self._api = ApiClient()

    def get_all(self) -> List[TimeSlot]:
        """Fetch all timeslot records.

        Returns:
            List of TimeSlot objects.
        """

        payload = self._api.get("/timeslot")
        items = payload.get("items", [])
        return [
            TimeSlot(
                id=item["id"],
                day=item.get("day", ""),
                start_time=item.get("start_time", ""),
                end_time=item.get("end_time", ""),
            )
            for item in items
        ]

    def get_by_id(self, item_id: int) -> TimeSlot | None:
        """Find a timeslot by id.

        Args:
            item_id: TimeSlot identifier.

        Returns:
            Matching TimeSlot or None.
        """

        return next((item for item in self.get_all() if item.id == item_id), None)

    def add(self, slot: TimeSlot) -> bool:
        """Add a timeslot record.

        Args:
            slot: TimeSlot payload.

        Returns:
            True on insert; False on duplicate id.
        """

        payload = {
            "day": slot.day,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        }
        self._api.post("/timeslot", json_body=payload)
        return True

    def update(self, item_id: int, slot: TimeSlot) -> bool:
        """Update an existing timeslot.

        Args:
            item_id: Existing timeslot id.
            slot: Updated TimeSlot payload.

        Returns:
            True on success else False.
        """

        payload = {
            "day": slot.day,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        }
        self._api.put(f"/timeslot/{item_id}", json_body=payload)
        return True

    def delete(self, item_id: int) -> bool:
        """Delete a timeslot record.

        Args:
            item_id: TimeSlot identifier.

        Returns:
            True if removed else False.
        """

        self._api.delete(f"/timeslot/{item_id}")
        return True

    def import_csv(self, filepath: str) -> Tuple[int, List[str]]:
        """Import timeslot records from CSV.

        Args:
            filepath: CSV path.

        Returns:
            Tuple of (success_count, error_messages).
        """

        success_count = 0
        errors: List[str] = []
        try:
            with open(filepath, newline="", encoding="utf-8") as handle:
                files = {"file": (filepath, handle, "text/csv")}
                data = {"entity": "timeslot"}
                result = self._api.post("/import-csv", files=files, data=data)
                success_count = result.get("inserted", 0)
                errors = result.get("errors", [])
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
