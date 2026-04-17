"""Conflict reporting view with filtering and export."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.components.badge import Badge
from timetable_generator.components.stat_card import StatCard
from timetable_generator.controllers.export_controller import ExportController
from timetable_generator.models.conflict import Conflict
from timetable_generator.utils import mock_data

TITLE_TEXT = "Conflict Report"
FILTER_OPTIONS = [
    "All Types",
    "FACULTY_OVERLAP",
    "ROOM_OVERLAP",
    "BATCH_OVERLAP",
    "UNSCHEDULED_LECTURE",
    "CONSTRAINT_VIOLATION",
]
HEADERS = ["#", "Type", "Description", "Severity"]


class ConflictView(QWidget):
    """Screen for viewing and exporting scheduling conflicts."""

    def __init__(self, export_controller: ExportController) -> None:
        """Initialize conflict report view.

        Args:
            export_controller: Export service controller.
        """

        super().__init__()
        self._export_controller = export_controller
        self._conflicts: list[Conflict] = mock_data.get_conflicts()
        self._table = QTableWidget()
        self._filter = QComboBox()
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        """Render summary cards, filter controls, and data table.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        summary = QHBoxLayout()
        total = len(self._conflicts)
        high = len([c for c in self._conflicts if c.severity == "HIGH"])
        unscheduled = len([c for c in self._conflicts if c.type == "UNSCHEDULED_LECTURE"])
        summary.addWidget(StatCard("Total Conflicts", total, "⚠️", "#ff4d6a"))
        summary.addWidget(StatCard("High Severity", high, "🚨", "#ff4d6a"))
        summary.addWidget(StatCard("Unscheduled", unscheduled, "📌", "#f5a623"))
        root.addLayout(summary)

        controls = QHBoxLayout()
        self._filter.addItems(FILTER_OPTIONS)
        self._filter.currentIndexChanged.connect(self._refresh)
        export_btn = QPushButton("Export Conflict Report (CSV)")
        export_btn.clicked.connect(self._export)
        controls.addWidget(self._filter)
        controls.addWidget(export_btn)
        root.addLayout(controls)

        self._table.setColumnCount(len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

        self._empty_state = QLabel("✅ No conflicts detected!")
        self._empty_state.setAlignment(Qt.AlignCenter)
        self._empty_state.hide()
        root.addWidget(self._empty_state)

    def _filtered(self) -> list[Conflict]:
        """Return conflicts filtered by selected conflict type.

        Returns:
            Filtered conflict list.
        """

        selected = self._filter.currentText()
        if selected == "All Types":
            return list(self._conflicts)
        return [item for item in self._conflicts if item.type == selected]

    def _refresh(self) -> None:
        """Refresh conflict table with current filter selection.

        Returns:
            None.
        """

        try:
            rows = self._filtered()
            self._table.setRowCount(0)
            if not rows:
                self._empty_state.show()
                return
            self._empty_state.hide()
            for idx, conflict in enumerate(rows, start=1):
                row = self._table.rowCount()
                self._table.insertRow(row)
                self._table.setItem(row, 0, self._item(str(idx)))
                self._table.setItem(row, 1, self._item(conflict.type))
                self._table.setItem(row, 2, self._item(conflict.description))
                if conflict.severity == "HIGH":
                    badge = Badge.danger("HIGH")
                elif conflict.severity == "MEDIUM":
                    badge = Badge.warning("MEDIUM")
                else:
                    badge = Badge.info("LOW")
                self._table.setCellWidget(row, 3, badge)
            self._table.resizeColumnsToContents()
        except Exception as exc:
            QMessageBox.critical(self, "Conflict Error", f"Unable to refresh conflicts: {exc}")

    def _item(self, value: str) -> QTableWidgetItem:
        """Create a read-only cell item.

        Args:
            value: Cell text.

        Returns:
            QTableWidgetItem value.
        """

        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _export(self) -> None:
        """Export currently filtered conflict list to CSV.

        Returns:
            None.
        """

        try:
            path, _ = QFileDialog.getSaveFileName(self, "Export Conflict CSV", "", "CSV Files (*.csv)")
            if not path:
                return
            payload = [
                {"type": c.type, "description": c.description, "severity": c.severity}
                for c in self._filtered()
            ]
            ok = self._export_controller.export_csv(payload, path)
            if ok:
                QMessageBox.information(self, "Export", "Conflict report exported successfully.")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Unable to export conflict report: {exc}")
