"""Room management view for classroom and lab inventory."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.components.badge import Badge
from timetable_generator.components.confirm_dialog import ConfirmDialog
from timetable_generator.components.form_dialog import FormDialog
from timetable_generator.controllers.room_controller import RoomController
from timetable_generator.models.room import Room
from timetable_generator.utils.helpers import normalize_query

TITLE_TEXT = "Room Management"
SEARCH_PLACEHOLDER = "Search by room or building..."
HEADERS = ["ID", "Room Number", "Building", "Capacity", "Type", "Actions"]


class RoomView(QWidget):
    """Screen for adding, editing, searching, and deleting rooms."""

    def __init__(self, controller: RoomController) -> None:
        """Initialize room view.

        Args:
            controller: Room data controller.
        """

        super().__init__()
        self._controller = controller
        self._search: QLineEdit
        self._table: QTableWidget
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        """Render room management UI layout.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        top = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText(SEARCH_PLACEHOLDER)
        self._search.textChanged.connect(self._refresh_table)

        add_btn = QPushButton("Add Room")
        add_btn.setProperty("primary", "true")
        add_btn.clicked.connect(self._add_room)

        top.addWidget(self._search)
        top.addWidget(add_btn)
        root.addLayout(top)

        self._table = QTableWidget()
        self._table.setColumnCount(len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

    def _filtered(self) -> list[Room]:
        """Filter room rows by room number/building query.

        Returns:
            Filtered room list.
        """

        query = normalize_query(self._search.text())
        rows = self._controller.get_all()
        if not query:
            return rows
        return [row for row in rows if query in row.room_number.lower() or query in row.building.lower()]

    def _refresh_table(self) -> None:
        """Populate room table with current data.

        Returns:
            None.
        """

        try:
            rows = self._filtered()
            self._table.setRowCount(0)
            for r, model in enumerate(rows):
                self._table.insertRow(r)
                self._table.setItem(r, 0, self._item(str(model.id)))
                self._table.setItem(r, 1, self._item(model.room_number))
                self._table.setItem(r, 2, self._item(model.building))
                self._table.setItem(r, 3, self._item(str(model.capacity)))
                self._table.setCellWidget(r, 4, Badge.warning("Lab") if model.is_lab else Badge.success("Lecture Hall"))

                action = QWidget()
                action_layout = QHBoxLayout(action)
                action_layout.setContentsMargins(2, 2, 2, 2)
                edit_btn = QPushButton("✏")
                edit_btn.clicked.connect(lambda _=False, rid=model.id: self._edit_room(rid))
                del_btn = QPushButton("🗑")
                del_btn.setProperty("danger", "true")
                del_btn.clicked.connect(lambda _=False, rid=model.id: self._delete_room(rid))
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)
                self._table.setCellWidget(r, 5, action)
            self._table.resizeColumnsToContents()
        except Exception as exc:
            QMessageBox.critical(self, "Room Error", f"Unable to refresh rooms: {exc}")

    def _item(self, value: str) -> QTableWidgetItem:
        """Build readonly table item.

        Args:
            value: Cell text.

        Returns:
            Read-only table item.
        """

        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _form(self, title: str, model: Room | None = None) -> dict | None:
        """Open room add/edit form.

        Args:
            title: Dialog title.
            model: Existing room record for edit mode.

        Returns:
            Submitted data payload or None.
        """

        fields = [
            {"label": "Room Number", "type": "text", "key": "room_number", "required": True},
            {"label": "Building", "type": "text", "key": "building", "required": True},
            {"label": "Capacity", "type": "spin", "key": "capacity", "required": True, "min": 1, "max": 500},
            {"label": "Is Lab", "type": "check", "key": "is_lab", "required": False},
        ]
        initial = {
            "room_number": model.room_number if model else "",
            "building": model.building if model else "",
            "capacity": model.capacity if model else 40,
            "is_lab": model.is_lab if model else False,
        }
        dialog = FormDialog(title=title, fields=fields, initial_data=initial)
        payload: dict = {}
        dialog.form_submitted.connect(lambda data: payload.update(data))
        if dialog.exec_() == dialog.Accepted:
            return payload
        return None

    def _add_room(self) -> None:
        """Create a new room entry.

        Returns:
            None.
        """

        try:
            payload = self._form("Add Room")
            if not payload:
                return
            new_id = max((item.id for item in self._controller.get_all()), default=0) + 1
            self._controller.add(Room(id=new_id, **payload))
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Room Error", f"Unable to add room: {exc}")

    def _edit_room(self, room_id: int) -> None:
        """Edit selected room.

        Args:
            room_id: Room identifier.

        Returns:
            None.
        """

        try:
            existing = self._controller.get_by_id(room_id)
            if existing is None:
                return
            payload = self._form("Edit Room", existing)
            if not payload:
                return
            self._controller.update(room_id, Room(id=room_id, **payload))
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Room Error", f"Unable to update room: {exc}")

    def _delete_room(self, room_id: int) -> None:
        """Delete selected room after confirmation.

        Args:
            room_id: Room identifier.

        Returns:
            None.
        """

        try:
            if not ConfirmDialog.ask("Delete selected room?"):
                return
            self._controller.delete(room_id)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Room Error", f"Unable to delete room: {exc}")
