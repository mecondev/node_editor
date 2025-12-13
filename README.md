# PyQt Node Editor

A portable, extensible framework for building node-based visual editors with PyQt5.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)
![Tests](https://img.shields.io/badge/tests-338%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## What is this?

**PyQt Node Editor** is a complete Python framework for creating visual node-based programming interfaces. Think Blender's node editor, Unreal Engine Blueprints, or audio software like Max/MSP – but for your own applications.

The framework is designed to be **portable**: simply copy the `node_editor/` folder into your project and start building custom node-based tools.

## Key Features

- **Portable Package**: Self-contained, copy-paste ready
- **Theme Engine**: Built-in dark/light themes with QSS stylesheet support
- **52 Built-in Nodes**: Math, logic, string, list, time, file I/O operations
- **Node Registry**: Decorator-based registration with unique operation codes
- **Full Serialization**: JSON save/load with undo/redo history
- **Edge Validators**: Customizable connection rules
- **Interactive Tools**: Edge dragging, rerouting, snapping, cut-line

## Σημαντικές αλλαγές — 2025-12-13

Έγινε μεγάλης κλίμακας refactor για να βελτιωθεί η ονοματολογία και η συνέπεια του API. Οι αλλαγές είναι breaking (δεν υπάρχουν aliases) — ελέγξτε και ενημερώστε τον κώδικά σας αν τον έχετε ενσωματώσει.

- Γενικό rename: όλα τα `gr*` identifiers (π.χ. `grView`, `gr_socket`, `grContent`) μετονομάστηκαν σε `graphics_*` (`graphics_view`, `graphics_socket`, `graphics_content`).
- Socket factory: `Socket_GR_Class` μετονομάστηκε σε `Socket_Graphics_Class` (binding στο `node_editor.core._init_graphics_classes`).
- Κατάργηση legacy aliases: η μέθοδος `Scene.is_modified()` αφαιρέθηκε — χρησιμοποιήστε την ιδιότητα `Scene.has_been_modified`.
- Helpers: τα helper functions για πληκτρολογικούς ελέγχους έγιναν snake_case: `is_ctrl_pressed`, `is_shift_pressed`, `is_alt_pressed` (παλιές camelCase συναρτήσεις αφαιρέθηκαν).
- Serialization: η παλαιά fallback λογική για `multi_edges` αφαιρέθηκε — τα serialized socket objects πρέπει πλέον να περιέχουν ρητά το πεδίο `multi_edges`.

Οδηγίες αναβάθμισης (γρήγορα):

1. Αντικαταστήστε `grView` → `graphics_view`, `grContent` → `graphics_content` σε custom code.
2. Χρησιμοποιήστε `Socket_Graphics_Class` αν κάνετε late-binding των graphics κλάσεων.
3. Αντικαταστήστε κλήσεις `scene.is_modified()` με `scene.has_been_modified`.
4. Κάντε search στο project σας για `isCTRLPressed`, `isSHIFTPressed`, `isALTPressed` και αλλάξτε σε snake_case αντίστοιχα.
5. Ελέγξτε τα JSON αρχεία που παράγετε: κάθε `socket` entry πρέπει τώρα να έχει `multi_edges` boolean.

Για οποιαδήποτε βοήθεια με την αναβάθμιση, πείτε μου ποια modules/παραδείγματα θέλετε να αναβαθμίσω αυτόματα.

## Installation

### Requirements

- Python 3.8+
- PyQt5 >= 5.15.0

### Option 1: Copy into your project (Recommended)

```bash
# Clone the repo
git clone https://github.com/mecondev/node_editor.git

# Copy the portable package into your project
cp -r node_editor/node_editor /path/to/your/project/
```

### Option 2: Install as package

```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # For development dependencies
```

## Quickstart

### Minimal Example

```python
import sys
from PyQt5.QtWidgets import QApplication
from node_editor import NodeEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NodeEditorWindow()
    window.show()
    sys.exit(app.exec_())
```

### Embedding in Your Application

```python
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from node_editor import NodeEditorWidget

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        container = QWidget()
        layout = QVBoxLayout(container)
        
        self.editor = NodeEditorWidget()
        layout.addWidget(self.editor)
        
        self.setCentralWidget(container)
```

### Creating Custom Nodes

```python
from node_editor.core.node import Node
from node_editor.nodes import NodeRegistry

@NodeRegistry.register(200)  # Use op_codes >= 100 for custom nodes
class MyCustomNode(Node):
    """Custom node with one input and one output."""
    
    def __init__(self, scene):
        super().__init__(scene, "My Node", inputs=[1], outputs=[1])
        self.markDirty()
    
    def eval(self):
        """Evaluate the node."""
        input_val = self.getInput(0)
        if input_val is None:
            self.markInvalid()
            return None
        
        # Your custom logic here
        result = input_val.eval() * 2
        
        self.value = result
        self.markDirty(False)
        self.markInvalid(False)
        return result
```

## Themes

### Switching Themes

```python
from node_editor.themes import ThemeEngine, DarkTheme, LightTheme

# Register themes (done automatically on first use)
ThemeEngine.register_theme(DarkTheme)
ThemeEngine.register_theme(LightTheme)

# List available themes
print(ThemeEngine.available_themes())  # ['dark', 'light']

# Switch theme
ThemeEngine.set_theme("light")

# Refresh existing graphics items after theme change
ThemeEngine.refresh_graphics_items(editor.scene)

# Get current theme for accessing colors
theme = ThemeEngine.current_theme()
print(theme.node_background)  # QColor object
```

### Creating Custom Themes

Create a new theme by subclassing `BaseTheme`:

```python
from node_editor.themes import BaseTheme, ThemeEngine
from PyQt5.QtGui import QColor

class MyTheme(BaseTheme):
    name = "mytheme"
    display_name = "My Custom Theme"
    
    scene_background = QColor("#1a1a2e")
    node_background = QColor("#16213e")
    node_title_background = QColor("#0f3460")
    # ... override other colors as needed

# Register and use
ThemeEngine.register_theme(MyTheme)
ThemeEngine.set_theme("mytheme")
```

## Node System

### Built-in Nodes (Op Codes)

| Category | Nodes | Op Codes |
|----------|-------|----------|
| **Input** | NumberInput, TextInput | 1-2 |
| **Output** | Output | 3 |
| **Math** | Add, Subtract, Multiply, Divide | 10-13 |
| **Math Extended** | Power, Sqrt, Abs, Min, Max, Round, Modulo | 50-56 |
| **Comparison** | Equal, NotEqual, LessThan, LessEqual, GreaterThan, GreaterEqual | 20-25 |
| **Logic** | If, And, Or, Not, Xor | 26, 60-63 |
| **String** | Concatenate, Format, Length, Substring, Split | 40-44 |
| **Conversion** | ToString, ToNumber, ToBool, ToInt | 70-73 |
| **Utility** | Constant, Print, Comment, Clamp, Random | 80-84 |
| **List** | CreateList, GetItem, ListLength, Append, Join | 90-94 |
| **Time** | CurrentTime, FormatDate, ParseDate, TimeDelta, CompareTime | 100-104 |
| **Advanced** | RegexMatch, FileRead, FileWrite, HttpRequest | 110-113 |

### Node Registration Convention

- **1-99**: Reserved for built-in framework nodes
- **100+**: Available for custom application nodes

```python
@NodeRegistry.register(150)  # Your custom op_code
class MyApplicationNode(Node):
    pass
```

## Serialization

### Save/Load Graphs

```python
# Save to file
editor.scene.saveToFile("my_graph.json")

# Load from file
editor.scene.loadFromFile("my_graph.json")

# Manual serialization
data = editor.scene.serialize()  # Returns OrderedDict with version field
editor.scene.deserialize(data)   # Restores state, handles version migrations
```

### JSON Format

```json
{
    "version": "1.0.0",
    "id": 12345,
    "scene_width": 64000,
    "scene_height": 64000,
    "nodes": [
        {
            "id": 67890,
            "title": "Add",
            "pos_x": 100,
            "pos_y": 200,
            "inputs": [...],
            "outputs": [...],
            "content": {}
        }
    ],
    "edges": [
        {
            "id": 11111,
            "edge_type": 2,
            "start": 22222,
            "end": 33333
        }
    ]
}
```

**Note:** The `version` field enables backward-compatible migrations when the format changes.

## Running Examples

### Calculator Example

A full-featured calculator application demonstrating MDI, custom nodes, and drag-and-drop:

```bash
cd examples/calculator
python main.py
```

### Minimal Example

Basic NodeEditorWindow showcase:

```bash
cd examples/minimal
python main.py
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=node_editor

# Run specific test file
pytest tests/test_nodes_math.py
```

**Test Status**: 338 tests passing

## Project Structure

```
node_editor/                    # Root repository
├── main.py                     # Demo entry point
├── config.py                   # App configuration
├── requirements.txt
├── pyproject.toml
│
├── node_editor/                # THE PORTABLE PACKAGE
│   ├── __init__.py             # Public API exports
│   │
│   ├── core/                   # Framework core
│   │   ├── node.py             # Node class
│   │   ├── edge.py             # Edge class
│   │   ├── socket.py           # Socket class
│   │   ├── scene.py            # Scene manager
│   │   ├── history.py          # Undo/redo
│   │   └── clipboard.py        # Copy/paste
│   │
│   ├── graphics/               # Qt graphics items
│   │   ├── view.py             # QGraphicsView
│   │   ├── scene.py            # QGraphicsScene
│   │   ├── node.py             # Node graphics
│   │   ├── edge.py             # Edge graphics
│   │   └── socket.py           # Socket graphics
│   │
│   ├── widgets/                # Embeddable widgets
│   │   ├── editor_widget.py    # NodeEditorWidget
│   │   ├── editor_window.py    # NodeEditorWindow
│   │   └── content_widget.py   # Node content base
│   │
│   ├── nodes/                  # Built-in nodes
│   │   ├── registry.py         # Node registration
│   │   ├── math_nodes.py       # Arithmetic
│   │   ├── logic_nodes.py      # Comparisons, boolean
│   │   ├── string_nodes.py     # String operations
│   │   └── ...                 # More node types
│   │
│   ├── themes/                 # Theme engine
│   │   ├── theme_engine.py     # Theme manager
│   │   ├── base_theme.py       # Base theme class
│   │   ├── dark/               # Dark theme
│   │   └── light/              # Light theme
│   │
│   ├── tools/                  # Interactive tools
│   │   ├── edge_dragging.py
│   │   ├── edge_validators.py
│   │   └── ...
│   │
│   └── utils/                  # Helpers
│       ├── qt_helpers.py
│       └── helpers.py
│
├── examples/                   # Example applications
│   ├── calculator/             # Full calculator app
│   └── minimal/                # Basic example
│
├── tests/                      # Unit tests
│
└── docs/                       # Documentation
```

## Public API Summary

### Core Classes

```python
from node_editor import (
    Node,               # Base node class
    Edge,               # Connection class
    Socket,             # Connection point class
)
```

### Widgets

```python
from node_editor import (
    NodeEditorWidget,   # Embeddable canvas
    NodeEditorWindow,   # Full application window
)
```

### Node System

```python
from node_editor.nodes import (
    NodeRegistry,       # Registration system
    
    # Built-in nodes
    AddNode, SubtractNode, MultiplyNode, DivideNode,
    NumberInputNode, TextInputNode, OutputNode,
    # ... and 40+ more
)
```

### Themes

```python
from node_editor.themes import (
    ThemeEngine,        # Theme manager
    BaseTheme,          # For custom themes
    DarkTheme,          # Built-in dark
    LightTheme,         # Built-in light
)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Write tests for your changes
4. Ensure `pytest` and `ruff check .` pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Based on the original nodeeditor framework, refactored for modularity and portability.

---

**Author**: Michael Economou  
**Version**: 1.0.0  
**Date**: 2025-12-12
