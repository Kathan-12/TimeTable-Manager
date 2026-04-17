"""Dashboard view for high-level timetable statistics and shortcuts."""

from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.components.stat_card import StatCard

TITLE_TEXT = "Dashboard"
QUICK_ACTIONS = "Quick Actions"


class DashboardView(QWidget):
    """Home screen showing system summary, quick actions, and activity logs."""

    navigate_requested = pyqtSignal(str)

    def __init__(self, faculty_count: int, course_count: int, batch_count: int, room_count: int, activities: list[str]) -> None:
        """Initialize dashboard with precomputed statistics.

        Args:
            faculty_count: Total faculty records.
            course_count: Total courses.
            batch_count: Total batches.
            room_count: Total rooms.
            activities: Recent activity lines.
        """

        super().__init__()
        self._faculty_count = faculty_count
        self._course_count = course_count
        self._batch_count = batch_count
        self._room_count = room_count
        self._activities = activities
        self._build_ui()

    def _build_ui(self) -> None:
        """Render dashboard cards, actions, and activity list.

        Returns:
            None.
        """

        root = QVBoxLayout(self)

        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        row_one = QHBoxLayout()
        row_one.addWidget(StatCard("Total Faculty", self._faculty_count, "👤", "#6c63ff"))
        row_one.addWidget(StatCard("Total Courses", self._course_count, "📚", "#00d084"))
        row_one.addWidget(StatCard("Total Batches", self._batch_count, "🏷️", "#f5a623"))
        row_one.addWidget(StatCard("Total Rooms", self._room_count, "🏫", "#4da3ff"))
        root.addLayout(row_one)

        row_two = QHBoxLayout()
        row_two.addWidget(StatCard("Scheduled Lectures", "42 / 50", "✅", "#00d084"))
        row_two.addWidget(StatCard("Unresolved Conflicts", 3, "⚠️", "#ff4d6a"))
        root.addLayout(row_two)

        quick_actions_label = QLabel(QUICK_ACTIONS)
        quick_actions_label.setObjectName("heading")
        root.addWidget(quick_actions_label)

        actions = QHBoxLayout()
        generate_button = QPushButton("Generate Timetable")
        generate_button.setProperty("primary", "true")
        generate_button.clicked.connect(lambda: self.navigate_requested.emit("generate"))

        timetable_button = QPushButton("View Timetable")
        timetable_button.clicked.connect(lambda: self.navigate_requested.emit("timetable"))

        conflicts_button = QPushButton("View Conflicts")
        conflicts_button.clicked.connect(lambda: self.navigate_requested.emit("conflicts"))

        actions.addWidget(generate_button)
        actions.addWidget(timetable_button)
        actions.addWidget(conflicts_button)
        root.addLayout(actions)

        activity_title = QLabel("Recent Activity")
        activity_title.setObjectName("heading")
        root.addWidget(activity_title)

        activity_list = QListWidget()
        for line in self._activities[:5]:
            activity_list.addItem(line)
        root.addWidget(activity_list)
