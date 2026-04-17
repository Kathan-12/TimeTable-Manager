"""Faculty availability configuration view."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.controllers.availability_controller import AvailabilityController
from timetable_generator.controllers.timeslot_controller import TimeSlotController

TITLE_TEXT = "Faculty Availability"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


class AvailabilityView(QWidget):
    """View for editing weekly availability grid for each faculty member."""

    def __init__(self, availability_controller: AvailabilityController, timeslot_controller: TimeSlotController) -> None:
        """Initialize availability view and dependencies.

        Args:
            availability_controller: Faculty availability controller.
            timeslot_controller: Time slot lookup controller.
        """

        super().__init__()
        self._availability_controller = availability_controller
        self._timeslot_controller = timeslot_controller
        self._faculty_list: QListWidget
        self._grid: QTableWidget
        self._selected_faculty_id: int | None = None
        self._build_ui()
        self._load_faculty_list()

    def _build_ui(self) -> None:
        """Render split panel layout and save actions.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        split = QHBoxLayout()

        self._faculty_list = QListWidget()
        self._faculty_list.currentRowChanged.connect(self._on_faculty_selected)
        split.addWidget(self._faculty_list, 1)

        self._grid = QTableWidget()
        self._grid.setColumnCount(len(DAYS))
        self._grid.setHorizontalHeaderLabels(DAYS)
        split.addWidget(self._grid, 3)

        root.addLayout(split)

        save_button = QPushButton("Save Availability")
        save_button.setProperty("primary", "true")
        save_button.clicked.connect(self._save_availability)
        root.addWidget(save_button)

    def _load_faculty_list(self) -> None:
        """Load faculty names into selector list.

        Returns:
            None.
        """

        try:
            self._faculty_list.clear()
            for faculty in self._availability_controller.get_all():
                self._faculty_list.addItem(f"{faculty.id} - {faculty.name}")
            if self._faculty_list.count() > 0:
                self._faculty_list.setCurrentRow(0)
        except Exception as exc:
            QMessageBox.critical(self, "Availability Error", f"Unable to load faculty list: {exc}")

    def _on_faculty_selected(self, row: int) -> None:
        """Handle faculty selection change and redraw availability grid.

        Args:
            row: Selected list row index.

        Returns:
            None.
        """

        try:
            faculty_records = self._availability_controller.get_all()
            if row < 0 or row >= len(faculty_records):
                return
            faculty = faculty_records[row]
            self._selected_faculty_id = faculty.id
            self._load_grid(faculty.available_slots)
        except Exception as exc:
            QMessageBox.critical(self, "Availability Error", f"Unable to load faculty availability: {exc}")

    def _load_grid(self, selected_slot_ids: list[int]) -> None:
        """Build day x slot availability matrix for selected faculty.

        Args:
            selected_slot_ids: Selected timeslot IDs.

        Returns:
            None.
        """

        slots = self._timeslot_controller.get_all()
        unique_windows = sorted({(slot.start_time, slot.end_time) for slot in slots})
        self._grid.setRowCount(len(unique_windows))
        self._grid.setVerticalHeaderLabels([f"{start}-{end}" for start, end in unique_windows])

        lookup = {(slot.day, slot.start_time, slot.end_time): slot.id for slot in slots}
        for row_idx, (start, end) in enumerate(unique_windows):
            for col_idx, day in enumerate(DAYS):
                slot_id = lookup.get((day, start, end))
                item = QTableWidgetItem("")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setData(Qt.UserRole, slot_id)
                checked = slot_id in selected_slot_ids if slot_id is not None else False
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                self._grid.setItem(row_idx, col_idx, item)

    def _save_availability(self) -> None:
        """Persist selected grid cells into controller state.

        Returns:
            None.
        """

        try:
            if self._selected_faculty_id is None:
                return
            selected_ids: list[int] = []
            for row in range(self._grid.rowCount()):
                for col in range(self._grid.columnCount()):
                    item = self._grid.item(row, col)
                    if item is None:
                        continue
                    if item.checkState() == Qt.Checked:
                        slot_id = item.data(Qt.UserRole)
                        if isinstance(slot_id, int):
                            selected_ids.append(slot_id)
            ok = self._availability_controller.set_faculty_availability(self._selected_faculty_id, selected_ids)
            if ok:
                QMessageBox.information(self, "Availability", "Availability saved successfully.")
        except Exception as exc:
            QMessageBox.critical(self, "Availability Error", f"Unable to save availability: {exc}")
