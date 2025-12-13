"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
import logging
import os

from PyQt5.QtCore import QDataStream, QIODevice, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGraphicsProxyWidget, QMenu

from examples.calculator.calc_conf import CALC_NODES, LISTBOX_MIMETYPE, get_class_from_opcode
from node_editor.core.edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT, EDGE_TYPE_SQUARE
from node_editor.graphics.view import MODE_EDGE_DRAG
from node_editor.utils.helpers import dump_exception
from node_editor.widgets.editor_widget import NodeEditorWidget

logger = logging.getLogger(__name__)


def get_icon_path(relative_path):
    """Get absolute path for icon file."""
    return os.path.join(os.path.dirname(__file__), relative_path)


class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        logger.info("CalculatorSubWindow.__init__: Starting")
        super().__init__()
        logger.info("CalculatorSubWindow.__init__: super().__init__() complete")
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self.set_title()
        logger.info("CalculatorSubWindow.__init__: Title set")

        self.init_new_node_actions()
        logger.info("CalculatorSubWindow.__init__: Node actions initialized")

        self.scene.add_has_been_modified_listener(self.set_title)
        self.scene.add_has_been_modified_listener(self.on_scene_modified)
        self.scene.history.add_history_restored_listener(self.on_history_restored)
        # Add drag/drop listeners directly to the view to avoid premature view access
        self.view.add_drag_enter_listener(self.on_drag_enter)
        self.view.add_drop_listener(self.on_drop)
        self.scene.set_node_class_selector(self.get_node_class_from_data)
        logger.info("CalculatorSubWindow.__init__: Listeners registered")

        self._close_event_listeners = []
        self._last_edge_count = 0
        logger.info("CalculatorSubWindow.__init__: Complete")

    def get_node_class_from_data(self, data):
        if 'op_code' not in data:
            from node_editor.core.node import Node
            return Node
        return get_class_from_opcode(data['op_code'])

    def do_eval_outputs(self):
        # eval all output nodes
        for node in self.scene.nodes:
            if node.__class__.__name__ == "CalcNodeOutput":
                node.mark_dirty()  # Force re-evaluation
                node.value = None  # Clear cached value
                node.eval()

    def on_history_restored(self):
        self.do_eval_outputs()

    def on_scene_modified(self):
        """Called when scene is modified - re-evaluate outputs."""
        self.do_eval_outputs()

    def file_load(self, filename):
        if super().file_load(filename):
            self.do_eval_outputs()
            return True

        return False

    def init_new_node_actions(self):
        self.node_actions = {}
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = CALC_NODES[key]
            icon_path = get_icon_path(node.icon)
            self.node_actions[node.op_code] = QAction(QIcon(icon_path), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def init_nodes_context_menu(self):
        context_menu = QMenu(self)
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = CALC_NODES[key]
            context_menu.addAction(self.node_actions[node.op_code])
        return context_menu

    def set_title(self):
        self.setWindowTitle(self.get_user_friendly_filename())

    def add_close_event_listener(self, callback):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners:
            callback(self, event)

    def on_drag_enter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            logger.debug("Drag enter event denied: unsupported MIME type")
            event.setAccepted(False)

    def on_drop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event_data = event.mimeData().data(LISTBOX_MIMETYPE)
            data_stream = QDataStream(event_data, QIODevice.ReadOnly)
            pixmap = QPixmap()
            data_stream >> pixmap
            op_code = data_stream.readInt()
            _ = data_stream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.graphics_scene.views()[0].mapToScene(mouse_position)

            try:
                node = get_class_from_opcode(op_code)(self.scene)
                node.set_pos(scene_position.x(), scene_position.y())
                self.scene.history.store_history(f"Created node {node.__class__.__name__}")
            except Exception as e:
                dump_exception(e)


            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()


    def contextMenuEvent(self, event):
        try:
            item = self.scene.get_item_at(event.pos())

            if isinstance(item, QGraphicsProxyWidget):
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handle_node_context_menu(event)
            elif hasattr(item, 'edge'):
                self.handle_edge_context_menu(event)
            #elif item is None:
            else:
                self.handle_new_node_context_menu(event)

            return super().contextMenuEvent(event)
        except Exception as e:
            dump_exception(e)

    def handle_node_context_menu(self, event):
        context_menu = QMenu(self)
        mark_dirty_act = context_menu.addAction("Mark Dirty")
        mark_dirty_descendants_act = context_menu.addAction("Mark Descendant Dirty")
        mark_invalid_act = context_menu.addAction("Mark Invalid")
        unmark_invalid_act = context_menu.addAction("Unmark Invalid")
        eval_act = context_menu.addAction("Eval")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.get_item_at(event.pos())
        if isinstance(item, QGraphicsProxyWidget):
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node
        if hasattr(item, 'socket'):
            selected = item.socket.node

        if selected and action == mark_dirty_act:
            selected.mark_dirty()
        if selected and action == mark_dirty_descendants_act:
            selected.mark_descendants_dirty()
        if selected and action == mark_invalid_act:
            selected.mark_invalid()
        if selected and action == unmark_invalid_act:
            selected.mark_invalid(False)
        if selected and action == eval_act:
            val = selected.eval()
            logger.info("Evaluated node %s with result %s", selected.__class__.__name__, val)


    def handle_edge_context_menu(self, event):
        context_menu = QMenu(self)
        bezier_act = context_menu.addAction("Bezier Edge")
        direct_act = context_menu.addAction("Direct Edge")
        square_act = context_menu.addAction("Square Edge")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.get_item_at(event.pos())
        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezier_act:
            selected.edge_type = EDGE_TYPE_BEZIER
        if selected and action == direct_act:
            selected.edge_type = EDGE_TYPE_DIRECT
        if selected and action == square_act:
            selected.edge_type = EDGE_TYPE_SQUARE

    # helper functions
    def determine_target_socket_of_node(self, was_dragged_flag, new_calc_node):
        target_socket = None
        if was_dragged_flag:
            if len(new_calc_node.inputs) > 0:
                target_socket = new_calc_node.inputs[0]
        else:
            if len(new_calc_node.outputs) > 0:
                target_socket = new_calc_node.outputs[0]
        return target_socket

    def finish_new_node_state(self, new_calc_node):
        self.scene.do_deselect_items()
        new_calc_node.graphics_node.do_select(True)
        new_calc_node.graphics_node.on_selected()


    def handle_new_node_context_menu(self, event):
        context_menu = self.init_nodes_context_menu()
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            new_calc_node = get_class_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.get_view().mapToScene(event.pos())
            new_calc_node.set_pos(scene_pos.x(), scene_pos.y())

            if self.scene.get_view().mode == MODE_EDGE_DRAG:
                # if we were dragging an edge...
                target_socket = self.determine_target_socket_of_node(self.scene.get_view().dragging.drag_start_socket.is_output, new_calc_node)
                if target_socket is not None:
                    self.scene.get_view().dragging.edge_drag_end(target_socket.graphics_socket)
                    self.finish_new_node_state(new_calc_node)

            else:
                self.scene.history.store_history(f"Created {new_calc_node.__class__.__name__}")
