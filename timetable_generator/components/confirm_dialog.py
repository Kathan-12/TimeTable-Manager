"""Reusable confirmation dialog component."""

from __future__ import annotations

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

DEFAULT_TITLE = "Confirm Action"


class ConfirmDialog(QDialog):
    """A modal dialog that asks the user to confirm or cancel an action."""

    def __init__(self, message: str, title: str = DEFAULT_TITLE) -> None:
        """Initialize the confirmation dialog.

        Args:
            message: Human-readable confirmation prompt.
            title: Dialog title.
        """

        super().__init__()
        self.setWindowTitle(title)
        self.setModal(True)
        self._message = message
        self._build_ui()

    def _build_ui(self) -> None:
        """Create dialog controls and wire events.

        Returns:
            None.
        """

        root = QVBoxLayout(self)

        icon = QLabel("⚠️")
        icon.setObjectName("warningIcon")
        root.addWidget(icon)

        message_label = QLabel(self._message)
        message_label.setWordWrap(True)
        root.addWidget(message_label)

        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        confirm_button = QPushButton("Confirm")
        confirm_button.setProperty("danger", "true")
        confirm_button.style().unpolish(confirm_button)
        confirm_button.style().polish(confirm_button)

        cancel_button.clicked.connect(self.reject)
        confirm_button.clicked.connect(self.accept)

        buttons.addWidget(cancel_button)
        buttons.addWidget(confirm_button)
        root.addLayout(buttons)

    @staticmethod
    def ask(message: str, title: str = DEFAULT_TITLE) -> bool:
        """Open a confirmation dialog and return user decision.

        Args:
            message: Confirmation prompt text.
            title: Dialog title text.

        Returns:
            True when confirmed, otherwise False.
        """

        dialog = ConfirmDialog(message=message, title=title)
        return dialog.exec_() == QDialog.Accepted
