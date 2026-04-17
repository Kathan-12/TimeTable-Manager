"""Sidebar navigation component for main application routing."""

from __future__ import annotations

from typing import Dict, List, Tuple

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QButtonGroup, QLabel, QToolButton, QVBoxLayout, QWidget

APP_NAME = "TT Generator"
VERSION_TEXT = "v1.0.0"
NAV_ITEMS: List[Tuple[str, str]] = [
    ("dashboard", "🏠 Dashboard"),
    ("faculty", "👤 Faculty"),
    ("courses", "📚 Courses"),
    ("batches", "🏷️ Batches"),
    ("rooms", "🏫 Rooms"),
    ("timeslots", "🕐 Time Slots"),
    ("availability", "📅 Availability"),
    ("constraints", "⚙️ Constraints"),
    ("generate", "▶ Generate"),
    ("timetable", "📊 Timetable"),
    ("conflicts", "⚠️ Conflicts"),
    ("export", "📤 Export"),
]


class Sidebar(QWidget):
    """Application sidebar that emits navigation target on item selection."""

    navigate = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize sidebar layout and navigation buttons."""

        super().__init__()
        self.setFixedWidth(220)
        self._buttons: Dict[str, QToolButton] = {}
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._build_ui()

    def _build_ui(self) -> None:
        """Create sidebar static sections and nav button list.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        logo = QLabel(APP_NAME)
        logo.setObjectName("sidebarLogo")
        root.addWidget(logo)

        for key, label in NAV_ITEMS:
            button = QToolButton()
            button.setText(label)
            button.setCheckable(True)
            button.setToolButtonStyle(3)
            button.setObjectName("sidebarButton")
            button.clicked.connect(lambda checked, screen=key: self._on_navigate(screen))
            self._button_group.addButton(button)
            self._buttons[key] = button
            root.addWidget(button)

        root.addStretch(1)

        version = QLabel(VERSION_TEXT)
        version.setObjectName("subtle")
        root.addWidget(version)

        if "dashboard" in self._buttons:
            self._buttons["dashboard"].setChecked(True)

    def _on_navigate(self, screen_name: str) -> None:
        """Emit navigate signal when user selects an item.

        Args:
            screen_name: Internal target screen name.

        Returns:
            None.
        """

        self.navigate.emit(screen_name)

    def set_active(self, screen_name: str) -> None:
        """Programmatically update highlighted navigation item.

        Args:
            screen_name: Screen key to activate.

        Returns:
            None.
        """

        if screen_name in self._buttons:
            self._buttons[screen_name].setChecked(True)
