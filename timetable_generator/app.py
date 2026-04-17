"""Application bootstrap utilities for the timetable generator desktop app."""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from timetable_generator.views.main_window import MainWindow

APP_TITLE = "Time Table Generator - University Scheduling System"
MIN_WIDTH = 1200
MIN_HEIGHT = 750


def _load_stylesheet() -> str:
    """Read QSS stylesheet content from disk.

    Returns:
        Stylesheet string or empty string if file unavailable.
    """

    style_path = Path(__file__).resolve().parent / "styles" / "dark_theme.qss"
    if not style_path.exists():
        return ""
    return style_path.read_text(encoding="utf-8")


def create_application() -> tuple[QApplication, MainWindow]:
    """Create and configure QApplication plus main window.

    Returns:
        Tuple containing configured QApplication and MainWindow.
    """

    app = QApplication.instance() or QApplication([])
    app.setApplicationName(APP_TITLE)
    app.setFont(QFont("Segoe UI", 10))

    stylesheet = _load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
    window.showMaximized()
    return app, window
