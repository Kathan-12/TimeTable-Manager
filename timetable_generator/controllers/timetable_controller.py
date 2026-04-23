"""Controller for timetable retrieval."""

from __future__ import annotations

from typing import Dict, List

from timetable_generator.controllers.api_client import ApiClient


class TimetableController:
    """Fetch timetable entries from the backend API."""

    def __init__(self) -> None:
        self._api = ApiClient()

    def get_by_batch(self, batch_id: int) -> List[Dict[str, str]]:
        payload = self._api.get(f"/timetable/batch/{batch_id}")
        return payload.get("items", [])

    def get_by_faculty(self, faculty_id: int) -> List[Dict[str, str]]:
        payload = self._api.get(f"/timetable/faculty/{faculty_id}")
        return payload.get("items", [])

    def get_by_room(self, room_id: int) -> List[Dict[str, str]]:
        payload = self._api.get(f"/timetable/room/{room_id}")
        return payload.get("items", [])
