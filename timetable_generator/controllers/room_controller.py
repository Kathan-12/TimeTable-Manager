"""Room controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.controllers.api_client import ApiClient
from timetable_generator.models.room import Room


class RoomController:
    """Controller handling room CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock room data."""

        self._api = ApiClient()

    def get_all(self) -> List[Room]:
        """Fetch all room records.

        Returns:
            List of Room objects.
        """

        payload = self._api.get("/room")
        items = payload.get("items", [])
        return [
            Room(
                id=item["id"],
                room_number=item.get("room_number", item.get("name", "")),
                building=item.get("building", ""),
                capacity=item.get("capacity", 0),
                is_lab=item.get("is_lab", False),
            )
            for item in items
        ]

    def get_by_id(self, item_id: int) -> Room | None:
        """Find a room by identifier.

        Args:
            item_id: Room identifier.

        Returns:
            Matching Room model or None.
        """

        return next((item for item in self.get_all() if item.id == item_id), None)

    def add(self, room: Room) -> bool:
        """Add a room record.

        Args:
            room: Room payload.

        Returns:
            True if inserted; False on duplicate id.
        """

        payload = {
            "name": room.room_number,
            "room_number": room.room_number,
            "building": room.building,
            "capacity": room.capacity,
            "is_lab": room.is_lab,
        }
        self._api.post("/room", json_body=payload)
        return True

    def update(self, item_id: int, room: Room) -> bool:
        """Update an existing room.

        Args:
            item_id: Existing room id.
            room: Updated room model.

        Returns:
            True on success else False.
        """

        payload = {
            "name": room.room_number,
            "room_number": room.room_number,
            "building": room.building,
            "capacity": room.capacity,
            "is_lab": room.is_lab,
        }
        self._api.put(f"/room/{item_id}", json_body=payload)
        return True

    def delete(self, item_id: int) -> bool:
        """Delete a room record.

        Args:
            item_id: Room identifier.

        Returns:
            True if deleted else False.
        """

        self._api.delete(f"/room/{item_id}")
        return True

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
                files = {"file": (filepath, handle, "text/csv")}
                data = {"entity": "room"}
                result = self._api.post("/import-csv", files=files, data=data)
                success_count = result.get("inserted", 0)
                errors = result.get("errors", [])
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
