"""Batch controller providing mock CRUD operations."""

from __future__ import annotations

import csv
from typing import List, Tuple

from timetable_generator.models.batch import Batch
from timetable_generator.utils import mock_data


class BatchController:
    """Controller handling batch CRUD and import operations."""

    def __init__(self) -> None:
        """Initialize controller and load mock batch data."""

        self.data: List[Batch] = mock_data.get_batch_list()

    def get_all(self) -> List[Batch]:
        """Fetch all batch records.

        Returns:
            List of Batch objects.
        """

        return list(self.data)

    def get_by_id(self, item_id: int) -> Batch | None:
        """Find a batch by identifier.

        Args:
            item_id: Batch identifier.

        Returns:
            Matching Batch model or None.
        """

        return next((item for item in self.data if item.id == item_id), None)

    def add(self, batch: Batch) -> bool:
        """Add a batch record.

        Args:
            batch: Batch payload.

        Returns:
            True if inserted; False on duplicate id.
        """

        if self.get_by_id(batch.id) is not None:
            return False
        self.data.append(batch)
        return True

    def update(self, item_id: int, batch: Batch) -> bool:
        """Update an existing batch.

        Args:
            item_id: Existing batch id.
            batch: Updated batch model.

        Returns:
            True on success else False.
        """

        for idx, item in enumerate(self.data):
            if item.id == item_id:
                self.data[idx] = batch
                return True
        return False

    def delete(self, item_id: int) -> bool:
        """Delete a batch record.

        Args:
            item_id: Batch identifier.

        Returns:
            True if deleted else False.
        """

        before = len(self.data)
        self.data = [item for item in self.data if item.id != item_id]
        return len(self.data) < before

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
                reader = csv.DictReader(handle)
                for row_no, row in enumerate(reader, start=2):
                    try:
                        new_id = max((item.id for item in self.data), default=0) + 1
                        model = Batch(
                            id=new_id,
                            name=row.get("name", "").strip(),
                            size=int(row.get("size", 1)),
                            semester=int(row.get("semester", 1)),
                            courses=[],
                        )
                        if not model.name:
                            raise ValueError("Missing required column: name")
                        self.data.append(model)
                        success_count += 1
                    except Exception as exc:
                        errors.append(f"Row {row_no}: {exc}")
        except Exception as exc:
            errors.append(str(exc))
        return success_count, errors
