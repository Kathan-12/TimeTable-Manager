"""Course management view with CRUD operations and CSV import."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
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
from timetable_generator.controllers.course_controller import CourseController
from timetable_generator.models.course import Course
from timetable_generator.utils.helpers import normalize_query

TITLE_TEXT = "Course Management"
SEARCH_PLACEHOLDER = "Search by code or name..."
HEADERS = ["ID", "Code", "Name", "Lectures/Week", "Type", "Duration", "Actions"]


class CourseView(QWidget):
    """Screen for creating and managing course records."""

    def __init__(self, controller: CourseController) -> None:
        """Initialize course view.

        Args:
            controller: Course data controller.
        """

        super().__init__()
        self._controller = controller
        self._search: QLineEdit
        self._table: QTableWidget
        self._build_ui()
        self._refresh_table()

    def _build_ui(self) -> None:
        """Render top actions and data table.

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

        add_btn = QPushButton("Add Course")
        add_btn.setProperty("primary", "true")
        add_btn.clicked.connect(self._add_course)

        import_btn = QPushButton("Import CSV")
        import_btn.clicked.connect(self._import_csv)

        top.addWidget(self._search)
        top.addWidget(add_btn)
        top.addWidget(import_btn)
        root.addLayout(top)

        self._table = QTableWidget()
        self._table.setColumnCount(len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

    def _filtered(self) -> list[Course]:
        """Filter courses by search query.

        Returns:
            Filtered course models.
        """

        query = normalize_query(self._search.text())
        rows = self._controller.get_all()
        if not query:
            return rows
        return [row for row in rows if query in row.name.lower() or query in row.code.lower()]

    def _refresh_table(self) -> None:
        """Refresh table rows from controller state.

        Returns:
            None.
        """

        try:
            rows = self._filtered()
            self._table.setRowCount(0)
            for r, model in enumerate(rows):
                self._table.insertRow(r)
                self._table.setItem(r, 0, self._ro_item(str(model.id)))
                self._table.setItem(r, 1, self._ro_item(model.code))
                self._table.setItem(r, 2, self._ro_item(model.name))
                self._table.setItem(r, 3, self._ro_item(str(model.lectures_per_week)))
                self._table.setCellWidget(r, 4, Badge.warning("Lab") if model.is_lab else Badge.success("Lecture"))
                self._table.setItem(r, 5, self._ro_item(str(model.duration_hours)))

                action = QWidget()
                action_layout = QHBoxLayout(action)
                action_layout.setContentsMargins(2, 2, 2, 2)
                edit_btn = QPushButton("✏")
                edit_btn.clicked.connect(lambda _=False, cid=model.id: self._edit_course(cid))
                del_btn = QPushButton("🗑")
                del_btn.setProperty("danger", "true")
                del_btn.clicked.connect(lambda _=False, cid=model.id: self._delete_course(cid))
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)
                self._table.setCellWidget(r, 6, action)
            self._table.resizeColumnsToContents()
        except Exception as exc:
            QMessageBox.critical(self, "Course Error", f"Unable to refresh course table: {exc}")

    def _ro_item(self, value: str) -> QTableWidgetItem:
        """Create read-only item.

        Args:
            value: Text value.

        Returns:
            QTableWidgetItem with readonly flag.
        """

        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _form(self, title: str, model: Course | None = None) -> dict | None:
        """Open course form dialog.

        Args:
            title: Window title.
            model: Optional course data for edit mode.

        Returns:
            Submitted payload or None.
        """

        fields = [
            {"label": "Course Name", "type": "text", "key": "name", "required": True},
            {"label": "Course Code", "type": "text", "key": "code", "required": True},
            {"label": "Lectures Per Week", "type": "spin", "key": "lectures_per_week", "required": True, "min": 1, "max": 10},
            {"label": "Is Lab", "type": "check", "key": "is_lab", "required": False},
            {"label": "Duration Hours", "type": "double", "key": "duration_hours", "required": True, "min": 1.0, "max": 4.0, "step": 0.5},
        ]
        initial = {
            "name": model.name if model else "",
            "code": model.code if model else "",
            "lectures_per_week": model.lectures_per_week if model else 1,
            "is_lab": model.is_lab if model else False,
            "duration_hours": model.duration_hours if model else 1.0,
        }
        dialog = FormDialog(title=title, fields=fields, initial_data=initial)
        payload: dict = {}
        dialog.form_submitted.connect(lambda data: payload.update(data))
        if dialog.exec_() == dialog.Accepted:
            return payload
        return None

    def _add_course(self) -> None:
        """Open add course form and persist created model.

        Returns:
            None.
        """

        try:
            payload = self._form("Add Course")
            if not payload:
                return
            new_id = max((item.id for item in self._controller.get_all()), default=0) + 1
            model = Course(id=new_id, **payload)
            self._controller.add(model)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Course Error", f"Unable to add course: {exc}")

    def _edit_course(self, course_id: int) -> None:
        """Open edit course form and save changes.

        Args:
            course_id: Target course identifier.

        Returns:
            None.
        """

        try:
            existing = self._controller.get_by_id(course_id)
            if existing is None:
                return
            payload = self._form("Edit Course", existing)
            if not payload:
                return
            updated = Course(id=existing.id, **payload)
            self._controller.update(existing.id, updated)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Course Error", f"Unable to update course: {exc}")

    def _delete_course(self, course_id: int) -> None:
        """Delete a course after confirmation.

        Args:
            course_id: Course identifier.

        Returns:
            None.
        """

        try:
            if not ConfirmDialog.ask("Delete selected course?"):
                return
            self._controller.delete(course_id)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Course Error", f"Unable to delete course: {exc}")

    def _import_csv(self) -> None:
        """Import courses from selected CSV file.

        Returns:
            None.
        """

        try:
            filepath, _ = QFileDialog.getOpenFileName(self, "Import Course CSV", "", "CSV Files (*.csv)")
            if not filepath:
                return
            count, errors = self._controller.import_csv(filepath)
            message = f"Imported {count} courses."
            if errors:
                message += "\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "Import Result", message)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Course Error", f"Unable to import courses: {exc}")
