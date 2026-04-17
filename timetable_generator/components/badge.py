"""Badge component for rendering compact status labels."""

from __future__ import annotations

from PyQt5.QtWidgets import QLabel

TEXT_COLOR = "#f8f8ff"
PADDING_Y = 2
PADDING_X = 10


class Badge(QLabel):
    """A pill-shaped colored label used to indicate status and severity."""

    def __init__(self, text: str, color: str) -> None:
        """Initialize a colored status badge.

        Args:
            text: Text displayed inside the badge.
            color: Background color as hex string.
        """

        super().__init__(text)
        self._color = color
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply dynamic badge style based on selected color.

        Returns:
            None.
        """

        self.setStyleSheet(
            f"background-color: {self._color}; color: {TEXT_COLOR};"
            f"border-radius: 10px; padding: {PADDING_Y}px {PADDING_X}px;"
            "font-weight: 600;"
        )

    @classmethod
    def success(cls, text: str) -> "Badge":
        """Create a green success badge.

        Args:
            text: Badge text.

        Returns:
            Configured Badge instance.
        """

        return cls(text, "#00d084")

    @classmethod
    def warning(cls, text: str) -> "Badge":
        """Create an amber warning badge.

        Args:
            text: Badge text.

        Returns:
            Configured Badge instance.
        """

        return cls(text, "#f5a623")

    @classmethod
    def danger(cls, text: str) -> "Badge":
        """Create a red danger badge.

        Args:
            text: Badge text.

        Returns:
            Configured Badge instance.
        """

        return cls(text, "#ff4d6a")

    @classmethod
    def info(cls, text: str) -> "Badge":
        """Create an informational blue badge.

        Args:
            text: Badge text.

        Returns:
            Configured Badge instance.
        """

        return cls(text, "#4da3ff")
