"""Batch controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.controllers.api_client import ApiClient
from timetable_generator.models.batch import Batch


class BatchController:
    """Controller handling batch CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock batch data."""

        self._api = ApiClient()

    def get_all(self) -> List[Batch]:
        """Fetch all batch records.

        Returns:
            List of Batch objects.
        """

        payload = self._api.get("/batch")
        items = payload.get("items", [])
        return [
            Batch(
                id=item["id"],
                name=item.get("name", ""),
                size=item.get("size", 0),
                semester=item.get("semester", 1),
                courses=item.get("courses", []),
            )
            for item in items
        ]

    def get_by_id(self, item_id: int) -> Batch | None:
        """Find a batch by identifier.

        Args:
            item_id: Batch identifier.

        Returns:
            Matching Batch model or None.
        """

        return next((item for item in self.get_all() if item.id == item_id), None)

    def add(self, batch: Batch) -> bool:
        """Add a batch record.

        Args:
            batch: Batch payload.

        Returns:
            True if inserted; False on duplicate id.
        """

        payload = {
            "name": batch.name,
            "size": batch.size,
            "semester": batch.semester,
            "courses": batch.courses,
        }
        self._api.post("/batch", json_body=payload)
        return True

    def update(self, item_id: int, batch: Batch) -> bool:
        """Update an existing batch.

        Args:
            item_id: Existing batch id.
            batch: Updated batch model.

        Returns:
            True on success else False.
        """

        payload = {
            "name": batch.name,
            "size": batch.size,
            "semester": batch.semester,
            "courses": batch.courses,
        }
        self._api.put(f"/batch/{item_id}", json_body=payload)
        return True

    def delete(self, item_id: int) -> bool:
        """Delete a batch record.

        Args:
            item_id: Batch identifier.

        Returns:
            True if deleted else False.
        """

        self._api.delete(f"/batch/{item_id}")
        return True

    def import_csv(self, filepath: str) -> Tuple[int, List[str]]:
        """Import batch records from CSV.

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
                data = {"entity": "batch"}
                result = self._api.post("/import-csv", files=files, data=data)
                success_count = result.get("inserted", 0)
                errors = result.get("errors", [])
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
