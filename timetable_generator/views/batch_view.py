"""Batch management view for student batches."""

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

from timetable_generator.components.confirm_dialog import ConfirmDialog
from timetable_generator.components.form_dialog import FormDialog
from timetable_generator.controllers.batch_controller import BatchController
from timetable_generator.controllers.course_controller import CourseController
from timetable_generator.models.batch import Batch
from timetable_generator.utils.helpers import normalize_query

TITLE_TEXT = "Batch Management"
SEARCH_PLACEHOLDER = "Search by batch name..."
HEADERS = ["ID", "Batch Name", "Semester", "Size", "No. of Courses", "Actions"]


class BatchView(QWidget):
    """Screen for creating and managing batch records."""

    def __init__(self, controller: BatchController, course_controller: CourseController) -> None:
        """Initialize batch management screen.

        Args:
            controller: Batch data controller.
            course_controller: Course lookup controller.
        """

        super().__init__()
        self._controller = controller
        self._course_controller = course_controller
        self._search: QLineEdit
        self._table: QTableWidget
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        """Render all batch view UI controls.

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

        add_btn = QPushButton("Add Batch")
        add_btn.setProperty("primary", "true")
        add_btn.clicked.connect(self._add_batch)

        top.addWidget(self._search)
        top.addWidget(add_btn)
        root.addLayout(top)

        self._table = QTableWidget()
        self._table.setColumnCount(len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

    def _filtered(self) -> list[Batch]:
        """Apply search filtering to batch list.

        Returns:
            Filtered list of batches.
        """

        query = normalize_query(self._search.text())
        rows = self._controller.get_all()
        if not query:
            return rows
        return [row for row in rows if query in row.name.lower()]

    def _refresh_table(self) -> None:
        """Refresh table contents from controller.

        Returns:
            None.
        """

        try:
            rows = self._filtered()
            self._table.setRowCount(0)
            for r, model in enumerate(rows):
                self._table.insertRow(r)
                self._table.setItem(r, 0, self._item(str(model.id)))
                self._table.setItem(r, 1, self._item(model.name))
                self._table.setItem(r, 2, self._item(str(model.semester)))
                self._table.setItem(r, 3, self._item(str(model.size)))
                self._table.setItem(r, 4, self._item(str(len(model.courses))))

                action = QWidget()
                action_layout = QHBoxLayout(action)
                action_layout.setContentsMargins(2, 2, 2, 2)
                edit_btn = QPushButton("✏")
                edit_btn.clicked.connect(lambda _=False, bid=model.id: self._edit_batch(bid))
                del_btn = QPushButton("🗑")
                del_btn.setProperty("danger", "true")
                del_btn.clicked.connect(lambda _=False, bid=model.id: self._delete_batch(bid))
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)
                self._table.setCellWidget(r, 5, action)
            self._table.resizeColumnsToContents()
        except Exception as exc:
            QMessageBox.critical(self, "Batch Error", f"Unable to refresh batches: {exc}")

    def _item(self, value: str) -> QTableWidgetItem:
        """Create read-only table cell item.

        Args:
            value: Cell text.

        Returns:
            Read-only table item.
        """

        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _open_form(self, title: str, model: Batch | None = None) -> dict | None:
        """Open batch add/edit form.

        Args:
            title: Dialog title text.
            model: Existing batch for edit mode.

        Returns:
            Payload dictionary if accepted else None.
        """

        courses = self._course_controller.get_all()
        fields = [
            {"label": "Batch Name", "type": "text", "key": "name", "required": True},
            {"label": "Semester", "type": "spin", "key": "semester", "required": True, "min": 1, "max": 8},
            {"label": "Batch Size", "type": "spin", "key": "size", "required": True, "min": 1, "max": 300},
            {
                "label": "Assigned Courses",
                "type": "list",
                "key": "courses",
                "required": False,
                "options": [(course.id, f"{course.code} - {course.name}") for course in courses],
            },
        ]
        initial = {
            "name": model.name if model else "",
            "semester": model.semester if model else 1,
            "size": model.size if model else 40,
            "courses": model.courses if model else [],
        }
        dialog = FormDialog(title=title, fields=fields, initial_data=initial)
        payload: dict = {}
        dialog.form_submitted.connect(lambda data: payload.update(data))
        if dialog.exec_() == dialog.Accepted:
            return payload
        return None

    def _add_batch(self) -> None:
        """Add a new batch record from form values.

        Returns:
            None.
        """

        try:
            payload = self._open_form("Add Batch")
            if not payload:
                return
            new_id = max((item.id for item in self._controller.get_all()), default=0) + 1
            self._controller.add(Batch(id=new_id, **payload))
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Batch Error", f"Unable to add batch: {exc}")

    def _edit_batch(self, batch_id: int) -> None:
        """Edit selected batch record.

        Args:
            batch_id: Batch identifier.

        Returns:
            None.
        """

        try:
            existing = self._controller.get_by_id(batch_id)
            if existing is None:
                return
            payload = self._open_form("Edit Batch", existing)
            if not payload:
                return
            self._controller.update(batch_id, Batch(id=batch_id, **payload))
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Batch Error", f"Unable to edit batch: {exc}")

    def _delete_batch(self, batch_id: int) -> None:
        """Delete selected batch record with confirmation.

        Args:
            batch_id: Batch identifier.

        Returns:
            None.
        """

        try:
            if not ConfirmDialog.ask("Delete selected batch?"):
                return
            self._controller.delete(batch_id)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Batch Error", f"Unable to delete batch: {exc}")
