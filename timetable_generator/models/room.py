"""Room model definitions."""

from dataclasses import dataclass


@dataclass(slots=True)
class Room:
    """Represents a physical classroom or lab.

    Attributes:
        id: Unique room identifier.
        room_number: Room number label.
        capacity: Maximum room occupancy.
        is_lab: Whether room is a lab.
        building: Building name.
    """

    id: int
    room_number: str
    capacity: int
    is_lab: bool
    building: str
