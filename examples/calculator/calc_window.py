"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
import logging
import os

from PyQt5.QtCore import Qt, QSignalMapper
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QAction, QDockWidget, QFileDialog, QMdiArea, QMessageBox

from examples.calculator.calc_conf import CALC_NODES
from examples.calculator.calc_drag_listbox import QDMDragListbox
from examples.calculator.calc_sub_window import CalculatorSubWindow

# Enabling edge validators
from node_editor.core.edge import Edge
from node_editor.tools.edge_validators import (
    edge_cannot_connect_input_and_output_of_same_node,
    edge_cannot_connect_two_outputs_or_two_inputs,
)
from node_editor.utils.helpers import dump_exception
from node_editor.utils.qt_helpers import loadStylesheets
from node_editor.widgets.editor_window import NodeEditorWindow

Edge.register_edge_validator(edge_cannot_connect_two_outputs_or_two_inputs)
Edge.register_edge_validator(edge_cannot_connect_input_and_output_of_same_node)

logger = logging.getLogger(__name__)

class CalculatorWindow(NodeEditorWindow):

    def init_ui(self):
        self.name_company = 'oncut'
        self.name_product = 'Calculator Node Editor'

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "qss/nodeeditor.qss")
        loadStylesheets(
            os.path.join(os.path.dirname(__file__), "qss/nodeeditor-dark.qss"),
            self.stylesheet_filename
        )

        self.empty_icon = QIcon(".")


        self.mdiArea = QMdiArea()
        # Mapper to activate MDI child windows from menu actions
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped.connect(lambda w: self.mdiArea.setActiveSubWindow(w))
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.update_menus)

        self.create_nodes_dock()

        self.create_actions()
        self.create_menus()
        self.create_tool_bars()
        self.create_status_bar()
        self.update_menus()

        self.read_settings()

        self.setWindowTitle("Calculator Node Editor Example")

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.write_settings()
            event.accept()
            # hacky fix for PyQt 5.14.x
            import sys
            sys.exit(0)


    def create_actions(self):
        super().create_actions()

        self.actClose = QAction("Cl&ose", self, statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = QAction("Close &All", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade = QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        self.actAbout = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)

    def get_current_node_editor_widget(self):
        """ we're returning NodeEditorWidget here... """
        active_sub_window = self.mdiArea.activeSubWindow()
        if active_sub_window:
            return active_sub_window.widget()
        return None

    def on_file_new(self):
        logger.info("on_file_new: Starting")
        try:
            logger.info("on_file_new: Creating MDI child")
            subwnd = self.create_mdi_child()
            logger.info("on_file_new: Calling file_new on widget")
            subwnd.widget().file_new()
            logger.info("on_file_new: Showing subwindow")
            subwnd.show()
            logger.info("on_file_new: Complete")
        except Exception as e:
            logger.error("on_file_new: Exception occurred", exc_info=True)
            dump_exception(e)


    def on_file_open(self):
        fnames, filter = QFileDialog.getOpenFileNames(
            self,
            'Open graph from file',
            self.get_file_dialog_directory(),
            self.get_file_dialog_filter(),
        )

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # we need to create new subWindow and open the file
                        nodeeditor = CalculatorSubWindow()
                        if nodeeditor.file_load(fname):
                            self.statusBar().showMessage(f"File {fname} loaded", 5000)
                            nodeeditor.set_title()
                            subwnd = self.create_mdi_child(nodeeditor)
                            subwnd.show()
                        else:
                            nodeeditor.close()
        except Exception as e:
            dump_exception(e)


    def about(self):
        QMessageBox.about(self, "About Calculator NodeEditor Example",
                "The <b>Calculator NodeEditor</b> example demonstrates how to write multiple "
                "document interface applications using PyQt5 and NodeEditor. For more information visit: "
                "<a href='https://www.blenderfreak.com/'>www.BlenderFreak.com</a>")

    def create_menus(self):
        super().create_menus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.update_window_menu()
        self.windowMenu.aboutToShow.connect(self.update_window_menu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actAbout)

        self.editMenu.aboutToShow.connect(self.update_edit_menu)

    def update_menus(self):
        active = self.get_current_node_editor_widget()
        has_mdi_child = (active is not None)

        self.actSave.setEnabled(has_mdi_child)
        self.actSaveAs.setEnabled(has_mdi_child)
        self.actClose.setEnabled(has_mdi_child)
        self.actCloseAll.setEnabled(has_mdi_child)
        self.actTile.setEnabled(has_mdi_child)
        self.actCascade.setEnabled(has_mdi_child)
        self.actNext.setEnabled(has_mdi_child)
        self.actPrevious.setEnabled(has_mdi_child)
        self.actSeparator.setVisible(has_mdi_child)

        self.update_edit_menu()

    def update_edit_menu(self):
        try:
            active = self.get_current_node_editor_widget()
            has_mdi_child = (active is not None)

            self.actPaste.setEnabled(has_mdi_child)

            self.actCut.setEnabled(has_mdi_child and active.has_selected_items())
            self.actCopy.setEnabled(has_mdi_child and active.has_selected_items())
            self.actDelete.setEnabled(has_mdi_child and active.has_selected_items())

            self.actUndo.setEnabled(has_mdi_child and active.can_undo())
            self.actRedo.setEnabled(has_mdi_child and active.can_redo())
        except Exception as e:
            dump_exception(e)



    def update_window_menu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction("Nodes Toolbar")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.on_window_nodes_toolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())

        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = f"{i + 1} {child.get_user_friendly_filename()}"
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.get_current_node_editor_widget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def on_window_nodes_toolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def create_tool_bars(self):
        pass

    def create_nodes_dock(self):
        self.nodesListWidget = QDMDragListbox()

        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    def create_status_bar(self):
        self.statusBar().showMessage("Ready")

    def create_mdi_child(self, child_widget=None):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("create_mdi_child: Starting")
        nodeeditor = child_widget if child_widget is not None else CalculatorSubWindow()
        logger.info("create_mdi_child: CalculatorSubWindow created")
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        logger.info("create_mdi_child: Added to MDI area")
        subwnd.setWindowIcon(self.empty_icon)
        # nodeeditor.scene.add_item_selected_listener(self.updateEditMenu)
        # nodeeditor.scene.add_items_deselected_listener(self.updateEditMenu)
        nodeeditor.scene.history.add_history_modified_listener(self.update_edit_menu)
        logger.info("create_mdi_child: Added history listener")
        nodeeditor.add_close_event_listener(self.on_sub_wnd_close)
        logger.info("create_mdi_child: Complete")
        return subwnd

    def on_sub_wnd_close(self, widget, event):
        existing = self.find_mdi_child(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybe_save():
            event.accept()
        else:
            event.ignore()


    def find_mdi_child(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None
