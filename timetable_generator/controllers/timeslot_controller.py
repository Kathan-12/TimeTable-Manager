"""TimeSlot controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.models.timeslot import TimeSlot
from timetable_generator.utils import mock_data


class TimeSlotController:
    """Controller handling timeslot CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock timeslot data."""

        self.data: List[TimeSlot] = mock_data.get_timeslot_list()

    def get_all(self) -> List[TimeSlot]:
        """Fetch all timeslot records.

        Returns:
            List of TimeSlot objects.
        """

        return list(self.data)

    def get_by_id(self, item_id: int) -> TimeSlot | None:
        """Find a timeslot by id.

        Args:
            item_id: TimeSlot identifier.

        Returns:
            Matching TimeSlot or None.
        """

        return next((item for item in self.data if item.id == item_id), None)

    def add(self, slot: TimeSlot) -> bool:
        """Add a timeslot record.

        Args:
            slot: TimeSlot payload.

        Returns:
            True on insert; False on duplicate id.
        """

        if self.get_by_id(slot.id) is not None:
            return False
        self.data.append(slot)
        return True

    def update(self, item_id: int, slot: TimeSlot) -> bool:
        """Update an existing timeslot.

        Args:
            item_id: Existing timeslot id.
            slot: Updated TimeSlot payload.

        Returns:
            True on success else False.
        """

        for idx, item in enumerate(self.data):
            if item.id == item_id:
                self.data[idx] = slot
                return True
        return False

    def delete(self, item_id: int) -> bool:
        """Delete a timeslot record.

        Args:
            item_id: TimeSlot identifier.

        Returns:
            True if removed else False.
        """

        before = len(self.data)
        self.data = [item for item in self.data if item.id != item_id]
        return len(self.data) < before

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
                reader = csv.DictReader(handle)
                for row_no, row in enumerate(reader, start=2):
                    try:
                        new_id = max((item.id for item in self.data), default=0) + 1
                        model = TimeSlot(
                            id=new_id,
                            day=row.get("day", "Monday").strip(),
                            start_time=row.get("start_time", "09:00").strip(),
                            end_time=row.get("end_time", "10:00").strip(),
                        )
                        self.data.append(model)
                        success_count += 1
                    except Exception as exc:
                        errors.append(f"Row {row_no}: {exc}")
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
