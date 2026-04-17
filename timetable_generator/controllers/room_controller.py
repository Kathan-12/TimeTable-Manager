"""Room controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.models.room import Room
from timetable_generator.utils import mock_data


class RoomController:
    """Controller handling room CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock room data."""

        self.data: List[Room] = mock_data.get_room_list()

    def get_all(self) -> List[Room]:
        """Fetch all room records.

        Returns:
            List of Room objects.
        """

        return list(self.data)

    def get_by_id(self, item_id: int) -> Room | None:
        """Find a room by identifier.

        Args:
            item_id: Room identifier.

        Returns:
            Matching Room model or None.
        """

        return next((item for item in self.data if item.id == item_id), None)

    def add(self, room: Room) -> bool:
        """Add a room record.

        Args:
            room: Room payload.

        Returns:
            True if inserted; False on duplicate id.
        """

        if self.get_by_id(room.id) is not None:
            return False
        self.data.append(room)
        return True

    def update(self, item_id: int, room: Room) -> bool:
        """Update an existing room.

        Args:
            item_id: Existing room id.
            room: Updated room model.

        Returns:
            True on success else False.
        """

        for idx, item in enumerate(self.data):
            if item.id == item_id:
                self.data[idx] = room
                return True
        return False

    def delete(self, item_id: int) -> bool:
        """Delete a room record.

        Args:
            item_id: Room identifier.

        Returns:
            True if deleted else False.
        """

        before = len(self.data)
        self.data = [item for item in self.data if item.id != item_id]
        return len(self.data) < before

    def import_csv(self, filepath: str) -> Tuple[int, List[str]]:
        """Import room records from CSV.

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
                        model = Room(
                            id=new_id,
                            room_number=row.get("room_number", "").strip(),
                            building=row.get("building", "").strip(),
                            capacity=int(row.get("capacity", 1)),
                            is_lab=row.get("is_lab", "false").lower() == "true",
                        )
                        if not model.room_number:
                            raise ValueError("Missing required column: room_number")
                        self.data.append(model)
                        success_count += 1
                    except Exception as exc:
                        errors.append(f"Row {row_no}: {exc}")
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
