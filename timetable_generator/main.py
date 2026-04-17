"""Executable entry point for the timetable generator desktop application."""

from __future__ import annotations

import sys

from timetable_generator.app import create_application


def main() -> int:
    """Launch the timetable generator UI process.

    Returns:
        Process exit code from Qt event loop.
    """

    app, _ = create_application()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
