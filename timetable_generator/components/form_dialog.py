"""Generic form dialog that dynamically renders field definitions."""

from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QSpinBox,
    QWidget,
)

FIELD_TEXT = "text"
FIELD_SPIN = "spin"
FIELD_DOUBLE = "double"
FIELD_CHECK = "check"
FIELD_COMBO = "combo"
FIELD_LIST = "list"


class FormDialog(QDialog):
    """A configurable add/edit dialog that validates required fields."""

    form_submitted = pyqtSignal(dict)

    def __init__(self, title: str, fields: List[Dict[str, Any]], initial_data: Dict[str, Any] | None = None) -> None:
        """Initialize dialog and build dynamic form controls.

        Args:
            title: Dialog title.
            fields: Field specification dictionaries.
            initial_data: Optional default values for edit mode.
        """

        super().__init__()
        self.setWindowTitle(title)
        self.setModal(True)
        self._fields = fields
        self._initial_data = initial_data or {}
        self._widgets: Dict[str, QWidget] = {}
        self._errors: Dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """Render all configured fields and action buttons.

        Returns:
            None.
        """

        form = QFormLayout(self)

        for field in self._fields:
            key = field["key"]
            label_text = field["label"]
            widget = self._create_widget(field)
            self._widgets[key] = widget

            field_container = QWidget()
            field_layout = QFormLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.addRow(widget)

            error = QLabel("")
            error.setProperty("error", True)
            self._errors[key] = error
            field_layout.addRow(error)

            form.addRow(label_text, field_container)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_submit)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _create_widget(self, field: Dict[str, Any]) -> QWidget:
        """Create an input widget according to field config.

        Args:
            field: Field metadata dictionary.

        Returns:
            Configured input widget.
        """

        field_type = field.get("type", FIELD_TEXT)
        key = field["key"]
        value = self._initial_data.get(key)

        if field_type == FIELD_TEXT:
            widget = QLineEdit()
            if value is not None:
                widget.setText(str(value))
            return widget

        if field_type == FIELD_SPIN:
            widget = QSpinBox()
            widget.setMinimum(field.get("min", 0))
            widget.setMaximum(field.get("max", 9999))
            if value is not None:
                widget.setValue(int(value))
            return widget

        if field_type == FIELD_DOUBLE:
            widget = QDoubleSpinBox()
            widget.setMinimum(field.get("min", 0.0))
            widget.setMaximum(field.get("max", 9999.0))
            widget.setSingleStep(field.get("step", 0.5))
            if value is not None:
                widget.setValue(float(value))
            return widget

        if field_type == FIELD_CHECK:
            widget = QCheckBox()
            if value is not None:
                widget.setChecked(bool(value))
            return widget

        if field_type == FIELD_COMBO:
            widget = QComboBox()
            options = field.get("options", [])
            widget.addItems([str(option) for option in options])
            if value is not None and str(value) in [str(option) for option in options]:
                widget.setCurrentText(str(value))
            return widget

        if field_type == FIELD_LIST:
            widget = QListWidget()
            selected_values = set(value or [])
            for option in field.get("options", []):
                if isinstance(option, tuple):
                    opt_value, text = option
                else:
                    opt_value, text = option, str(option)
                item = QListWidgetItem(text)
                item.setData(256, opt_value)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if opt_value in selected_values else Qt.Unchecked)
                widget.addItem(item)
            return widget

        return QLineEdit()

    def _clear_errors(self) -> None:
        """Clear all inline field validation errors.

        Returns:
            None.
        """

        for label in self._errors.values():
            label.setText("")

    def _collect_data(self) -> Dict[str, Any]:
        """Collect values from all configured form fields.

        Returns:
            Dictionary of form values keyed by field key.
        """

        payload: Dict[str, Any] = {}
        for field in self._fields:
            key = field["key"]
            field_type = field.get("type", FIELD_TEXT)
            widget = self._widgets[key]

            if field_type == FIELD_TEXT:
                payload[key] = widget.text().strip()  # type: ignore[attr-defined]
            elif field_type == FIELD_SPIN:
                payload[key] = widget.value()  # type: ignore[attr-defined]
            elif field_type == FIELD_DOUBLE:
                payload[key] = widget.value()  # type: ignore[attr-defined]
            elif field_type == FIELD_CHECK:
                payload[key] = widget.isChecked()  # type: ignore[attr-defined]
            elif field_type == FIELD_COMBO:
                payload[key] = widget.currentText()  # type: ignore[attr-defined]
            elif field_type == FIELD_LIST:
                values = []
                list_widget = widget  # type: ignore[assignment]
                for idx in range(list_widget.count()):
                    item = list_widget.item(idx)
                    if item.checkState() == Qt.Checked:
                        values.append(item.data(256))
                payload[key] = values
            else:
                payload[key] = None
        return payload

    def _validate(self, payload: Dict[str, Any]) -> bool:
        """Validate required fields and show inline messages.

        Args:
            payload: Form data payload.

        Returns:
            True when all required fields are valid.
        """

        valid = True
        for field in self._fields:
            key = field["key"]
            required = field.get("required", False)
            value = payload.get(key)
            error = self._errors[key]

            if required:
                if isinstance(value, str) and not value.strip():
                    error.setText("This field is required.")
                    valid = False
                elif isinstance(value, list) and len(value) == 0:
                    error.setText("Select at least one option.")
                    valid = False
        return valid

    def _on_submit(self) -> None:
        """Handle save click with validation and signal emission.

        Returns:
            None.
        """

        try:
            self._clear_errors()
            payload = self._collect_data()
            if not self._validate(payload):
                return
            self.form_submitted.emit(payload)
            self.accept()
        except Exception as exc:  # pragma: no cover - defensive UI handler
            QMessageBox.critical(self, "Form Error", f"Unable to submit form: {exc}")
