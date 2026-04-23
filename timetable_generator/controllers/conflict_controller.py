"""Controller for conflict retrieval."""

from __future__ import annotations

from typing import List

from timetable_generator.controllers.api_client import ApiClient
from timetable_generator.models.conflict import Conflict


class ConflictController:
    """Fetch conflicts from the backend API."""

    def __init__(self) -> None:
        self._api = ApiClient()

    def get_all(self) -> List[Conflict]:
        payload = self._api.get("/conflicts")
        items = payload.get("items", [])
        conflicts: List[Conflict] = []
        for item in items:
            conflicts.append(
                Conflict(
                    type=item.get("type", "UNKNOWN"),
                    description=item.get("description", ""),
                    severity=_severity_from_type(item.get("type", "")),
                )
            )
        return conflicts


def _severity_from_type(conflict_type: str) -> str:
    upper = conflict_type.upper()
    if "UNSCHEDULED" in upper or "OVERLAP" in upper:
        return "HIGH"
    if "CONSTRAINT" in upper:
        return "MEDIUM"
    return "LOW"
