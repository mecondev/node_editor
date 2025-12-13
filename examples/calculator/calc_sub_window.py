"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
from PyQt5.QtCore import QDataStream, QIODevice, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QGraphicsProxyWidget, QMenu

from examples.calculator.calc_conf import CALC_NODES, LISTBOX_MIMETYPE, get_class_from_opcode
from node_editor.core.edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT, EDGE_TYPE_SQUARE
from node_editor.graphics.view import MODE_EDGE_DRAG
from node_editor.utils.helpers import dump_exception
from node_editor.widgets.editor_widget import NodeEditorWidget

DEBUG = False
DEBUG_CONTEXT = False


class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        # self.setAttribute(Qt.WA_DeleteOnClose)

        self.set_title()

        self.initNewNodeActions()

        self.scene.addHasBeenModifiedListener(self.set_title)
        self.scene.history.addHistoryRestoredListener(self.onHistoryRestored)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self._close_event_listeners = []

    def get_node_class_from_data(self, data):
        if 'op_code' not in data:
            from node_editor.core.node import Node
            return Node
        return get_class_from_opcode(data['op_code'])

    def do_eval_outputs(self):
        # eval all output nodes
        for node in self.scene.nodes:
            if node.__class__.__name__ == "CalcNode_Output":
                node.eval()

    def on_history_restored(self):
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
            self.node_actions[node.op_code] = QAction(QIcon(node.icon), node.op_title)
            self.node_actions[node.op_code].setData(node.op_code)

    def init_nodes_context_menu(self):
        context_menu = QMenu(self)
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            context_menu.addAction(self.node_actions[key])
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
            # print(" ... denied drag enter event")
            event.setAccepted(False)

    def on_drop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event_data = event.mimeData().data(LISTBOX_MIMETYPE)
            data_stream = QDataStream(event_data, QIODevice.ReadOnly)
            pixmap = QPixmap()
            data_stream >> pixmap
            op_code = data_stream.readInt()
            text = data_stream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.graphics_scene.views()[0].mapToScene(mouse_position)

            if DEBUG:
                print(f"GOT DROP: [{op_code}] '{text}'", "mouse:", mouse_position, "scene:", scene_position)

            try:
                node = get_class_from_opcode(op_code)(self.scene)
                node.set_pos(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory(f"Created node {node.__class__.__name__}")
            except Exception as e:
                dump_exception(e)


            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            # print(" ... drop ignored, not requested format '%s'" % LISTBOX_MIMETYPE)
            event.ignore()


    def contextMenuEvent(self, event):
        try:
            item = self.scene.getItemAt(event.pos())
            if DEBUG_CONTEXT:
                print(item)

            if isinstance(item, QGraphicsProxyWidget):
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handleNodeContextMenu(event)
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)
            #elif item is None:
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e:
            dump_exception(e)

    def handle_node_context_menu(self, event):
        if DEBUG_CONTEXT:
            print("CONTEXT: NODE")
        context_menu = QMenu(self)
        mark_dirty_act = context_menu.addAction("Mark Dirty")
        mark_dirty_descendants_act = context_menu.addAction("Mark Descendant Dirty")
        mark_invalid_act = context_menu.addAction("Mark Invalid")
        unmark_invalid_act = context_menu.addAction("Unmark Invalid")
        eval_act = context_menu.addAction("Eval")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
        if isinstance(item, QGraphicsProxyWidget):
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node
        if hasattr(item, 'socket'):
            selected = item.socket.node

        if DEBUG_CONTEXT:
            print("got item:", selected)
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
            if DEBUG_CONTEXT:
                print("EVALUATED:", val)


    def handle_edge_context_menu(self, event):
        if DEBUG_CONTEXT:
            print("CONTEXT: EDGE")
        context_menu = QMenu(self)
        bezier_act = context_menu.addAction("Bezier Edge")
        direct_act = context_menu.addAction("Direct Edge")
        square_act = context_menu.addAction("Square Edge")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())
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
        self.scene.doDeselectItems()
        new_calc_node.graphics_node.do_select(True)
        new_calc_node.graphics_node.on_selected()


    def handle_new_node_context_menu(self, event):

        if DEBUG_CONTEXT:
            print("CONTEXT: EMPTY SPACE")
        context_menu = self.initNodesContextMenu()
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            new_calc_node = get_class_from_opcode(action.data())(self.scene)
            scene_pos = self.scene.getView().mapToScene(event.pos())
            new_calc_node.set_pos(scene_pos.x(), scene_pos.y())
            if DEBUG_CONTEXT:
                print("Selected node:", new_calc_node)

            if self.scene.getView().mode == MODE_EDGE_DRAG:
                # if we were dragging an edge...
                target_socket = self.determine_target_socket_of_node(self.scene.getView().dragging.drag_start_socket.is_output, new_calc_node)
                if target_socket is not None:
                    self.scene.getView().dragging.edgeDragEnd(target_socket.graphics_socket)
                    self.finish_new_node_state(new_calc_node)

            else:
                self.scene.history.storeHistory(f"Created {new_calc_node.__class__.__name__}")
