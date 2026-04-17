"""Faculty management view with CRUD operations and CSV import."""

from __future__ import annotations

from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.components.confirm_dialog import ConfirmDialog
from timetable_generator.components.form_dialog import FormDialog
from timetable_generator.controllers.course_controller import CourseController
from timetable_generator.controllers.faculty_controller import FacultyController
from timetable_generator.controllers.timeslot_controller import TimeSlotController
from timetable_generator.models.faculty import Faculty
from timetable_generator.utils.helpers import is_valid_email, normalize_query

TITLE_TEXT = "Faculty Management"
SEARCH_PLACEHOLDER = "Search by name or department..."
HEADERS = ["ID", "Name", "Department", "Email", "Assigned Courses", "Actions"]


class FacultyView(QWidget):
    """Screen used to create, edit, search, and remove faculty records."""

    data_changed = pyqtSignal()

    def __init__(self, controller: FacultyController, course_controller: CourseController, timeslot_controller: TimeSlotController) -> None:
        """Initialize faculty view and dependencies.

        Args:
            controller: Faculty controller instance.
            course_controller: Course lookup controller.
            timeslot_controller: Time slot lookup controller.
        """

        super().__init__()
        self._controller = controller
        self._course_controller = course_controller
        self._timeslot_controller = timeslot_controller
        self._search: QLineEdit
        self._table: QTableWidget
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        """Create all UI controls for the faculty management page.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        top_bar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText(SEARCH_PLACEHOLDER)
        self._search.textChanged.connect(self._refresh_table)

        add_button = QPushButton("Add Faculty")
        add_button.setProperty("primary", "true")
        add_button.clicked.connect(self._add_faculty)

        import_button = QPushButton("Import CSV")
        import_button.clicked.connect(self._import_csv)

        top_bar.addWidget(self._search)
        top_bar.addWidget(add_button)
        top_bar.addWidget(import_button)
        root.addLayout(top_bar)

        self._table = QTableWidget()
        self._table.setColumnCount(len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

    def _filtered_data(self) -> List[Faculty]:
        """Apply keyword filtering across faculty records.

        Returns:
            Filtered faculty list.
        """

        query = normalize_query(self._search.text())
        items = self._controller.get_all()
        if not query:
            return items
        return [
            item
            for item in items
            if query in item.name.lower() or query in item.department.lower()
        ]

    def _refresh_table(self) -> None:
        """Populate table with current filtered faculty rows.

        Returns:
            None.
        """

        try:
            rows = self._filtered_data()
            self._table.setRowCount(0)
            for row_idx, faculty in enumerate(rows):
                self._table.insertRow(row_idx)
                course_count = len(faculty.assigned_courses)
                self._table.setItem(row_idx, 0, self._item(str(faculty.id)))
                self._table.setItem(row_idx, 1, self._item(faculty.name))
                self._table.setItem(row_idx, 2, self._item(faculty.department))
                self._table.setItem(row_idx, 3, self._item(faculty.email))
                self._table.setItem(row_idx, 4, self._item(str(course_count)))

                action_cell = QWidget()
                action_layout = QHBoxLayout(action_cell)
                action_layout.setContentsMargins(2, 2, 2, 2)

                edit_btn = QPushButton("✏")
                edit_btn.clicked.connect(lambda _=False, item_id=faculty.id: self._edit_faculty(item_id))
                del_btn = QPushButton("🗑")
                del_btn.setProperty("danger", "true")
                del_btn.clicked.connect(lambda _=False, item_id=faculty.id: self._delete_faculty(item_id))
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)
                self._table.setCellWidget(row_idx, 5, action_cell)
            self._table.resizeColumnsToContents()
            self.data_changed.emit()
        except Exception as exc:
            QMessageBox.critical(self, "Faculty Error", f"Unable to refresh faculty table: {exc}")

    def _item(self, value: str):
        """Create a read-only table item.

        Args:
            value: Cell text.

        Returns:
            Configured table item.
        """

        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QTableWidgetItem

        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _open_form(self, title: str, faculty: Faculty | None = None) -> dict | None:
        """Open add/edit form and return payload.

        Args:
            title: Dialog title.
            faculty: Optional existing faculty for edit mode.

        Returns:
            Submitted payload dictionary or None if cancelled.
        """

        slots = self._timeslot_controller.get_all()
        courses = self._course_controller.get_all()
        fields = [
            {"label": "Name", "type": "text", "key": "name", "required": True},
            {"label": "Department", "type": "text", "key": "department", "required": True},
            {"label": "Email", "type": "text", "key": "email", "required": True},
            {
                "label": "Available Slots",
                "type": "list",
                "key": "available_slots",
                "required": False,
                "options": [(slot.id, f"{slot.day} {slot.start_time}-{slot.end_time}") for slot in slots],
            },
            {
                "label": "Assigned Courses",
                "type": "list",
                "key": "assigned_courses",
                "required": False,
                "options": [(course.id, f"{course.code} - {course.name}") for course in courses],
            },
        ]
        initial = {
            "name": faculty.name if faculty else "",
            "department": faculty.department if faculty else "",
            "email": faculty.email if faculty else "",
            "available_slots": faculty.available_slots if faculty else [],
            "assigned_courses": faculty.assigned_courses if faculty else [],
        }
        dialog = FormDialog(title=title, fields=fields, initial_data=initial)
        payload: dict = {}
        dialog.form_submitted.connect(lambda data: payload.update(data))
        if dialog.exec_() == dialog.Accepted:
            return payload
        return None

    def _add_faculty(self) -> None:
        """Handle Add Faculty button action.

        Returns:
            None.
        """

        try:
            payload = self._open_form("Add Faculty")
            if not payload:
                return
            if not is_valid_email(payload["email"]):
                QMessageBox.critical(self, "Validation Error", "Please provide a valid email.")
                return
            new_id = max((item.id for item in self._controller.get_all()), default=0) + 1
            model = Faculty(
                id=new_id,
                name=payload["name"],
                department=payload["department"],
                email=payload["email"],
                available_slots=payload.get("available_slots", []),
                assigned_courses=payload.get("assigned_courses", []),
            )
            self._controller.add(model)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Faculty Error", f"Unable to add faculty: {exc}")

    def _edit_faculty(self, faculty_id: int) -> None:
        """Open edit form for selected faculty record.

        Args:
            faculty_id: Faculty identifier.

        Returns:
            None.
        """

        try:
            existing = self._controller.get_by_id(faculty_id)
            if existing is None:
                return
            payload = self._open_form("Edit Faculty", faculty=existing)
            if not payload:
                return
            if not is_valid_email(payload["email"]):
                QMessageBox.critical(self, "Validation Error", "Please provide a valid email.")
                return
            updated = Faculty(
                id=existing.id,
                name=payload["name"],
                department=payload["department"],
                email=payload["email"],
                available_slots=payload.get("available_slots", []),
                assigned_courses=payload.get("assigned_courses", []),
            )
            self._controller.update(existing.id, updated)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Faculty Error", f"Unable to update faculty: {exc}")

    def _delete_faculty(self, faculty_id: int) -> None:
        """Delete faculty after user confirmation.

        Args:
            faculty_id: Faculty identifier.

        Returns:
            None.
        """

        try:
            if not ConfirmDialog.ask("Delete selected faculty?"):
                return
            self._controller.delete(faculty_id)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Faculty Error", f"Unable to delete faculty: {exc}")

    def _import_csv(self) -> None:
        """Open file picker and import faculty from CSV.

        Returns:
            None.
        """

        try:
            filepath, _ = QFileDialog.getOpenFileName(self, "Import Faculty CSV", "", "CSV Files (*.csv)")
            if not filepath:
                return
            count, errors = self._controller.import_csv(filepath)
            message = f"Imported {count} faculty records."
            if errors:
                message += "\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "Import Result", message)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Faculty Error", f"Unable to import faculty CSV: {exc}")
