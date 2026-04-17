"""Dashboard statistics card component."""

from __future__ import annotations

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

ICON_FONT_SIZE = 18
VALUE_FONT_SIZE = 20
TITLE_FONT_SIZE = 10


class StatCard(QFrame):
    """Card widget that displays a titled numeric KPI with accent and icon."""

    def __init__(self, title: str, value: str | int, icon: str, color: str) -> None:
        """Initialize a statistics card.

        Args:
            title: Card title text.
            value: Main value to display.
            icon: Emoji or icon text.
            color: Accent bar color in hex format.
        """

        super().__init__()
        self.setObjectName("CardPanel")
        self._title = title
        self._value = str(value)
        self._icon = icon
        self._color = color
        self._build_ui()

    def _build_ui(self) -> None:
        """Construct card widgets and layout.

        Returns:
            None.
        """

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        accent = QFrame()
        accent.setFixedWidth(4)
        accent.setStyleSheet(f"background-color: {self._color}; border-radius: 2px;")
        root.addWidget(accent)

        inner = QHBoxLayout()
        inner.setContentsMargins(12, 10, 12, 10)

        text_col = QVBoxLayout()

        title_label = QLabel(self._title)
        title_label.setObjectName("subtle")

        value_label = QLabel(self._value)
        value_label.setObjectName("statValue")

        text_col.addWidget(title_label)
        text_col.addWidget(value_label)
        inner.addLayout(text_col)

        icon_label = QLabel(self._icon)
        icon_label.setObjectName("statIcon")
        inner.addWidget(icon_label)

        root.addLayout(inner)
