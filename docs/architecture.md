# Node Editor Architecture

This document describes the architectural design, layering rules, data flow, and extension points of the PyQt Node Editor framework.

## Table of Contents

1. [Overview](#overview)
2. [Layer Architecture](#layer-architecture)
3. [Module Structure](#module-structure)
4. [Data Flow](#data-flow)
5. [Theme System](#theme-system)
6. [Node Evaluation](#node-evaluation)
7. [Serialization](#serialization)
8. [Extension Points](#extension-points)
9. [Design Decisions](#design-decisions)

---

## Overview

The node editor follows a **Model-View-Graphics** architecture where:

- **Model Layer** (`core/`): Business logic, node graph structure, serialization
- **Graphics Layer** (`graphics/`): Qt QGraphicsItem subclasses for rendering
- **Widget Layer** (`widgets/`): Qt QWidget containers for embedding

```
┌──────────────────────────────────────────────────────────┐
│                    Application Layer                      │
│              (examples/, main.py, your app)              │
├──────────────────────────────────────────────────────────┤
│                     Widget Layer                          │
│          NodeEditorWidget, NodeEditorWindow              │
├──────────────────────────────────────────────────────────┤
│                    Graphics Layer                         │
│  QDMGraphicsView, QDMGraphicsScene, QDMGraphicsNode...   │
├──────────────────────────────────────────────────────────┤
│                      Core Layer                           │
│            Scene, Node, Edge, Socket, History            │
├──────────────────────────────────────────────────────────┤
│                    Support Layers                         │
│     themes/ (ThemeEngine)  │  tools/  │  utils/          │
└──────────────────────────────────────────────────────────┘
```

---

## Layer Architecture

### Core Layer (`node_editor/core/`)

The foundation layer containing all model classes. **No Qt graphics imports here** (only QPointF for positions).

| Module | Class | Responsibility |
|--------|-------|----------------|
| `node.py` | `Node` | Graph node with sockets, evaluation state |
| `edge.py` | `Edge` | Connection between sockets |
| `socket.py` | `Socket` | Connection point on a node |
| `scene.py` | `Scene` | Container for nodes/edges, save/load |
| `history.py` | `SceneHistory` | Undo/redo stack |
| `clipboard.py` | `SceneClipboard` | Copy/paste operations |
| `serializable.py` | `Serializable` | Base class for persistence |

**Key Design**: Core classes hold references to their graphics counterparts (`node.grNode`, `edge.grEdge`, etc.) but never import graphics modules directly. Graphics classes are injected via `_init_graphics_classes()`.

### Graphics Layer (`node_editor/graphics/`)

Qt QGraphicsItem subclasses for visual rendering. Depends on core layer for model data.

| Module | Class | Responsibility |
|--------|-------|----------------|
| `view.py` | `QDMGraphicsView` | Pan, zoom, mouse handling |
| `scene.py` | `QDMGraphicsScene` | Grid background, selection signals |
| `node.py` | `QDMGraphicsNode` | Node rectangle rendering |
| `edge.py` | `QDMGraphicsEdge` | Connection line rendering |
| `socket.py` | `QDMGraphicsSocket` | Socket circle rendering |
| `edge_path.py` | `GraphicsEdgePath*` | Path calculation strategies |
| `cutline.py` | `QDMGraphicsCutLine` | Edge cutting interaction |

**Theme Integration**: All graphics classes access colors via `ThemeEngine.current_theme()` in their `initAssets()` method.

### Widget Layer (`node_editor/widgets/`)

High-level Qt widgets for application integration.

| Module | Class | Responsibility |
|--------|-------|----------------|
| `editor_widget.py` | `NodeEditorWidget` | Embeddable canvas (Scene + View) |
| `editor_window.py` | `NodeEditorWindow` | Full window with menus/toolbar |
| `content_widget.py` | `QDMNodeContentWidget` | Base for node content areas |

### Node Layer (`node_editor/nodes/`)

Built-in node implementations and registration system.

| Module | Classes | Op Codes |
|--------|---------|----------|
| `registry.py` | `NodeRegistry` | - |
| `input_node.py` | `NumberInputNode`, `TextInputNode` | 1-2 |
| `output_node.py` | `OutputNode` | 3 |
| `math_nodes.py` | `AddNode`, `SubtractNode`, ... | 10-13, 50-56 |
| `logic_nodes.py` | `EqualNode`, `AndNode`, ... | 20-30, 60-63 |
| `string_nodes.py` | `ConcatenateNode`, ... | 40-44 |
| `conversion_nodes.py` | `ToStringNode`, ... | 70-73 |
| `utility_nodes.py` | `ConstantNode`, ... | 80-84 |
| `list_nodes.py` | `CreateListNode`, ... | 90-94 |
| `time_nodes.py` | `CurrentTimeNode`, ... | 100-104 |
| `advanced_nodes.py` | `RegexMatchNode`, ... | 110-113 |

### Theme Layer (`node_editor/themes/`)

Centralized appearance management.

| Module | Class | Responsibility |
|--------|-------|----------------|
| `theme_engine.py` | `ThemeEngine` | Registration, switching, QSS loading |
| `base_theme.py` | `BaseTheme` | Property definitions |
| `dark/__init__.py` | `DarkTheme` | Dark color scheme |
| `light/__init__.py` | `LightTheme` | Light color scheme |

### Tools Layer (`node_editor/tools/`)

Interactive behaviors for edge manipulation.

| Module | Class | Responsibility |
|--------|-------|----------------|
| `edge_dragging.py` | `EdgeDragging` | Create edges by dragging |
| `edge_rerouting.py` | `EdgeRerouting` | Reconnect existing edges |
| `edge_snapping.py` | `EdgeSnapping` | Snap to nearby sockets |
| `edge_intersect.py` | `EdgeIntersect` | Insert nodes into edges |
| `edge_validators.py` | Various functions | Connection rule enforcement |

---

## Module Structure

### Import Hierarchy

```
                    ┌─────────────┐
                    │   __init__  │ (Public API)
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐       ┌──────────┐       ┌──────────┐
   │ widgets │       │  nodes   │       │  themes  │
   └────┬────┘       └────┬─────┘       └────┬─────┘
        │                 │                  │
        ▼                 ▼                  │
   ┌─────────┐       ┌─────────┐            │
   │graphics │       │  core   │◄───────────┘
   └────┬────┘       └────┬────┘
        │                 │
        └────────┬────────┘
                 ▼
            ┌─────────┐
            │  utils  │
            └─────────┘
```

### Circular Import Prevention

The core layer needs graphics classes but importing them directly would create cycles. Solution:

```python
# core/__init__.py
def _init_graphics_classes():
    """Initialize graphics class references."""
    from node_editor.graphics.node import QDMGraphicsNode
    # ... other imports
    
    Node.GraphicsNode_class = QDMGraphicsNode
    # ... other assignments
```

Called once from package `__init__.py` before any widgets are created.

---

## Data Flow

### Scene → Nodes → Evaluation → Graphics

```
User edits graph
        │
        ▼
┌───────────────────┐
│  Scene.addNode()  │
│  Scene.addEdge()  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Node.onInputChanged() │──► markDirty()
└────────┬──────────┘      markDescendantsDirty()
         │
         ▼
┌───────────────────┐
│    Node.eval()    │──► Get inputs via getInput()
└────────┬──────────┘    Compute result
         │               Store in self.value
         ▼
┌───────────────────┐
│ markInvalid(False)│──► grNode.update()
│ markDirty(False)  │    Triggers paint()
└───────────────────┘
```

### Dirty/Invalid State Propagation

```python
# When input changes:
def onInputChanged(self, socket):
    self.markDirty()           # This node needs re-eval
    self.markDescendantsDirty() # Children need re-eval too
    
# After successful evaluation:
def eval(self):
    # ... compute ...
    self.markDirty(False)      # No longer dirty
    self.markInvalid(False)    # Valid result
    
# After failed evaluation:
def eval(self):
    self.markInvalid(True)     # Show error state
    self.grNode.setToolTip("Error message")
```

---

## Theme System

### Theme Propagation

```
┌─────────────────────────────────────────────────────────┐
│                    ThemeEngine                          │
│  _current_theme: BaseTheme                             │
│  _themes: dict[str, type[BaseTheme]]                   │
└────────────────────┬────────────────────────────────────┘
                     │
         ThemeEngine.current_theme()
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌─────────┐   ┌───────────┐   ┌───────────┐
│QDMGrNode│   │QDMGrEdge │   │QDMGrScene │
│initAssets│  │initAssets│   │initAssets │
└─────────┘   └───────────┘   └───────────┘
```

### Theme Properties Used

| Component | Properties Accessed |
|-----------|---------------------|
| `QDMGraphicsScene` | `scene_background`, `scene_grid_light`, `scene_grid_dark` |
| `QDMGraphicsNode` | `node_background`, `node_title_*`, `node_border_*` |
| `QDMGraphicsEdge` | `edge_color_*`, `edge_width*` |
| `QDMGraphicsSocket` | `socket_colors[]`, `socket_radius` |

### Changing Themes at Runtime

```python
ThemeEngine.set_theme("light")
# This:
# 1. Instantiates theme class
# 2. Loads QSS file from themes/light/style.qss
# 3. Applies QSS to QApplication
# Note: Graphics items cache colors at init - they won't update automatically
```

For full runtime theme switching, graphics items would need to re-call `initAssets()`.

---

## Serialization

### Format Overview

The framework uses JSON for persistence. All serializable classes inherit from `Serializable` base.

```
Scene
  ├─ id: int (Python object id)
  ├─ scene_width: int
  ├─ scene_height: int
  ├─ nodes: list[NodeData]
  │    ├─ id: int
  │    ├─ title: str
  │    ├─ pos_x, pos_y: float
  │    ├─ inputs: list[SocketData]
  │    ├─ outputs: list[SocketData]
  │    └─ content: dict
  └─ edges: list[EdgeData]
       ├─ id: int
       ├─ edge_type: int
       ├─ start: int (socket id)
       └─ end: int (socket id)
```

### Hashmap for References

During deserialization, a hashmap maps old IDs to new objects:

```python
hashmap = {}
for node_data in data["nodes"]:
    node = NodeClass(scene, ...)
    hashmap[node_data["id"]] = node  # Old ID → new object
    
for edge_data in data["edges"]:
    start_socket = hashmap[edge_data["start"]]  # Resolve reference
    # ...
```

### Custom Node Serialization

Nodes with state (e.g., ConstantNode's value) override serialize/deserialize:

```python
class ConstantNode(Node):
    def serialize(self):
        data = super().serialize()
        data["constant_value"] = self.constant_value
        return data
    
    def deserialize(self, data, hashmap=None, restore_id=True):
        super().deserialize(data, hashmap, restore_id)
        self.constant_value = data.get("constant_value", "")
        return True
```

### Versioning Strategy

Currently no explicit version field. Recommended addition:

```json
{
    "version": "1.0",
    "id": 12345,
    ...
}
```

Handle migration:
```python
def deserialize(self, data, hashmap=None, restore_id=True):
    version = data.get("version", "0.9")  # Legacy default
    if version < "1.0":
        data = self._migrate_0_9_to_1_0(data)
    # ...
```

---

## Extension Points

### 1. Custom Node Types

```python
from node_editor.core.node import Node
from node_editor.nodes import NodeRegistry

@NodeRegistry.register(150)
class CustomNode(Node):
    def __init__(self, scene):
        super().__init__(scene, "Custom", inputs=[1], outputs=[1])
    
    def eval(self):
        # Your logic
        pass
```

### 2. Custom Graphics

```python
from node_editor.graphics.node import QDMGraphicsNode

class MyGraphicsNode(QDMGraphicsNode):
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        # Custom drawing
        
class MyNode(Node):
    GraphicsNode_class = MyGraphicsNode  # Use custom graphics
```

### 3. Custom Themes

```python
from node_editor.themes import BaseTheme, ThemeEngine

class CyberpunkTheme(BaseTheme):
    name = "cyberpunk"
    scene_background = QColor("#0d0221")
    # ...

ThemeEngine.register_theme(CyberpunkTheme)
```

### 4. Edge Validators

```python
from node_editor.core.edge import Edge

def my_validator(input_socket, output_socket) -> bool:
    """Prevent connections between certain socket types."""
    if input_socket.socket_type == 5:  # Type 5 can only connect to type 5
        return output_socket.socket_type == 5
    return True

Edge.registerEdgeValidator(my_validator)
```

### 5. Node Class Selection (Polymorphic Deserialization)

```python
def select_node_class(data: dict) -> type:
    """Return correct Node subclass based on saved data."""
    op_code = data.get("op_code", 0)
    return NodeRegistry.get_node_class(op_code) or Node

scene.setNodeClassSelector(select_node_class)
```

---

## Design Decisions

### Why Separate Core and Graphics?

1. **Testability**: Core logic can be tested without Qt
2. **Headless operation**: Batch processing without GUI
3. **Portability**: Core could theoretically support other GUI toolkits

### Why Class-Level Graphics Factory?

```python
class Node:
    GraphicsNode_class = QDMGraphicsNode  # Class attribute
```

Allows subclasses to override without modifying Node code. Set once via `_init_graphics_classes()`.

### Why Op Codes?

Operation codes provide:
- Stable identifiers for serialization (class names can change)
- Fast lookup in registry
- Clear namespace separation (1-99 built-in, 100+ custom)

---

## File Dependency Graph

```
node_editor/__init__.py
├── core/__init__.py
│   ├── serializable.py
│   ├── socket.py ← serializable
│   ├── node.py ← socket, serializable
│   ├── edge.py ← socket, serializable
│   ├── scene.py ← node, edge, serializable
│   ├── history.py ← scene
│   └── clipboard.py ← scene
├── graphics/__init__.py
│   ├── socket.py ← themes
│   ├── node.py ← themes
│   ├── edge.py ← themes, edge_path
│   ├── edge_path.py
│   ├── scene.py ← themes
│   ├── view.py ← scene, tools
│   └── cutline.py
├── widgets/__init__.py
│   ├── content_widget.py
│   ├── editor_widget.py ← core.scene, graphics.view
│   └── editor_window.py ← editor_widget
├── nodes/__init__.py
│   ├── registry.py
│   └── *_nodes.py ← core.node, registry
├── themes/__init__.py
│   ├── base_theme.py
│   ├── theme_engine.py ← base_theme
│   ├── dark/__init__.py ← base_theme
│   └── light/__init__.py ← base_theme
├── tools/__init__.py
│   ├── edge_dragging.py ← core.edge
│   ├── edge_rerouting.py ← core.edge
│   ├── edge_snapping.py
│   ├── edge_intersect.py
│   └── edge_validators.py
└── utils/__init__.py
    ├── helpers.py
    ├── qt_helpers.py
    └── logging_config.py
```

---

*Document created: 2025-12-12*  
*Last updated: 2025-12-12*

---

## Proposed Improvements and Renaming

- Clarify graphics naming: consider `graphics_node` / `graphics_edge` / `graphics_socket` instead of `grNode` / `grEdge` / `grSocket` for snake_case consistency (breaking change; migration guide required).
- Align method names with PEP8: `markDirty` / `markInvalid` → `mark_dirty` / `mark_invalid` in `core/node.py` (breaking change; requires deprecation shim).
- Document the `_init_graphics_classes()` bootstrap as the intentional core→graphics bridge to make coupling explicit.
- Confirm that `tools/` is the sole location for edge tools; removed `edge_tools/` and `nodes/base.py` to keep the public surface minimal.
