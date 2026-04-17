"""Timetable generation trigger and progress display view."""

from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.controllers.scheduler_controller import SchedulerController

TITLE_TEXT = "Generate Timetable"
CHECK_ITEMS = [
    "Faculty data loaded",
    "Courses defined",
    "Batches configured",
    "Rooms available",
    "Time slots defined",
    "Constraints configured",
]


class GenerateView(QWidget):
    """Screen used to run mock scheduling and display progress and summary."""

    navigate_requested = pyqtSignal(str)

    def __init__(self, scheduler_controller: SchedulerController) -> None:
        """Initialize generation view.

        Args:
            scheduler_controller: Scheduler controller instance.
        """

        super().__init__()
        self._scheduler_controller = scheduler_controller
        self._progress: QProgressBar
        self._status: QLabel
        self._summary: QLabel
        self._view_timetable_btn: QPushButton
        self._view_conflicts_btn: QPushButton
        self._build_ui()

    def _build_ui(self) -> None:
        """Render checklist, generate controls, and result summary widgets.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        checklist = QFrame()
        checklist.setObjectName("CardPanel")
        checklist_layout = QVBoxLayout(checklist)
        for item in CHECK_ITEMS:
            checklist_layout.addWidget(QLabel(f"✔ {item}"))
        root.addWidget(checklist)

        self._generate_btn = QPushButton("Generate Timetable")
        self._generate_btn.setProperty("primary", "true")
        self._generate_btn.clicked.connect(self._generate)
        root.addWidget(self._generate_btn)

        self._progress = QProgressBar()
        self._progress.setValue(0)
        self._status = QLabel("Idle")
        root.addWidget(self._progress)
        root.addWidget(self._status)

        self._summary = QLabel("Result summary will appear here.")
        self._summary.setWordWrap(True)
        root.addWidget(self._summary)

        summary_actions = QHBoxLayout()
        self._view_timetable_btn = QPushButton("View Timetable")
        self._view_timetable_btn.clicked.connect(lambda: self.navigate_requested.emit("timetable"))
        self._view_conflicts_btn = QPushButton("View Conflicts")
        self._view_conflicts_btn.clicked.connect(lambda: self.navigate_requested.emit("conflicts"))
        regenerate_btn = QPushButton("Regenerate")
        regenerate_btn.clicked.connect(self._generate)

        summary_actions.addWidget(self._view_timetable_btn)
        summary_actions.addWidget(self._view_conflicts_btn)
        summary_actions.addWidget(regenerate_btn)
        root.addLayout(summary_actions)

    def _on_progress(self, value: int, message: str) -> None:
        """Update progress widgets from scheduler callback.

        Args:
            value: Progress percentage.
            message: Status message.

        Returns:
            None.
        """

        self._progress.setValue(value)
        self._status.setText(message)

    def _generate(self) -> None:
        """Run simulated generation process and display summary.

        Returns:
            None.
        """

        try:
            self._generate_btn.setEnabled(False)
            result = self._scheduler_controller.run(self._on_progress)
            self._summary.setText(
                f"Scheduled: {result['scheduled']} / {result['total']} lectures\n"
                f"Unresolved Conflicts: {result['conflicts']}"
            )
            self._generate_btn.setEnabled(True)
        except Exception as exc:
            self._generate_btn.setEnabled(True)
            QMessageBox.critical(self, "Scheduler Error", f"Unable to generate timetable: {exc}")
