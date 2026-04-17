"""Export controller for CSV and PDF output generation."""

from __future__ import annotations

import csv
from typing import Any, Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class ExportController:
    """Controller handling report and timetable export operations."""

    def export_csv(self, data: List[dict], filepath: str) -> bool:
        """Export list of dictionaries to CSV file.

        Args:
            data: Rows represented as dictionaries.
            filepath: Destination CSV path.

        Returns:
            True when export succeeds, otherwise False.
        """

        try:
            if not data:
                with open(filepath, "w", newline="", encoding="utf-8") as handle:
                    handle.write("")
                return True
            headers = list(data[0].keys())
            with open(filepath, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception:
            return False

    def export_pdf(self, data: Dict[str, Any], filepath: str) -> bool:
        """Export dictionary payload into a simple PDF summary.

        Args:
            data: Dictionary report payload.
            filepath: Destination PDF path.

        Returns:
            True when export succeeds, otherwise False.
        """

        try:
            pdf = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            y = height - 40
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(40, y, "Time Table Generator Report")
            y -= 24
            pdf.setFont("Helvetica", 10)

            for key, value in data.items():
                text = f"{key}: {value}"
                pdf.drawString(40, y, text)
                y -= 16
                if y < 40:
                    pdf.showPage()
                    y = height - 40
                    pdf.setFont("Helvetica", 10)

            pdf.save()
            return True
        except Exception:
            return False
