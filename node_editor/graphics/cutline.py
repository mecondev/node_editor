"""
Cut Line - Visual line for cutting edges.

This module provides the QDMCutLine class which represents a cutting line
that users can draw to cut through multiple edges at once.

Author: Michael Economou
Date: 2025-12-11
"""

from __future__ import annotations

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QWidget


class QDMCutLine(QGraphicsItem):
    """Graphics item representing a cutting line for cutting edges.

    The user can draw this line by holding Ctrl and left-clicking.
    All edges that intersect with the line will be removed.

    Attributes:
        line_points: List of QPointF representing the path of the line
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the cut line.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.line_points: list[QPointF] = []

        # White dashed pen
        self._pen = QPen(Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        # Draw on top of everything
        self.setZValue(2)

    def boundingRect(self) -> QRectF:
        """Get the bounding rectangle of the cut line.

        Returns:
            QRectF bounding rectangle
        """
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        """Calculate the painter path from line points.

        Returns:
            QPainterPath representing the cutting line
        """
        QPolygonF(self.line_points)

        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            # Return minimal path if no points
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPointF(1, 1))

        return path

    def paint(self, painter: QPainter, _option, _widget=None) -> None:
        """Paint the cutting line.

        Args:
            painter: QPainter to paint with
            option: Style options (unused)
            widget: Widget being painted on (unused)
        """
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)
