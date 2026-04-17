"""Scheduling constraints configuration view."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.controllers.constraint_controller import ConstraintController

TITLE_TEXT = "Scheduling Constraints"
HARD_TITLE = "Hard Constraints"
SOFT_TITLE = "Soft Constraints"


class ConstraintsView(QWidget):
    """View displaying enforced hard constraints and editable soft weights."""

    def __init__(self, controller: ConstraintController) -> None:
        """Initialize constraints view.

        Args:
            controller: Constraint data controller.
        """

        super().__init__()
        self._controller = controller
        self._sliders: dict[str, QSlider] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """Render hard constraint list and soft constraint sliders.

        Returns:
            None.
        """

        root = QVBoxLayout(self)
        title = QLabel(TITLE_TEXT)
        title.setObjectName("heading")
        root.addWidget(title)

        hard_label = QLabel(HARD_TITLE)
        hard_label.setObjectName("heading")
        root.addWidget(hard_label)

        hard_panel = QFrame()
        hard_panel.setObjectName("CardPanel")
        hard_layout = QVBoxLayout(hard_panel)
        for item in self._controller.get_hard_constraints():
            hard_layout.addWidget(QLabel(f"🔒 ✔ {item}"))
        root.addWidget(hard_panel)

        soft_label = QLabel(SOFT_TITLE)
        soft_label.setObjectName("heading")
        root.addWidget(soft_label)

        soft_panel = QFrame()
        soft_panel.setObjectName("CardPanel")
        soft_layout = QVBoxLayout(soft_panel)
        for name, value in self._controller.get_all().items():
            row = QHBoxLayout()
            label = QLabel(name)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(10)
            slider.setValue(value)
            self._sliders[name] = slider
            row.addWidget(label)
            row.addWidget(slider)
            soft_layout.addLayout(row)
        root.addWidget(soft_panel)

        save_button = QPushButton("Save Constraint Settings")
        save_button.setProperty("primary", "true")
        save_button.clicked.connect(self._save)
        root.addWidget(save_button)

    def _save(self) -> None:
        """Persist soft constraint slider values.

        Returns:
            None.
        """

        try:
            payload = {name: slider.value() for name, slider in self._sliders.items()}
            self._controller.update(0, payload)
            QMessageBox.information(self, "Constraints", "Constraint settings saved.")
        except Exception as exc:
            QMessageBox.critical(self, "Constraint Error", f"Unable to save constraints: {exc}")
