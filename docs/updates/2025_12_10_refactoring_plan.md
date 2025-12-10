# Node Editor Refactoring Plan

**Date:** 2025-12-10  
**Status:** Planning  
**Goal:** Transform node_editor into a portable, self-contained, modular framework

---

## 1. Executive Summary

### Current State Problems
- Tightly coupled with examples (calculator nodes inside examples/)
- No theme engine (hardcoded colors in Python files)
- Package name `nodeeditor` inconsistent with Python conventions
- Requires installation or complex path manipulation
- Examples depend on framework internals

### Target State
- **Self-contained** folder that can be copy-pasted to any project
- **Theme engine** with .py config + .qss stylesheets
- **Generic nodes** as part of the framework
- **Calculator** becomes a standalone example using the framework as wrapper
- **Modular architecture** allowing custom nodes in external projects

---

## 2. Proposed Directory Structure

```
node_editor/                    # Root folder (this repo)
├── main.py                     # Demo/development entry point
├── config.py                   # App-level configuration
├── requirements.txt
├── pyproject.toml
│
├── node_editor/                # THE PORTABLE PACKAGE (copy this to other projects)
│   ├── __init__.py             # Package init, version, public API exports
│   │
│   ├── core/                   # Core framework (DO NOT MODIFY)
│   │   ├── __init__.py
│   │   ├── node.py             # Base Node class
│   │   ├── edge.py             # Edge class
│   │   ├── socket.py           # Socket class
│   │   ├── scene.py            # Scene management
│   │   ├── serializable.py     # Serialization base class
│   │   ├── history.py          # Undo/redo system
│   │   └── clipboard.py        # Copy/paste functionality
│   │
│   ├── graphics/               # Qt Graphics classes
│   │   ├── __init__.py
│   │   ├── view.py             # QDMGraphicsView
│   │   ├── scene.py            # QDMGraphicsScene
│   │   ├── node.py             # QDMGraphicsNode
│   │   ├── edge.py             # QDMGraphicsEdge
│   │   ├── edge_path.py        # Edge path calculators
│   │   ├── socket.py           # QDMGraphicsSocket
│   │   └── cutline.py          # Cutting line graphics
│   │
│   ├── widgets/                # Reusable Qt widgets
│   │   ├── __init__.py
│   │   ├── editor_widget.py    # NodeEditorWidget (the canvas)
│   │   ├── editor_window.py    # NodeEditorWindow (full window with menus)
│   │   └── content_widget.py   # Base node content widget
│   │
│   ├── nodes/                  # Built-in generic nodes
│   │   ├── __init__.py
│   │   ├── registry.py         # Node registration system
│   │   ├── base.py             # Base classes for custom nodes
│   │   ├── input_node.py       # Number/Text input
│   │   ├── output_node.py      # Display/Output
│   │   ├── math_nodes.py       # Add, Sub, Mul, Div
│   │   └── logic_nodes.py      # Compare, If/Switch
│   │
│   ├── edge_tools/             # Edge-related utilities
│   │   ├── __init__.py
│   │   ├── dragging.py         # Edge dragging behavior
│   │   ├── validators.py       # Edge validation logic
│   │   ├── snapping.py         # Edge snapping
│   │   ├── rerouting.py        # Edge rerouting
│   │   └── intersect.py        # Intersection detection
│   │
│   ├── themes/                 # Theme engine
│   │   ├── __init__.py
│   │   ├── theme_engine.py     # Theme loading/switching logic
│   │   ├── base_theme.py       # Base theme class
│   │   ├── dark/               # Dark theme
│   │   │   ├── __init__.py
│   │   │   ├── theme.py        # Color definitions
│   │   │   └── style.qss       # Qt stylesheet
│   │   └── light/              # Light theme
│   │       ├── __init__.py
│   │       ├── theme.py        # Color definitions
│   │       └── style.qss       # Qt stylesheet
│   │
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── helpers.py          # General helpers
│       └── qt_helpers.py       # Qt-specific helpers (stylesheet loading)
│
├── examples/                   # Example applications (NOT part of portable package)
│   ├── calculator/             # Calculator app using node_editor as wrapper
│   │   ├── main.py
│   │   ├── calculator_window.py
│   │   ├── nodes/              # Calculator-specific nodes
│   │   │   ├── __init__.py
│   │   │   ├── calc_input.py
│   │   │   ├── calc_output.py
│   │   │   └── calc_operations.py
│   │   ├── resources/
│   │   │   ├── icons/
│   │   │   └── styles/
│   │   └── data/               # Example graph files
│   │       └── example.json
│   │
│   └── minimal/                # Minimal example (simplest usage)
│       └── main.py
│
├── tests/                      # Unit tests
│
└── docs/                       # Documentation
    └── updates/                # Planning documents
```

---

## 3. Theme Engine Design

### 3.1 Theme Structure

Each theme consists of:
- **theme.py** - Python file with color constants and node styling
- **style.qss** - Qt stylesheet for widget styling

### 3.2 Theme Python File (theme.py)

```python
# node_editor/themes/dark/theme.py

from PyQt5.QtGui import QColor, QFont

class DarkTheme:
    """Dark theme color definitions."""
    
    # Theme metadata
    name = "dark"
    display_name = "Dark Theme"
    
    # Scene colors
    scene_background = QColor("#393939")
    scene_grid_light = QColor("#2f2f2f")
    scene_grid_dark = QColor("#292929")
    
    # Node colors
    node_background = QColor("#E3212121")
    node_title_background = QColor("#FF313131")
    node_title_color = QColor("#FFFFFF")
    node_border_default = QColor("#7F000000")
    node_border_selected = QColor("#FFFFA637")
    node_border_hovered = QColor("#FF37A6FF")
    
    # Edge colors
    edge_color_default = QColor("#001000")
    edge_color_selected = QColor("#00ff00")
    edge_color_dragging = QColor("#FFFFFF")
    
    # Socket colors by type
    socket_colors = [
        QColor("#FFFF7700"),  # Type 0 - Orange
        QColor("#FF52e220"),  # Type 1 - Green
        QColor("#FF0056a6"),  # Type 2 - Blue
        QColor("#FFa86db1"),  # Type 3 - Purple
        QColor("#FFb54747"),  # Type 4 - Red
        QColor("#FFdbe220"),  # Type 5 - Yellow
    ]
    
    # Fonts
    node_title_font = QFont("Ubuntu", 10)
    
    # Dimensions (can also be themed)
    node_border_radius = 10.0
    node_padding = 10
    socket_radius = 6
```

### 3.3 Theme Engine (theme_engine.py)

```python
# node_editor/themes/theme_engine.py

import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile

class ThemeEngine:
    """Manages theme loading and switching."""
    
    _current_theme = None
    _themes = {}
    
    @classmethod
    def register_theme(cls, theme_class):
        """Register a theme class."""
        cls._themes[theme_class.name] = theme_class
    
    @classmethod
    def get_theme(cls, name: str = None):
        """Get current theme or theme by name."""
        if name:
            return cls._themes.get(name)
        return cls._current_theme
    
    @classmethod
    def set_theme(cls, name: str):
        """Set the current theme."""
        if name not in cls._themes:
            raise ValueError(f"Theme '{name}' not registered")
        
        cls._current_theme = cls._themes[name]
        cls._apply_stylesheet(name)
    
    @classmethod
    def _apply_stylesheet(cls, theme_name: str):
        """Load and apply the QSS stylesheet."""
        theme_dir = os.path.dirname(__file__)
        qss_path = os.path.join(theme_dir, theme_name, "style.qss")
        
        if os.path.exists(qss_path):
            file = QFile(qss_path)
            file.open(QFile.ReadOnly | QFile.Text)
            stylesheet = str(file.readAll(), encoding='utf-8')
            QApplication.instance().setStyleSheet(stylesheet)
    
    @classmethod
    def available_themes(cls) -> list:
        """Return list of available theme names."""
        return list(cls._themes.keys())
```

### 3.4 Usage in Graphics Classes

```python
# Example: node_editor/graphics/node.py

from node_editor.themes import ThemeEngine

class QDMGraphicsNode(QGraphicsItem):
    def initAssets(self):
        theme = ThemeEngine.get_theme()
        
        self._title_color = theme.node_title_color
        self._title_font = theme.node_title_font
        self._color = theme.node_border_default
        self._color_selected = theme.node_border_selected
        self._brush_title = QBrush(theme.node_title_background)
        self._brush_background = QBrush(theme.node_background)
```

---

## 4. Node System Design

### 4.1 Base Node Classes

```python
# node_editor/nodes/base.py

from node_editor.core.node import Node
from node_editor.graphics.node import QDMGraphicsNode
from node_editor.widgets.content_widget import QDMNodeContentWidget

class BaseNode(Node):
    """Base class for all custom nodes."""
    
    # Override these in subclasses
    op_code = 0
    op_title = "Base Node"
    icon = None
    
    # Graphics and content classes (can be overridden)
    GraphicsNode_class = QDMGraphicsNode
    NodeContent_class = QDMNodeContentWidget
    
    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, self.op_title, inputs, outputs)
        self._value = None
        self.markDirty()
    
    @property
    def value(self):
        return self._value
    
    def eval(self):
        """Override in subclass to implement evaluation logic."""
        raise NotImplementedError
    
    def onInputChanged(self, socket=None):
        """Called when an input connection changes."""
        self.markDirty()
        self.eval()
```

### 4.2 Node Registry

```python
# node_editor/nodes/registry.py

class NodeRegistry:
    """Central registry for all node types."""
    
    _nodes = {}
    
    @classmethod
    def register(cls, op_code: int):
        """Decorator to register a node class."""
        def decorator(node_class):
            if op_code in cls._nodes:
                raise ValueError(f"OpCode {op_code} already registered")
            cls._nodes[op_code] = node_class
            node_class.op_code = op_code
            return node_class
        return decorator
    
    @classmethod
    def register_node(cls, op_code: int, node_class):
        """Manually register a node class."""
        if op_code in cls._nodes:
            raise ValueError(f"OpCode {op_code} already registered")
        cls._nodes[op_code] = node_class
        node_class.op_code = op_code
    
    @classmethod
    def get_node_class(cls, op_code: int):
        """Get node class by op_code."""
        return cls._nodes.get(op_code)
    
    @classmethod
    def get_all_nodes(cls) -> dict:
        """Get all registered nodes."""
        return cls._nodes.copy()
    
    @classmethod
    def clear(cls):
        """Clear all registered nodes (useful for testing)."""
        cls._nodes.clear()
```

### 4.3 Built-in Generic Nodes

```python
# node_editor/nodes/math_nodes.py

from node_editor.nodes.base import BaseNode
from node_editor.nodes.registry import NodeRegistry

# Op codes for built-in nodes (100+ reserved for user nodes)
OP_ADD = 1
OP_SUB = 2
OP_MUL = 3
OP_DIV = 4

@NodeRegistry.register(OP_ADD)
class AddNode(BaseNode):
    op_title = "Add"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1])
    
    def eval(self):
        input1 = self.getInputValue(0)
        input2 = self.getInputValue(1)
        
        if input1 is None or input2 is None:
            self.markInvalid()
            return None
        
        self._value = input1 + input2
        self.markDirty(False)
        self.markInvalid(False)
        return self._value
```

---

## 5. Portable Package Design

### 5.1 Package __init__.py

```python
# node_editor/__init__.py

"""
Node Editor - A portable PyQt5 node-based visual programming framework.

Usage:
    from node_editor import NodeEditorWidget, NodeEditorWindow
    from node_editor.nodes import BaseNode, NodeRegistry
    from node_editor.themes import ThemeEngine
"""

__version__ = "1.0.0"

# Core classes
from node_editor.core.node import Node
from node_editor.core.edge import Edge
from node_editor.core.socket import Socket
from node_editor.core.scene import Scene

# Widgets
from node_editor.widgets.editor_widget import NodeEditorWidget
from node_editor.widgets.editor_window import NodeEditorWindow
from node_editor.widgets.content_widget import QDMNodeContentWidget

# Node system
from node_editor.nodes.base import BaseNode
from node_editor.nodes.registry import NodeRegistry

# Theme engine
from node_editor.themes.theme_engine import ThemeEngine

# Graphics (for advanced customization)
from node_editor.graphics import (
    QDMGraphicsView,
    QDMGraphicsScene,
    QDMGraphicsNode,
    QDMGraphicsEdge,
    QDMGraphicsSocket,
)

__all__ = [
    # Core
    'Node', 'Edge', 'Socket', 'Scene',
    # Widgets
    'NodeEditorWidget', 'NodeEditorWindow', 'QDMNodeContentWidget',
    # Nodes
    'BaseNode', 'NodeRegistry',
    # Themes
    'ThemeEngine',
    # Graphics
    'QDMGraphicsView', 'QDMGraphicsScene', 'QDMGraphicsNode',
    'QDMGraphicsEdge', 'QDMGraphicsSocket',
]
```

### 5.2 Usage in External Project (oncutf)

```python
# In oncutf project:

# Just copy node_editor/ folder to oncutf/
# Then:

from node_editor import NodeEditorWidget, BaseNode, NodeRegistry, ThemeEngine

# Set theme
ThemeEngine.set_theme("dark")

# Create custom node
@NodeRegistry.register(100)  # Use op_codes >= 100 for custom nodes
class MyCustomNode(BaseNode):
    op_title = "My Node"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
    
    def eval(self):
        # Custom logic
        pass

# Embed in your window
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.node_editor = NodeEditorWidget(self)
        self.setCentralWidget(self.node_editor)
```

---

## 6. Migration Plan

### Phase 1: Preparation (Non-breaking)
1. Create new directory structure alongside existing code
2. Set up theme engine framework
3. Create base node classes
4. Write migration utilities

### Phase 2: Core Migration
1. Rename `nodeeditor/` to `node_editor/`
2. Reorganize files into new structure (core/, graphics/, widgets/, etc.)
3. Update all internal imports
4. Implement theme engine
5. Migrate graphics classes to use theme engine

### Phase 3: Node System
1. Create node registry
2. Create built-in generic nodes
3. Create base classes for custom nodes
4. Update serialization for new structure

### Phase 4: Examples
1. Migrate calculator to use node_editor as wrapper
2. Create minimal example
3. Update documentation

### Phase 5: Testing & Cleanup
1. Run all tests
2. Remove old files
3. Update README
4. Final testing with copy-paste to oncutf

---

## 7. File Mapping (Old → New)

| Old Location | New Location |
|--------------|--------------|
| `nodeeditor/__init__.py` | `node_editor/__init__.py` |
| `nodeeditor/node_node.py` | `node_editor/core/node.py` |
| `nodeeditor/node_edge.py` | `node_editor/core/edge.py` |
| `nodeeditor/node_socket.py` | `node_editor/core/socket.py` |
| `nodeeditor/node_scene.py` | `node_editor/core/scene.py` |
| `nodeeditor/node_serializable.py` | `node_editor/core/serializable.py` |
| `nodeeditor/node_scene_history.py` | `node_editor/core/history.py` |
| `nodeeditor/node_scene_clipboard.py` | `node_editor/core/clipboard.py` |
| `nodeeditor/node_graphics_view.py` | `node_editor/graphics/view.py` |
| `nodeeditor/node_graphics_scene.py` | `node_editor/graphics/scene.py` |
| `nodeeditor/node_graphics_node.py` | `node_editor/graphics/node.py` |
| `nodeeditor/node_graphics_edge.py` | `node_editor/graphics/edge.py` |
| `nodeeditor/node_graphics_edge_path.py` | `node_editor/graphics/edge_path.py` |
| `nodeeditor/node_graphics_socket.py` | `node_editor/graphics/socket.py` |
| `nodeeditor/node_graphics_cutline.py` | `node_editor/graphics/cutline.py` |
| `nodeeditor/node_editor_widget.py` | `node_editor/widgets/editor_widget.py` |
| `nodeeditor/node_editor_window.py` | `node_editor/widgets/editor_window.py` |
| `nodeeditor/node_content_widget.py` | `node_editor/widgets/content_widget.py` |
| `nodeeditor/node_edge_dragging.py` | `node_editor/edge_tools/dragging.py` |
| `nodeeditor/node_edge_validators.py` | `node_editor/edge_tools/validators.py` |
| `nodeeditor/node_edge_snapping.py` | `node_editor/edge_tools/snapping.py` |
| `nodeeditor/node_edge_rerouting.py` | `node_editor/edge_tools/rerouting.py` |
| `nodeeditor/node_edge_intersect.py` | `node_editor/edge_tools/intersect.py` |
| `nodeeditor/utils.py` | `node_editor/utils/qt_helpers.py` |
| `nodeeditor/utils_no_qt.py` | `node_editor/utils/helpers.py` |
| `nodeeditor/qss/` | `node_editor/themes/dark/style.qss` |
| `examples/example_calculator/` | `examples/calculator/` |
| `examples/example_test/` | `examples/minimal/` |

---

## 8. Estimated Effort

| Phase | Estimated Time | Priority |
|-------|---------------|----------|
| Phase 1: Preparation | 2-3 hours | High |
| Phase 2: Core Migration | 4-6 hours | High |
| Phase 3: Node System | 3-4 hours | High |
| Phase 4: Examples | 2-3 hours | Medium |
| Phase 5: Testing | 2-3 hours | High |
| **Total** | **13-19 hours** | |

---

## 9. Dependencies

### Required (no changes)
- Python 3.8+
- PyQt5 >= 5.15.0

### Removed
- qtpy (removed, direct PyQt5 imports only)

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing calculator example | Medium | Keep old structure until migration complete |
| Import path issues after reorganization | High | Comprehensive import testing |
| Theme engine complexity | Low | Start with simple implementation |
| Serialization compatibility | Medium | Version the JSON format |

---

## 11. Success Criteria

1. ✅ Can copy `node_editor/` folder to oncutf and it works
2. ✅ Theme switching works (dark/light)
3. ✅ Calculator example runs independently
4. ✅ Custom nodes can be created in external projects
5. ✅ All existing functionality preserved
6. ✅ Tests pass

---

## 12. Next Steps

1. **Review this plan** - Confirm approach is correct
2. **Start Phase 1** - Create directory structure
3. **Iterate** - Implement phase by phase with testing

---

*Document created: 2025-12-10*  
*Last updated: 2025-12-10*
