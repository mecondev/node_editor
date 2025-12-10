"""
Widgets module - Reusable Qt widgets for node editor.

Classes:
    - QDMNodeContentWidget: Base widget for node content
    - QDMTextEdit: Text edit with editing flag support
    - NodeEditorWidget: The main canvas widget (to be migrated)
    - NodeEditorWindow: Complete window with menus and toolbar (to be migrated)
"""

from node_editor.widgets.content_widget import QDMNodeContentWidget, QDMTextEdit

__all__ = ["QDMNodeContentWidget", "QDMTextEdit"]

# Will be populated after migration
# from node_editor.widgets.editor_widget import NodeEditorWidget
# from node_editor.widgets.editor_window import NodeEditorWindow
