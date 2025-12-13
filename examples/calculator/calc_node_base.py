"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QLabel

from node_editor.core.node import Node
from node_editor.core.socket import LEFT_CENTER, RIGHT_CENTER
from node_editor.graphics.node import QDMGraphicsNode
from node_editor.utils.helpers import dump_exception
from node_editor.widgets.content_widget import QDMNodeContentWidget


class CalcGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 74
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        self.icons = QImage("icons/status_icons.png")

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        offset = 24.0
        if self.node.isDirty():
            offset = 0.0
        if self.node.isInvalid():
            offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class CalcContent(QDMNodeContentWidget):
    def init_ui(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)


class CalcNode(Node):
    icon = ""
    op_code = 0
    op_title = "Undefined"
    content_label = ""
    content_label_objname = "calc_node_bg"

    _graphics_node_class = CalcGraphicsNode
    NodeContent_class = CalcContent

    def __init__(self, scene, inputs=None, outputs=None):
        if inputs is None:
            inputs = [2, 2]
        if outputs is None:
            outputs = [1]
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

        self.value = None

        # it's really important to mark all nodes Dirty by default
        self.mark_dirty()


    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def evalOperation(self, _input1, _input2):
        return 123

    def evalImplementation(self):
        i1 = self.getInput(0)
        i2 = self.getInput(1)

        if i1 is None or i2 is None:
            self.mark_invalid()
            self.mark_descendants_dirty()
            self.graphics_node.setToolTip("Connect all inputs")
            return None

        else:
            try:
                val = self.evalOperation(i1.eval(), i2.eval())
                self.value = val
                self.mark_dirty(False)
                self.mark_invalid(False)
                self.graphics_node.setToolTip("")

                self.mark_descendants_dirty()
                self.evalChildren()

                return val
            except ZeroDivisionError:
                self.mark_invalid()
                self.graphics_node.setToolTip("⚠ Cannot divide by zero")
                self.mark_descendants_dirty()
                return None
            except (ValueError, TypeError) as e:
                self.mark_invalid()
                self.graphics_node.setToolTip(f"⚠ Invalid input: {str(e)}")
                self.mark_descendants_dirty()
                return None

    def eval(self):
        if not self.isDirty() and not self.isInvalid():
            print(f" _> returning cached {self.__class__.__name__} value:", self.value)
            return self.value

        try:

            val = self.evalImplementation()
            return val
        except ValueError as e:
            self.mark_invalid()
            self.graphics_node.setToolTip(str(e))
            self.mark_descendants_dirty()
        except Exception as e:
            self.mark_invalid()
            self.graphics_node.setToolTip(str(e))
            dump_exception(e)



    def onInputChanged(self, _socket=None):
        print(f"{self.__class__.__name__}::__onInputChanged")
        self.mark_dirty()
        self.eval()


    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap=None, restore_id=True):
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap, restore_id)
        print(f"Deserialized CalcNode '{self.__class__.__name__}'", "res:", res)
        return res
