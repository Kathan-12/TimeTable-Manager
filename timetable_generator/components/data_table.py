"""Reusable data table widget with sorting and helper methods."""

from __future__ import annotations

from typing import Any, Iterable, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem


class DataTable(QTableWidget):
    """A pre-styled read-only table component used for CRUD screens."""

    def __init__(self, headers: List[str], data: Iterable[Iterable[Any]] | None = None) -> None:
        """Initialize table structure and optional initial data.

        Args:
            headers: Table header labels.
            data: Optional 2D rows to populate.
        """

        super().__init__()
        self._headers = headers
        self._setup_table()
        self.load_data(list(data) if data else [])

    def _setup_table(self) -> None:
        """Apply table configuration for appearance and behavior.

        Returns:
            None.
        """

        self.setColumnCount(len(self._headers))
        self.setHorizontalHeaderLabels(self._headers)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

    def load_data(self, data: List[List[Any]]) -> None:
        """Load rows into the table replacing any existing content.

        Args:
            data: List of table rows.

        Returns:
            None.
        """

        self.setSortingEnabled(False)
        self.setRowCount(0)
        for row_idx, row_values in enumerate(data):
            self.insertRow(row_idx)
            for col_idx, value in enumerate(row_values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_idx, col_idx, item)
        self.setSortingEnabled(True)
        self.resizeColumnsToContents()

    def get_selected_row_id(self) -> int:
        """Return the ID from the first column of current selected row.

        Returns:
            Selected row identifier or -1 if no selection.
        """

        selected = self.selectionModel().selectedRows()
        if not selected:
            return -1
        row = selected[0].row()
        item = self.item(row, 0)
        if item is None:
            return -1
        try:
            return int(item.text())
        except ValueError:
            return -1
