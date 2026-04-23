"""Main application window with sidebar navigation and stacked screens."""

from __future__ import annotations

from typing import Dict

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from timetable_generator.components.sidebar import Sidebar
from timetable_generator.controllers.availability_controller import AvailabilityController
from timetable_generator.controllers.batch_controller import BatchController
from timetable_generator.controllers.conflict_controller import ConflictController
from timetable_generator.controllers.constraint_controller import ConstraintController
from timetable_generator.controllers.course_controller import CourseController
from timetable_generator.controllers.export_controller import ExportController
from timetable_generator.controllers.faculty_controller import FacultyController
from timetable_generator.controllers.room_controller import RoomController
from timetable_generator.controllers.scheduler_controller import SchedulerController
from timetable_generator.controllers.timeslot_controller import TimeSlotController
from timetable_generator.controllers.timetable_controller import TimetableController
from timetable_generator.utils import mock_data
from timetable_generator.views.availability_view import AvailabilityView
from timetable_generator.views.batch_view import BatchView
from timetable_generator.views.conflict_view import ConflictView
from timetable_generator.views.constraints_view import ConstraintsView
from timetable_generator.views.course_view import CourseView
from timetable_generator.views.dashboard_view import DashboardView
from timetable_generator.views.export_view import ExportView
from timetable_generator.views.faculty_view import FacultyView
from timetable_generator.views.generate_view import GenerateView
from timetable_generator.views.room_view import RoomView
from timetable_generator.views.timetable_view import TimetableView
from timetable_generator.views.timeslot_view import TimeSlotView

ADMIN_LABEL = "Admin"
DEFAULT_SCREEN = "dashboard"


class MainWindow(QMainWindow):
    """Primary window orchestrating navigation and all feature screens."""

    def __init__(self) -> None:
        """Initialize main window shell and screen routing."""

        super().__init__()
        self.setWindowTitle("Time Table Generator - University Scheduling System")

        self._sidebar = Sidebar()
        self._stack = QStackedWidget()
        self._title_label = QLabel("Dashboard")
        self._title_label.setObjectName("heading")
        self._role_label = QLabel(ADMIN_LABEL)
        self._role_label.setObjectName("subtle")
        self._views: Dict[str, QWidget] = {}

        self._faculty_controller = FacultyController()
        self._course_controller = CourseController()
        self._batch_controller = BatchController()
        self._room_controller = RoomController()
        self._timeslot_controller = TimeSlotController()
        self._availability_controller = AvailabilityController()
        self._constraint_controller = ConstraintController()
        self._scheduler_controller = SchedulerController()
        self._export_controller = ExportController()
        self._timetable_controller = TimetableController()
        self._conflict_controller = ConflictController()

        self._build_ui()
        self._init_views()
        self.switch_screen(DEFAULT_SCREEN)

    def _build_ui(self) -> None:
        """Build shell layout with sidebar, top bar, and stacked content.

        Returns:
            None.
        """

        container = QWidget()
        self.setCentralWidget(container)

        root = QHBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(self._sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self._title_label)
        top_bar.addStretch(1)
        top_bar.addWidget(self._role_label)
        content_layout.addLayout(top_bar)
        content_layout.addWidget(self._stack)

        root.addWidget(content)

        self._sidebar.navigate.connect(self.switch_screen)

    def _init_views(self) -> None:
        """Instantiate all views and register them in the stacked widget.

        Returns:
            None.
        """

        dashboard = DashboardView(
            faculty_count=len(self._faculty_controller.get_all()),
            course_count=len(self._course_controller.get_all()),
            batch_count=len(self._batch_controller.get_all()),
            room_count=len(self._room_controller.get_all()),
            activities=mock_data.get_recent_activity(),
        )
        dashboard.navigate_requested.connect(self.switch_screen)

        faculty = FacultyView(self._faculty_controller, self._course_controller, self._timeslot_controller)
        courses = CourseView(self._course_controller)
        batches = BatchView(self._batch_controller, self._course_controller)
        rooms = RoomView(self._room_controller)
        timeslots = TimeSlotView(self._timeslot_controller)
        availability = AvailabilityView(self._availability_controller, self._timeslot_controller)
        constraints = ConstraintsView(self._constraint_controller)

        generate = GenerateView(self._scheduler_controller)
        generate.navigate_requested.connect(self.switch_screen)

        timetable = TimetableView(
            self._batch_controller,
            self._faculty_controller,
            self._room_controller,
            self._course_controller,
            self._timeslot_controller,
            self._timetable_controller,
            self._export_controller,
        )
        conflicts = ConflictView(self._conflict_controller, self._export_controller)
        export = ExportView(self._export_controller)

        mapping: Dict[str, QWidget] = {
            "dashboard": dashboard,
            "faculty": faculty,
            "courses": courses,
            "batches": batches,
            "rooms": rooms,
            "timeslots": timeslots,
            "availability": availability,
            "constraints": constraints,
            "generate": generate,
            "timetable": timetable,
            "conflicts": conflicts,
            "export": export,
        }

        for key, view in mapping.items():
            self._views[key] = view
            self._stack.addWidget(view)

    def switch_screen(self, screen_name: str) -> None:
        """Switch the stacked content area to selected view.

        Args:
            screen_name: Internal screen identifier.

        Returns:
            None.
        """

        if screen_name not in self._views:
            return
        widget = self._views[screen_name]
        self._stack.setCurrentWidget(widget)
        self._sidebar.set_active(screen_name)
        self._title_label.setText(screen_name.replace("_", " ").title())
