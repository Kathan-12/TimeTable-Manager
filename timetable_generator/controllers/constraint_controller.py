"""Constraint controller for scheduling weight configuration."""

from __future__ import annotations

from typing import Dict, List, Tuple

from timetable_generator.utils import mock_data

HARD_CONSTRAINTS: List[str] = [
    "No Faculty Overlap",
    "No Batch Overlap",
    "No Room Overlap",
    "Room Capacity Must Match Batch Size",
    "Lab Rooms Only for Lab Sessions",
    "No Back-to-Back Faculty Lectures",
    "Faculty Availability Must Be Respected",
]


class ConstraintController:
    """Controller handling hard and soft scheduling constraints."""

    def __init__(self) -> None:
        """Initialize controller state with default weights."""

        self.data: Dict[str, int] = mock_data.get_soft_constraint_weights()

    def get_all(self) -> Dict[str, int]:
        """Return all soft constraint weights.

        Returns:
            Dictionary mapping constraint name to weight.
        """

        return dict(self.data)

    def get_by_id(self, key: int) -> Dict[str, int]:
        """Compatibility accessor returning all weights.

        Args:
            key: Unused numeric key placeholder.

        Returns:
            Dictionary of current soft constraints.
        """

        return dict(self.data)

    def add(self, constraint: Dict[str, int]) -> bool:
        """Merge additional soft constraints.

        Args:
            constraint: Constraint dictionary to merge.

        Returns:
            Always True for stub behavior.
        """

        self.data.update(constraint)
        return True

    def update(self, key: int, constraint: Dict[str, int]) -> bool:
        """Replace soft constraint values.

        Args:
            key: Unused key placeholder.
            constraint: New constraint mapping.

        Returns:
            True if mapping is non-empty.
        """

        if not constraint:
            return False
        self.data = dict(constraint)
        return True

    def delete(self, key: int) -> bool:
        """Reset all soft constraints to defaults.

        Args:
            key: Unused key placeholder.

        Returns:
            True always.
        """

        self.data = mock_data.get_soft_constraint_weights()
        return True

    def import_csv(self, filepath: str) -> Tuple[int, List[str]]:
        """Placeholder CSV import for constraints.

        Args:
            filepath: Input CSV path.

        Returns:
            Tuple with zero imports and informational message.
        """

        return 0, [f"Constraint CSV import is currently stubbed: {filepath}"]

    def get_hard_constraints(self) -> List[str]:
        """Return immutable hard constraints list.

        Returns:
            List of hard constraint labels.
        """

        return list(HARD_CONSTRAINTS)
