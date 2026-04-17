"""Export view containing grouped export/report actions."""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.controllers.export_controller import ExportController
from timetable_generator.utils.helpers import format_timestamp

TITLE_TEXT = "Export & Reports"


class ExportView(QWidget):
    """Screen exposing all timetable and report export entry points."""

    def __init__(self, export_controller: ExportController) -> None:
        """Initialize export view.

        Args:
            export_controller: Controller handling CSV/PDF writes.
        """

        super().__init__()
        self._export_controller = export_controller
        self._status = QLabel("Last exported: None")
        self._build_ui()

    def _build_ui(self) -> None:
        """Render grouped export buttons and status label.

        Returns:
            None.
        """

        root = QVBoxLayout(self)

        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        root.addWidget(QLabel("Export Timetables"))
        root.addWidget(self._button("Export Batch Timetable (CSV)", lambda: self._export_csv("batch_timetable.csv")))
        root.addWidget(self._button("Export Faculty Timetable (CSV)", lambda: self._export_csv("faculty_timetable.csv")))
        root.addWidget(self._button("Export Room Schedule (CSV)", lambda: self._export_csv("room_schedule.csv")))
        root.addWidget(self._button("Export All Timetables (PDF)", self._export_pdf))

        root.addWidget(QLabel("Export Reports"))
        root.addWidget(self._button("Export Conflict Report (CSV)", lambda: self._export_csv("conflict_report.csv")))
        root.addWidget(self._button("Export Utilization Report (CSV)", lambda: self._export_csv("utilization_report.csv")))
        root.addWidget(self._button("Export Faculty Workload Report (CSV)", lambda: self._export_csv("faculty_workload.csv")))

        self._status.setObjectName("subtle")
        root.addWidget(self._status)
        root.addStretch(1)

    def _button(self, label: str, callback) -> QPushButton:
        """Create an action button with attached callback.

        Args:
            label: Button text.
            callback: Click event callback.

        Returns:
            Configured QPushButton.
        """

        button = QPushButton(label)
        button.clicked.connect(callback)
        return button

    def _export_csv(self, suggested_name: str) -> None:
        """Prompt save location and create a stub CSV report.

        Args:
            suggested_name: Suggested file name.

        Returns:
            None.
        """

        try:
            path, _ = QFileDialog.getSaveFileName(self, "Export CSV", suggested_name, "CSV Files (*.csv)")
            if not path:
                return
            payload = [{"status": "ok", "name": suggested_name}]
            if self._export_controller.export_csv(payload, path):
                self._status.setText(f"Last exported: {path} at {format_timestamp()}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Unable to export CSV: {exc}")

    def _export_pdf(self) -> None:
        """Prompt save location and create a stub PDF report.

        Returns:
            None.
        """

        try:
            path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "all_timetables.pdf", "PDF Files (*.pdf)")
            if not path:
                return
            payload = {"report": "All Timetables", "generated_at": format_timestamp()}
            if self._export_controller.export_pdf(payload, path):
                self._status.setText(f"Last exported: {path} at {format_timestamp()}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Unable to export PDF: {exc}")
