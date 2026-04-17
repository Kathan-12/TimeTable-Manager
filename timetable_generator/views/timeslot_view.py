"""Timeslot management view for day/time configuration."""

from __future__ import annotations

from PyQt5.QtCore import QTime, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.components.confirm_dialog import ConfirmDialog
from timetable_generator.controllers.timeslot_controller import TimeSlotController
from timetable_generator.models.timeslot import TimeSlot
from timetable_generator.utils.helpers import is_valid_time_range

TITLE_TEXT = "Time Slot Management"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
HEADERS = ["ID", "Day", "Start Time", "End Time", "Actions"]


class TimeSlotDialog(QDialog):
    """Modal dialog for creating and editing one timeslot."""

    def __init__(self, slot: TimeSlot | None = None) -> None:
        """Initialize dialog controls.

        Args:
            slot: Existing slot to pre-fill when editing.
        """

        super().__init__()
        self._slot = slot
        self.setWindowTitle("Add Time Slot" if slot is None else "Edit Time Slot")
        self._day = QComboBox()
        self._day.addItems(DAYS)
        self._start = QTimeEdit()
        self._start.setDisplayFormat("HH:mm")
        self._end = QTimeEdit()
        self._end.setDisplayFormat("HH:mm")
        self._build_ui()

    def _build_ui(self) -> None:
        """Render dialog form and assign initial values.

        Returns:
            None.
        """

        form = QFormLayout(self)
        form.addRow("Day", self._day)
        form.addRow("Start Time", self._start)
        form.addRow("End Time", self._end)

        if self._slot is not None:
            self._day.setCurrentText(self._slot.day)
            self._start.setTime(QTime.fromString(self._slot.start_time, "HH:mm"))
            self._end.setTime(QTime.fromString(self._slot.end_time, "HH:mm"))

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self) -> tuple[str, str, str]:
        """Return current day/start/end form values.

        Returns:
            Tuple of day, start_time, end_time strings.
        """

        return (
            self._day.currentText(),
            self._start.time().toString("HH:mm"),
            self._end.time().toString("HH:mm"),
        )


class TimeSlotView(QWidget):
    """Screen for CRUD operations on available timeslots."""

    def __init__(self, controller: TimeSlotController) -> None:
        """Initialize timeslot management screen.

        Args:
            controller: Timeslot data controller.
        """

        super().__init__()
        self._controller = controller
        self._table: QTableWidget
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        """Render timeslot table and actions.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        top = QHBoxLayout()
        add_btn = QPushButton("Add Time Slot")
        add_btn.setProperty("primary", "true")
        add_btn.clicked.connect(self._add_slot)
        top.addWidget(add_btn)
        top.addStretch(1)
        root.addLayout(top)

        self._table = QTableWidget()
        self._table.setColumnCount(len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

    def _refresh_table(self) -> None:
        """Refresh timeslot rows in table.

        Returns:
            None.
        """

        try:
            rows = self._controller.get_all()
            self._table.setRowCount(0)
            for r, model in enumerate(rows):
                self._table.insertRow(r)
                self._table.setItem(r, 0, self._item(str(model.id)))
                self._table.setItem(r, 1, self._item(model.day))
                self._table.setItem(r, 2, self._item(model.start_time))
                self._table.setItem(r, 3, self._item(model.end_time))

                action = QWidget()
                action_layout = QHBoxLayout(action)
                action_layout.setContentsMargins(2, 2, 2, 2)
                edit_btn = QPushButton("✏")
                edit_btn.clicked.connect(lambda _=False, sid=model.id: self._edit_slot(sid))
                del_btn = QPushButton("🗑")
                del_btn.setProperty("danger", "true")
                del_btn.clicked.connect(lambda _=False, sid=model.id: self._delete_slot(sid))
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)
                self._table.setCellWidget(r, 4, action)
            self._table.resizeColumnsToContents()
        except Exception as exc:
            QMessageBox.critical(self, "Time Slot Error", f"Unable to refresh timeslots: {exc}")

    def _item(self, value: str) -> QTableWidgetItem:
        """Create a read-only table item.

        Args:
            value: Cell text.

        Returns:
            QTableWidgetItem.
        """

        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _add_slot(self) -> None:
        """Create a timeslot from dialog values.

        Returns:
            None.
        """

        try:
            dialog = TimeSlotDialog()
            if dialog.exec_() != QDialog.Accepted:
                return
            day, start, end = dialog.values()
            if not is_valid_time_range(start, end):
                QMessageBox.critical(self, "Validation Error", "End time must be later than start time.")
                return
            new_id = max((item.id for item in self._controller.get_all()), default=0) + 1
            self._controller.add(TimeSlot(id=new_id, day=day, start_time=start, end_time=end))
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Time Slot Error", f"Unable to add timeslot: {exc}")

    def _edit_slot(self, slot_id: int) -> None:
        """Edit selected timeslot entry.

        Args:
            slot_id: Timeslot identifier.

        Returns:
            None.
        """

        try:
            existing = self._controller.get_by_id(slot_id)
            if existing is None:
                return
            dialog = TimeSlotDialog(existing)
            if dialog.exec_() != QDialog.Accepted:
                return
            day, start, end = dialog.values()
            if not is_valid_time_range(start, end):
                QMessageBox.critical(self, "Validation Error", "End time must be later than start time.")
                return
            self._controller.update(slot_id, TimeSlot(id=slot_id, day=day, start_time=start, end_time=end))
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Time Slot Error", f"Unable to edit timeslot: {exc}")

    def _delete_slot(self, slot_id: int) -> None:
        """Delete timeslot record after confirmation.

        Args:
            slot_id: Timeslot identifier.

        Returns:
            None.
        """

        try:
            if not ConfirmDialog.ask("Delete selected time slot?"):
                return
            self._controller.delete(slot_id)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Time Slot Error", f"Unable to delete timeslot: {exc}")
