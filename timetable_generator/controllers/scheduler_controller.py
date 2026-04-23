"""Scheduling controller that simulates timetable generation progress."""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

from PyQt5.QtCore import QEventLoop, QTimer

from timetable_generator.controllers.api_client import ApiClient

PROGRESS_STEPS: List[Tuple[int, str]] = [
    (10, "Initializing..."),
    (30, "Applying constraints..."),
    (55, "Running CSP Engine..."),
    (80, "Optimizing schedule..."),
    (100, "Done!"),
]


class SchedulerController:
    """Controller exposing a simulated scheduling engine execution."""

    def run(self, on_progress: Callable[[int, str], None]) -> Dict[str, int]:
        """Simulate scheduling process with timed progress updates.

        Args:
            on_progress: Callback receiving progress percent and status label.

        Returns:
            Summary dictionary with scheduled totals and conflicts.
        """

        loop = QEventLoop()
        api = ApiClient()

        def emit_step(index: int) -> None:
            if index >= len(PROGRESS_STEPS):
                loop.quit()
                return
            percent, message = PROGRESS_STEPS[index]
            on_progress(percent, message)
            QTimer.singleShot(450, lambda: emit_step(index + 1))

        QTimer.singleShot(50, lambda: emit_step(0))
        loop.exec_()
        result = api.post("/generate-timetable")
        return {
            "scheduled": result.get("timetable_count", 0),
            "total": result.get("timetable_count", 0) + result.get("conflict_count", 0),
            "conflicts": result.get("conflict_count", 0),
        }
