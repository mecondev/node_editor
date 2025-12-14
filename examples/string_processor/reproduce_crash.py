import logging
import os
import sys

from PyQt5.QtWidgets import QApplication

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from examples.string_processor.str_window import StringProcessorWindow

logging.basicConfig(level=logging.DEBUG)

def main():
    QApplication(sys.argv)
    window = StringProcessorWindow()
    window.show()

    # Load the problematic file
    filename = os.path.join(os.path.dirname(__file__), "reproduce_issue.json")
    window.nodeeditor.file_load(filename)

    # Find the node (it should be a base Node because op_code is missing)
    node = window.nodeeditor.scene.nodes[0]
    print(f"Node class: {node.__class__.__name__}")

    # Select the node
    node.graphics_node.setSelected(True)

    # Delete selected
    print("Deleting selected node...")
    window.nodeeditor.view.delete_selected()
    print("Deletion complete.")

    # Check if scene is empty
    print(f"Nodes remaining: {len(window.nodeeditor.scene.nodes)}")

    # sys.exit(app.exec_())

if __name__ == "__main__":
    main()
