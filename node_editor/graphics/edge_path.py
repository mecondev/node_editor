"""Graphics edge path calculators for different edge styles."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainterPath

if TYPE_CHECKING:
    from node_editor.graphics.edge import QDMGraphicsEdge

# Edge path constants
EDGE_CP_ROUNDNESS = 100  # Bezier control point distance on the line
WEIGHT_SOURCE = 0.2  # Factor for square edge midpoint between start and end
EDGE_IBCP_ROUNDNESS = 75  # Scale curvature with distance
NODE_DISTANCE = 12
EDGE_CURVATURE = 2


class GraphicsEdgePathBase:
    """Base class for calculating graphics path to draw for an edge."""

    def __init__(self, owner: QDMGraphicsEdge):
        """Initialize path calculator.

        Args:
            owner: Reference to owner QDMGraphicsEdge
        """
        self.owner = owner

    def calcPath(self) -> QPainterPath | None:
        """Calculate the path to draw.

        Returns:
            QPainterPath or None
        """
        return None


class GraphicsEdgePathDirect(GraphicsEdgePathBase):
    """Direct line connection graphics edge."""

    def calcPath(self) -> QPainterPath:
        """Calculate direct line connection.

        Returns:
            QPainterPath of the direct line
        """
        path = QPainterPath(
            QPointF(self.owner.posSource[0], self.owner.posSource[1])
        )
        path.lineTo(self.owner.posDestination[0], self.owner.posDestination[1])
        return path


class GraphicsEdgePathBezier(GraphicsEdgePathBase):
    """Cubic Bezier line connection graphics edge."""

    def calcPath(self) -> QPainterPath:
        """Calculate cubic Bezier line with 2 control points.

        Returns:
            QPainterPath of the cubic Bezier line
        """
        s = self.owner.posSource
        d = self.owner.posDestination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.owner.edge.start_socket is not None:
            ssin = self.owner.edge.start_socket.is_input
            ssout = self.owner.edge.start_socket.is_output

            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = (
                    (s[1] - d[1])
                    / math.fabs((s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS
                cpy_s = (
                    (d[1] - s[1])
                    / math.fabs((d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS

        path = QPainterPath(
            QPointF(self.owner.posSource[0], self.owner.posSource[1])
        )
        path.cubicTo(
            s[0] + cpx_s,
            s[1] + cpy_s,
            d[0] + cpx_d,
            d[1] + cpy_d,
            self.owner.posDestination[0],
            self.owner.posDestination[1],
        )

        return path


class GraphicsEdgePathSquare(GraphicsEdgePathBase):
    """Square line connection graphics edge."""

    def __init__(self, *args, handle_weight: float = 0.5, **kwargs):
        """Initialize square path calculator.

        Args:
            handle_weight: Weight for midpoint calculation (0.0 to 1.0)
        """
        super().__init__(*args, **kwargs)
        self.rand = None
        self.handle_weight = handle_weight

    def calcPath(self) -> QPainterPath:
        """Calculate square edge line connection.

        Returns:
            QPainterPath of the edge square line
        """
        s = self.owner.posSource
        d = self.owner.posDestination

        mid_x = s[0] + ((d[0] - s[0]) * self.handle_weight)

        path = QPainterPath(QPointF(s[0], s[1]))
        path.lineTo(mid_x, s[1])
        path.lineTo(mid_x, d[1])
        path.lineTo(d[0], d[1])

        return path


class GraphicsEdgePathImprovedSharp(GraphicsEdgePathBase):
    """Improved sharp edge with horizontal segments."""

    def calcPath(self) -> QPainterPath:
        """Calculate improved sharp line connection.

        Returns:
            QPainterPath of the painting line
        """
        sx, sy = self.owner.posSource
        dx, dy = self.owner.posDestination
        distx, disty = dx - sx, dy - sy
        dist = math.sqrt(distx * distx + disty * disty)

        # Is start/end socket on left side?
        sleft = self.owner.edge.start_socket.position <= 3

        # If drag edge started from input socket, connect to output socket
        eleft = self.owner.edge.start_socket.position > 3

        if self.owner.edge.end_socket is not None:
            eleft = self.owner.edge.end_socket.position <= 3

        node_sdist = (-NODE_DISTANCE) if sleft else NODE_DISTANCE
        node_edist = (-NODE_DISTANCE) if eleft else NODE_DISTANCE

        path = QPainterPath(QPointF(sx, sy))

        if abs(dist) > NODE_DISTANCE:
            path.lineTo(sx + node_sdist, sy)
            path.lineTo(dx + node_edist, dy)

        path.lineTo(dx, dy)

        return path


class GraphicsEdgePathImprovedBezier(GraphicsEdgePathBase):
    """Improved Bezier curve edge with adaptive curvature."""

    def calcPath(self) -> QPainterPath:
        """Calculate improved Bezier line connection.

        Returns:
            QPainterPath of the painting line
        """
        sx, sy = self.owner.posSource
        dx, dy = self.owner.posDestination
        distx, disty = dx - sx, dy - sy
        dist = math.sqrt(distx * distx + disty * disty)

        # Is start/end socket on left side?
        sleft = self.owner.edge.start_socket.position <= 3

        # If drag edge started from input socket, connect to output socket
        eleft = self.owner.edge.start_socket.position > 3

        if self.owner.edge.end_socket is not None:
            eleft = self.owner.edge.end_socket.position <= 3

        path = QPainterPath(QPointF(sx, sy))

        if abs(dist) > NODE_DISTANCE:
            curvature = max(
                EDGE_CURVATURE, (EDGE_CURVATURE * abs(dist)) / EDGE_IBCP_ROUNDNESS
            )

            node_sdist = (-NODE_DISTANCE) if sleft else NODE_DISTANCE
            node_edist = (-NODE_DISTANCE) if eleft else NODE_DISTANCE

            path.lineTo(sx + node_sdist, sy)

            path.cubicTo(
                QPointF(sx + node_sdist * curvature, sy),
                QPointF(dx + node_edist * curvature, dy),
                QPointF(dx + node_edist, dy),
            )

            path.lineTo(dx + node_edist, dy)

        path.lineTo(dx, dy)

        return path
