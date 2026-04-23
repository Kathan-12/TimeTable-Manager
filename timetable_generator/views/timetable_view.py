"""Timetable display view grouped by batch, faculty, and room."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QFileDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.controllers.batch_controller import BatchController
from timetable_generator.controllers.course_controller import CourseController
from timetable_generator.controllers.export_controller import ExportController
from timetable_generator.controllers.faculty_controller import FacultyController
from timetable_generator.controllers.room_controller import RoomController
from timetable_generator.controllers.timeslot_controller import TimeSlotController
from timetable_generator.controllers.timetable_controller import TimetableController

TITLE_TEXT = "Timetable"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class TimetableView(QWidget):
    """View that renders timetable grids for different perspectives."""

    def __init__(
        self,
        batch_controller: BatchController,
        faculty_controller: FacultyController,
        room_controller: RoomController,
        course_controller: CourseController,
        timeslot_controller: TimeSlotController,
        timetable_controller: TimetableController,
        export_controller: ExportController,
    ) -> None:
        """Initialize timetable view dependencies.

        Args:
            batch_controller: Batch lookup controller.
            faculty_controller: Faculty lookup controller.
            room_controller: Room lookup controller.
            course_controller: Course lookup controller.
            export_controller: Export controller.
        """

        super().__init__()
        self._batch_controller = batch_controller
        self._faculty_controller = faculty_controller
        self._room_controller = room_controller
        self._course_controller = course_controller
        self._timeslot_controller = timeslot_controller
        self._timetable_controller = timetable_controller
        self._export_controller = export_controller

        self._entries: list[dict] = []
        self._batch_grid = QTableWidget()
        self._faculty_grid = QTableWidget()
        self._room_grid = QTableWidget()
        self._batch_combo = QComboBox()
        self._faculty_combo = QComboBox()
        self._room_combo = QComboBox()
        self._build_ui()
        self._load_selectors()
        self._render_all()

    def _build_ui(self) -> None:
        """Render tabs, selectors, filters, and export buttons.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        toolbar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search in cells...")
        self._search.textChanged.connect(self._render_all)

        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.clicked.connect(self._export_csv)
        export_pdf_btn = QPushButton("Export PDF")
        export_pdf_btn.clicked.connect(self._export_pdf)

        toolbar.addWidget(self._search)
        toolbar.addWidget(export_csv_btn)
        toolbar.addWidget(export_pdf_btn)
        root.addLayout(toolbar)

        tabs = QTabWidget()
        tabs.addTab(self._batch_tab(), "By Batch")
        tabs.addTab(self._faculty_tab(), "By Faculty")
        tabs.addTab(self._room_tab(), "By Room")
        root.addWidget(tabs)

    def _build_grid(self, grid: QTableWidget) -> None:
        """Apply shared timetable grid structure.

        Args:
            grid: Target table widget.

        Returns:
            None.
        """

        windows = ["09:00-10:00", "10:00-11:00", "11:00-12:00", "14:00-15:00", "15:00-16:00"]
        grid.setRowCount(len(windows))
        grid.setColumnCount(len(DAYS))
        grid.setVerticalHeaderLabels(windows)
        grid.setHorizontalHeaderLabels(DAYS)
        grid.verticalHeader().setVisible(True)

    def _batch_tab(self) -> QWidget:
        """Build batch tab container.

        Returns:
            Configured tab widget.
        """

        widget = QWidget()
        layout = QVBoxLayout(widget)
        self._batch_combo.currentIndexChanged.connect(self._render_batch_grid)
        layout.addWidget(self._batch_combo)
        self._build_grid(self._batch_grid)
        layout.addWidget(self._batch_grid)
        return widget

    def _faculty_tab(self) -> QWidget:
        """Build faculty tab container.

        Returns:
            Configured tab widget.
        """

        widget = QWidget()
        layout = QVBoxLayout(widget)
        self._faculty_combo.currentIndexChanged.connect(self._render_faculty_grid)
        layout.addWidget(self._faculty_combo)
        self._build_grid(self._faculty_grid)
        layout.addWidget(self._faculty_grid)
        return widget

    def _room_tab(self) -> QWidget:
        """Build room tab container.

        Returns:
            Configured tab widget.
        """

        widget = QWidget()
        layout = QVBoxLayout(widget)
        self._room_combo.currentIndexChanged.connect(self._render_room_grid)
        layout.addWidget(self._room_combo)
        self._build_grid(self._room_grid)
        layout.addWidget(self._room_grid)
        return widget

    def _load_selectors(self) -> None:
        """Populate combo boxes for batch/faculty/room selection.

        Returns:
            None.
        """

        self._batch_combo.clear()
        for item in self._batch_controller.get_all():
            self._batch_combo.addItem(item.name, item.id)

        self._faculty_combo.clear()
        for item in self._faculty_controller.get_all():
            self._faculty_combo.addItem(item.name, item.id)

        self._room_combo.clear()
        for item in self._room_controller.get_all():
            self._room_combo.addItem(item.room_number, item.id)

    def _maps(self) -> tuple[dict[int, str], dict[int, str], dict[int, str], dict[int, str], dict[int, tuple[str, str, str]]]:
        """Build lookup dictionaries used to render grid cell text.

        Returns:
            Tuple of course, faculty, batch, room, and slot lookups.
        """

        course = {item.id: item.name for item in self._course_controller.get_all()}
        faculty = {item.id: item.name for item in self._faculty_controller.get_all()}
        batch = {item.id: item.name for item in self._batch_controller.get_all()}
        room = {item.id: item.room_number for item in self._room_controller.get_all()}
        slots = {
            item.id: (item.day, item.start_time, item.end_time)
            for item in self._timeslot_controller.get_all()
        }
        return course, faculty, batch, room, slots

    def _render_all(self) -> None:
        """Re-render all tab grids according to selected filters.

        Returns:
            None.
        """

        self._render_batch_grid()
        self._render_faculty_grid()
        self._render_room_grid()

    def _clear_grid(self, grid: QTableWidget) -> None:
        """Fill grid with default empty placeholders.

        Args:
            grid: Target table to reset.

        Returns:
            None.
        """

        for row in range(grid.rowCount()):
            for col in range(grid.columnCount()):
                item = QTableWidgetItem("-")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setForeground(QColor("#8b8fa8"))
                grid.setItem(row, col, item)

    def _row_for_start(self, start: str) -> int:
        """Map start-time string to timetable row index.

        Args:
            start: Start time in HH:MM.

        Returns:
            Matching row index or -1.
        """

        mapping = {"09:00": 0, "10:00": 1, "11:00": 2, "14:00": 3, "15:00": 4}
        return mapping.get(start, -1)

    def _col_for_day(self, day: str) -> int:
        """Map day string to table column index.

        Args:
            day: Weekday text.

        Returns:
            Matching column index or -1.
        """

        return DAYS.index(day) if day in DAYS else -1

    def _render_batch_grid(self) -> None:
        """Render timetable cells for selected batch.

        Returns:
            None.
        """

        try:
            self._clear_grid(self._batch_grid)
            batch_id = self._batch_combo.currentData()
            if batch_id is None:
                return
            course_map, faculty_map, _, room_map, slots = self._maps()
            query = self._search.text().strip().lower()
            self._entries = self._timetable_controller.get_by_batch(batch_id)
            for entry in self._entries:
                day = entry.get("day", "")
                start = entry.get("start_time", "")
                row = self._row_for_start(start)
                col = self._col_for_day(day)
                if row < 0 or col < 0:
                    continue
                text = f"{entry.get('course_name', 'N/A')}\n{entry.get('faculty_name', 'N/A')}\n{entry.get('room_name', 'N/A')}"
                if query and query not in text.lower():
                    continue
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self._batch_grid.setItem(row, col, item)
        except Exception as exc:
            QMessageBox.critical(self, "Timetable Error", f"Unable to render batch timetable: {exc}")

    def _render_faculty_grid(self) -> None:
        """Render timetable cells for selected faculty.

        Returns:
            None.
        """

        try:
            self._clear_grid(self._faculty_grid)
            faculty_id = self._faculty_combo.currentData()
            if faculty_id is None:
                return
            course_map, _, batch_map, room_map, slots = self._maps()
            query = self._search.text().strip().lower()
            self._entries = self._timetable_controller.get_by_faculty(faculty_id)
            for entry in self._entries:
                day = entry.get("day", "")
                start = entry.get("start_time", "")
                row = self._row_for_start(start)
                col = self._col_for_day(day)
                if row < 0 or col < 0:
                    continue
                text = f"{entry.get('course_name', 'N/A')}\n{entry.get('batch_name', 'N/A')}\n{entry.get('room_name', 'N/A')}"
                if query and query not in text.lower():
                    continue
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self._faculty_grid.setItem(row, col, item)
        except Exception as exc:
            QMessageBox.critical(self, "Timetable Error", f"Unable to render faculty timetable: {exc}")

    def _render_room_grid(self) -> None:
        """Render timetable cells for selected room.

        Returns:
            None.
        """

        try:
            self._clear_grid(self._room_grid)
            room_id = self._room_combo.currentData()
            if room_id is None:
                return
            course_map, faculty_map, batch_map, _, slots = self._maps()
            query = self._search.text().strip().lower()
            self._entries = self._timetable_controller.get_by_room(room_id)
            for entry in self._entries:
                day = entry.get("day", "")
                start = entry.get("start_time", "")
                row = self._row_for_start(start)
                col = self._col_for_day(day)
                if row < 0 or col < 0:
                    continue
                text = f"{entry.get('course_name', 'N/A')}\n{entry.get('faculty_name', 'N/A')}\n{entry.get('batch_name', 'N/A')}"
                if query and query not in text.lower():
                    continue
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self._room_grid.setItem(row, col, item)
        except Exception as exc:
            QMessageBox.critical(self, "Timetable Error", f"Unable to render room timetable: {exc}")

    def _export_csv(self) -> None:
        """Export selected tab timetable entries to CSV.

        Returns:
            None.
        """

        try:
            path, _ = QFileDialog.getSaveFileName(self, "Export Timetable CSV", "", "CSV Files (*.csv)")
            if not path:
                return
            course_map, faculty_map, batch_map, room_map, slots = self._maps()
            rows: list[dict] = []
            for entry in self._entries:
                day = entry.get("day", "")
                start = entry.get("start_time", "")
                end = entry.get("end_time", "")
                rows.append(
                    {
                        "course": entry.get("course_name", "N/A"),
                        "faculty": entry.get("faculty_name", "N/A"),
                        "batch": entry.get("batch_name", "N/A"),
                        "room": entry.get("room_name", "N/A"),
                        "day": day,
                        "start": start,
                        "end": end,
                    }
                )
            ok = self._export_controller.export_csv(rows, path)
            if ok:
                QMessageBox.information(self, "Export", "Timetable CSV exported successfully.")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Unable to export CSV: {exc}")

    def _export_pdf(self) -> None:
        """Export summary timetable report to PDF.

        Returns:
            None.
        """

        try:
            path, _ = QFileDialog.getSaveFileName(self, "Export Timetable PDF", "", "PDF Files (*.pdf)")
            if not path:
                return
            payload = {
                "Total Entries": len(self._entries),
                "Batches": len(self._batch_controller.get_all()),
                "Faculty": len(self._faculty_controller.get_all()),
                "Rooms": len(self._room_controller.get_all()),
            }
            ok = self._export_controller.export_pdf(payload, path)
            if ok:
                QMessageBox.information(self, "Export", "Timetable PDF exported successfully.")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Unable to export PDF: {exc}")
