"""
Graphics View - Main view widget for the node editor.

This module provides the QDMGraphicsView class which handles all user interactions
including zooming, panning, edge dragging, node selection, and edge cutting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import QEvent, QPoint, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QMouseEvent, QPainter, QWheelEvent
from PyQt5.QtWidgets import QApplication, QGraphicsView

from node_editor.utils.helpers import dump_exception
from node_editor.utils.qt_helpers import is_ctrl_pressed, is_shift_pressed

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QWidget

    from node_editor.graphics.scene import QDMGraphicsScene

# View mode constants
MODE_NOOP = 1               # Ready state
MODE_EDGE_DRAG = 2          # Dragging an edge
MODE_EDGE_CUT = 3           # Drawing cutting line
MODE_EDGES_REROUTING = 4    # Rerouting existing edges
MODE_NODE_DRAG = 5          # Dragging a node

STATE_STRING = ['', 'Noop', 'Edge Drag', 'Edge Cut', 'Edge Rerouting', 'Node Drag']

# Configuration constants
EDGE_DRAG_START_THRESHOLD = 50  # Distance threshold for edge drag
EDGE_REROUTING_UE = True        # Enable UnrealEngine style rerouting
EDGE_SNAPPING_RADIUS = 24       # Socket snapping distance
EDGE_SNAPPING = True            # Enable socket snapping

# Debug flags
DEBUG = False
DEBUG_MMB_SCENE_ITEMS = False
DEBUG_MMB_LAST_SELECTIONS = False
DEBUG_EDGE_INTERSECT = False
DEBUG_STATE = False


class QDMGraphicsView(QGraphicsView):
    """Graphics view for the node editor with zooming, panning, and interaction support.

    This class manages all user interactions including:
    - Zooming with mouse wheel
    - Panning with middle mouse button
    - Edge dragging and creation
    - Edge cutting
    - Node selection and dragging
    - Edge rerouting
    - Socket snapping

    Attributes:
        grScene: Reference to QDMGraphicsScene
        mode: Current interaction mode (MODE_NOOP, MODE_EDGE_DRAG, etc.)
        zoom: Current zoom level
        zoomInFactor: Zoom step scaling factor (default: 1.25)
        zoomClamp: Whether to clamp zooming
        zoomRange: Min/max zoom range
        last_scene_mouse_position: Last mouse position in scene coordinates

    Signals:
        scene_pos_changed: Emitted when cursor position changes (x, y)
    """

    # Signal for scene position changes
    scene_pos_changed = pyqtSignal(int, int)

    def __init__(self, gr_scene: QDMGraphicsScene, parent: QWidget | None = None) -> None:
        """Initialize the graphics view.

        Args:
            gr_scene: QDMGraphicsScene to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.grScene = gr_scene

        # Initialize UI
        self.initUI()
        self.setScene(self.grScene)

        # State management
        self.mode: int = MODE_NOOP
        self.editingFlag: bool = False
        self.rubberBandDraggingRectangle: bool = False

        # Edge dragging (late import to avoid circular dependencies)
        from node_editor.tools.edge_dragging import EdgeDragging
        self.dragging = EdgeDragging(self)

        # Edge rerouting
        from node_editor.tools.edge_rerouting import EdgeRerouting
        self.rerouting = EdgeRerouting(self)

        # Drop node on edge
        from node_editor.tools.edge_intersect import EdgeIntersect
        self.edgeIntersect = EdgeIntersect(self)

        # Socket snapping
        from node_editor.tools.edge_snapping import EdgeSnapping
        self.snapping = EdgeSnapping(self, snapping_radius=EDGE_SNAPPING_RADIUS)

        # Cut line
        from node_editor.graphics.cutline import QDMCutLine
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)

        # Mouse tracking
        self.last_scene_mouse_position = QPoint(0, 0)
        self.last_lmb_click_scene_pos: QPointF | None = None

        # Zoom settings
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        # Event listeners
        self._drag_enter_listeners: list = []
        self._drop_listeners: list = []

    def initUI(self) -> None:
        """Set up the graphics view."""
        # Rendering hints
        self.setRenderHints(
            QPainter.Antialiasing |
            QPainter.TextAntialiasing |
            QPainter.SmoothPixmapTransform
        )

        # Update mode
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # Hide scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Transformation and drag settings
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Enable dropping
        self.setAcceptDrops(True)

    def isSnappingEnabled(self, event: QMouseEvent | None = None) -> bool:
        """Check if socket snapping is currently enabled.

        Args:
            event: Mouse event (checks for Ctrl modifier)

        Returns:
            True if snapping is enabled
        """
        return EDGE_SNAPPING and is_ctrl_pressed(event) if event else True

    def resetMode(self) -> None:
        """Reset the view's state machine to default mode."""
        self.mode = MODE_NOOP

    # Event listener management

    def addDragEnterListener(self, callback) -> None:
        """Register callback for drag enter event.

        Args:
            callback: Function to call on drag enter
        """
        self._drag_enter_listeners.append(callback)

    def addDropListener(self, callback) -> None:
        """Register callback for drop event.

        Args:
            callback: Function to call on drop
        """
        self._drop_listeners.append(callback)

    # Qt event handlers

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events.

        Args:
            event: Drag enter event
        """
        for callback in self._drag_enter_listeners:
            callback(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events.

        Args:
            event: Drop event
        """
        for callback in self._drop_listeners:
            callback(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Dispatch mouse press event to corresponding function.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Dispatch mouse release event to corresponding function.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    # Middle mouse button - panning

    def middleMouseButtonPress(self, event: QMouseEvent) -> None:
        """Handle middle mouse button press for panning and debug info.

        Args:
            event: Mouse event
        """
        item = self.getItemAtClick(event)

        # Debug printout
        if DEBUG_MMB_SCENE_ITEMS:
            from node_editor.graphics.edge import QDMGraphicsEdge
            from node_editor.graphics.socket import QDMGraphicsSocket

            if isinstance(item, QDMGraphicsEdge):
                return

            if isinstance(item, QDMGraphicsSocket):
                if item.socket.edges:
                    for _edge in item.socket.edges:
                        pass
                return

        if DEBUG_MMB_SCENE_ITEMS and (item is None or self.mode == MODE_EDGES_REROUTING):
            for _node in self.grScene.scene.nodes:
                pass
            for _edge in self.grScene.scene.edges:
                pass

            if is_ctrl_pressed(event):
                for item in self.grScene.items():
                    pass

        if DEBUG_MMB_LAST_SELECTIONS and is_shift_pressed(event):
            return

        # Enable MMB dragging by faking left button events
        release_event = QMouseEvent(
            QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
            Qt.LeftButton, Qt.NoButton, event.modifiers()
        )
        super().mouseReleaseEvent(release_event)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        fake_event = QMouseEvent(
            event.type(), event.localPos(), event.screenPos(),
            Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers()
        )
        super().mousePressEvent(fake_event)

    def middleMouseButtonRelease(self, event: QMouseEvent) -> None:
        """Handle middle mouse button release to stop panning.

        Args:
            event: Mouse event
        """
        fake_event = QMouseEvent(
            event.type(), event.localPos(), event.screenPos(),
            Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers()
        )
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    # Left mouse button - main interactions

    def leftMouseButtonPress(self, event: QMouseEvent) -> None:
        """Handle left mouse button press for various interactions.

        Args:
            event: Mouse event
        """
        from node_editor.graphics.edge import QDMGraphicsEdge
        from node_editor.graphics.socket import QDMGraphicsSocket

        # Get clicked item
        item = self.getItemAtClick(event)

        # Store click position
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        # Logic: Shift + LMB for multi-select
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if is_shift_pressed(event):
                event.ignore()
                fake_event = QMouseEvent(
                    QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                    Qt.LeftButton, event.buttons() | Qt.LeftButton,
                    event.modifiers() | Qt.ControlModifier
                )
                super().mousePressEvent(fake_event)
                return

        # Start node dragging
        if hasattr(item, "node"):
            if DEBUG_EDGE_INTERSECT:
                pass
            if self.mode == MODE_NOOP:
                self.mode = MODE_NODE_DRAG
                self.edgeIntersect.enterState(item.node)
                if DEBUG_EDGE_INTERSECT:
                    pass

        # Socket snapping
        if self.isSnappingEnabled(event):
            item = self.snapping.getSnappedSocketItem(event)

        # Socket interactions
        if isinstance(item, QDMGraphicsSocket):
            # Ctrl+Click on socket with edges = rerouting mode
            if self.mode == MODE_NOOP and is_ctrl_pressed(event):
                socket = item.socket
                if socket.hasAnyEdge():
                    self.mode = MODE_EDGES_REROUTING
                    self.rerouting.startRerouting(socket)
                    return

            # Normal socket click = start edge drag
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.dragging.edgeDragStart(item)
                return

        # Finish edge drag
        if self.mode == MODE_EDGE_DRAG:
            res = self.dragging.edgeDragEnd(item)
            if res:
                return

        # Empty space click
        if item is None:
            if is_ctrl_pressed(event):
                # Ctrl+Click = start edge cutting
                self.mode = MODE_EDGE_CUT
                fake_event = QMouseEvent(
                    QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                    Qt.LeftButton, Qt.NoButton, event.modifiers()
                )
                super().mouseReleaseEvent(fake_event)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event: QMouseEvent) -> None:
        """Handle left mouse button release.

        Args:
            event: Mouse event
        """
        from node_editor.graphics.edge import QDMGraphicsEdge
        from node_editor.graphics.socket import QDMGraphicsSocket

        item = self.getItemAtClick(event)

        try:
            # Logic: Shift + LMB release
            if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
                if is_shift_pressed(event):
                    event.ignore()
                    fake_event = QMouseEvent(
                        event.type(), event.localPos(), event.screenPos(),
                        Qt.LeftButton, Qt.NoButton,
                        event.modifiers() | Qt.ControlModifier
                    )
                    super().mouseReleaseEvent(fake_event)
                    return

            # Finish edge drag
            if self.mode == MODE_EDGE_DRAG:
                if self.distanceBetweenClickAndReleaseIsOff(event):
                    if self.isSnappingEnabled(event):
                        item = self.snapping.getSnappedSocketItem(event)

                    res = self.dragging.edgeDragEnd(item)
                    if res:
                        return

            # Finish edge rerouting
            if self.mode == MODE_EDGES_REROUTING:
                if self.isSnappingEnabled(event):
                    item = self.snapping.getSnappedSocketItem(event)

                if not EDGE_REROUTING_UE:
                    if not self.rerouting.first_mb_release:
                        self.rerouting.first_mb_release = True
                        return

                self.rerouting.stopRerouting(
                    item.socket if isinstance(item, QDMGraphicsSocket) else None
                )
                self.mode = MODE_NOOP

            # Finish edge cutting
            if self.mode == MODE_EDGE_CUT:
                self.cutIntersectingEdges()
                self.cutline.line_points = []
                self.cutline.update()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.mode = MODE_NOOP
                return

            # Finish node dragging
            if self.mode == MODE_NODE_DRAG:
                scenepos = self.mapToScene(event.pos())
                self.edgeIntersect.leaveState(scenepos.x(), scenepos.y())
                self.mode = MODE_NOOP
                self.update()

            # Finish rubber band selection
            if self.rubberBandDraggingRectangle:
                self.rubberBandDraggingRectangle = False
                current_selected_items = self.grScene.selectedItems()

                if current_selected_items != self.grScene.scene._last_selected_items:
                    if current_selected_items == []:
                        self.grScene.itemsDeselected.emit()
                    else:
                        self.grScene.itemSelected.emit()
                    self.grScene.scene._last_selected_items = current_selected_items

                super().mouseReleaseEvent(event)
                return

            # Deselect on empty space
            if item is None:
                self.grScene.itemsDeselected.emit()

        except Exception as e:
            dump_exception(e)

        super().mouseReleaseEvent(event)

    # Right mouse button

    def rightMouseButtonPress(self, event: QMouseEvent) -> None:
        """Handle right mouse button press.

        Args:
            event: Mouse event
        """
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event: QMouseEvent) -> None:
        """Handle right mouse button release.

        Args:
            event: Mouse event
        """
        super().mouseReleaseEvent(event)

    # Mouse move

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move for updating interactions.

        Args:
            event: Mouse event
        """
        scenepos = self.mapToScene(event.pos())

        try:
            # Update socket highlights
            modified = self.setSocketHighlights(
                scenepos, highlighted=False, radius=EDGE_SNAPPING_RADIUS + 100
            )
            if self.isSnappingEnabled(event):
                _, scenepos = self.snapping.getSnappedToSocketPosition(scenepos)
            if modified:
                self.update()

            # Update based on mode
            if self.mode == MODE_EDGE_DRAG:
                self.dragging.updateDestination(scenepos.x(), scenepos.y())

            if self.mode == MODE_NODE_DRAG:
                self.edgeIntersect.update(scenepos.x(), scenepos.y())

            if self.mode == MODE_EDGES_REROUTING:
                self.rerouting.updateScenePos(scenepos.x(), scenepos.y())

            if self.mode == MODE_EDGE_CUT and self.cutline is not None:
                self.cutline.line_points.append(scenepos)
                self.cutline.update()

        except Exception as e:
            dump_exception(e)

        self.last_scene_mouse_position = scenepos
        self.scene_pos_changed.emit(int(scenepos.x()), int(scenepos.y()))

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events.

        Args:
            event: Key event
        """
        super().keyPressEvent(event)

    # Helper methods

    def cutIntersectingEdges(self) -> None:
        """Cut all edges that intersect with the current cut line."""
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            for edge in self.grScene.scene.edges.copy():
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.grScene.scene.history.storeHistory("Delete cutted edges", setModified=True)

    def setSocketHighlights(
        self, scenepos: QPointF, highlighted: bool = True, radius: float = 50
    ) -> list:
        """Set/disable socket highlights in scene area.

        Args:
            scenepos: Scene position to check around
            highlighted: Whether to highlight or unhighlight
            radius: Search radius

        Returns:
            List of affected socket items
        """
        from node_editor.graphics.socket import QDMGraphicsSocket

        scanrect = QRectF(
            scenepos.x() - radius, scenepos.y() - radius,
            radius * 2, radius * 2
        )
        items = self.grScene.items(scanrect)
        items = list(filter(lambda x: isinstance(x, QDMGraphicsSocket), items))

        for gr_socket in items:
            gr_socket.isHighlighted = highlighted

        return items

    def deleteSelected(self) -> None:
        """Delete all selected items in the scene."""
        from node_editor.graphics.edge import QDMGraphicsEdge

        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()

        self.grScene.scene.history.storeHistory("Delete selected", setModified=True)

    def getItemAtClick(self, event: QEvent):
        """Get the graphics item at the click position.

        Args:
            event: Mouse or key event

        Returns:
            QGraphicsItem at the position or None
        """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def distanceBetweenClickAndReleaseIsOff(self, event: QMouseEvent) -> bool:
        """Check if release is too far from click position.

        This is used to detect if we release too far after clicking on a socket.

        Args:
            event: Mouse event

        Returns:
            True if distance exceeds threshold
        """
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD * EDGE_DRAG_START_THRESHOLD
        return (dist_scene.x() ** 2 + dist_scene.y() ** 2) > edge_drag_threshold_sq

    # Zooming

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel for zooming.

        Args:
            event: Wheel event
        """
        # Calculate zoom factor
        zoom_out_factor = 1 / self.zoomInFactor

        # Calculate zoom direction
        if event.angleDelta().y() > 0:
            zoom_factor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoomStep

        # Clamp zoom
        clamped = False
        if self.zoom < self.zoomRange[0]:
            self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]:
            self.zoom, clamped = self.zoomRange[1], True

        # Apply zoom
        if not clamped or self.zoomClamp is False:
            self.scale(zoom_factor, zoom_factor)
