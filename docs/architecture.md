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

- **Core Layer** (`core/`): Qt-free business logic, node graph structure, serialization
- **Graphics Layer** (`graphics/`): Qt QGraphicsItem subclasses for rendering
- **Widget Layer** (`widgets/`): Qt QWidget containers for embedding
- **Support Layers** (`themes/`, `tools/`, `utils/`): Theming, interaction, helpers

### Design Principles

- **Core Independence**: No runtime Qt dependencies in `core/` - only domain logic
- **Stable Identifiers**: ULID-based stable IDs (`sid`) for reliable persistence
- **IO-Free Snapshots**: Serialization independent of file I/O operations
- **Clean Separation**: Graphics layer manages visual state, core layer manages model state

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
│           Core Layer (Qt-Free Runtime)                    │
│   Scene, Node, Edge, Socket, History, Clipboard         │
├──────────────────────────────────────────────────────────┤
│      Support Layers (themes, tools, utils)              │
│    ThemeEngine, EdgeDragging, Helpers                   │
└──────────────────────────────────────────────────────────┘
```

**Core Layer Constraint**: No PyQt/PySide imports at runtime - only TYPE_CHECKING for type hints.

---

## Layer Architecture

### Core Layer (`node_editor/core/`)

The foundation layer containing all model classes. **Qt-free at runtime** - only TYPE_CHECKING imports for type hints.

| Module | Class | Responsibility |
|--------|-------|----------------|
| `node.py` | `Node` | Graph node with sockets, evaluation state, stable ID (sid) |
| `edge.py` | `Edge` | Connection between sockets with stable ID |
| `socket.py` | `Socket` | Connection point on a node |
| `scene.py` | `Scene` | Container for nodes/edges, domain-level selection APIs |
| `history.py` | `SceneHistory` | Undo/redo stack |
| `clipboard.py` | `SceneClipboard` | Copy/paste operations |
| `serializable.py` | `Serializable` | Base class for persistence |
| `host_bridge.py` | `NodeHostBridge` | Host application integration interface |

**Key Design**: Core classes hold references to their graphics counterparts (`node.graphics_node`, `edge.graphics_edge`, etc.) but never import graphics modules directly. Graphics classes are injected via `_init_graphics_classes()`. All model objects use stable ULID identifiers (`sid`) for persistent identification across sessions.

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

## Stable Identifiers (ULID)

### Why Stable IDs?

Python object `id()` values change between sessions, breaking deserialization. Solution: ULID-based stable IDs.

### ULID Properties

- **Sortable**: Ordered by timestamp (first 48 bits)
- **Unique**: Contains 80 bits of entropy
- **URL-safe**: Base32 encoding (Crockford)
- **Readable**: 26 characters, no confusion (no I/L/O/U)

### Implementation

Every `Node`, `Edge`, and `Socket` has a `sid` (stable ID):

```python
node = Node(scene, "MyNode")
print(node.sid)  # e.g., "01BX5ZZKBK6S0URNNZZ0BCZ7X0"

# Persists across saves and loads
data = scene.serialize()
scene2 = Scene()
scene2.deserialize(data)
print(scene2.nodes[0].sid)  # Same as original
```

### Serialization

```json
{
    "nodes": [
        {
            "sid": "01BX5ZZKBK6S0URNNZZ0BCZ7X0",
            "title": "Add",
            ...
        }
    ]
}
```

---

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
    
    Node._graphics_node_class = QDMGraphicsNode
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
│ Node.on_input_changed() │──► mark_dirty()
└────────┬──────────┘         mark_descendants_dirty()
         │
         ▼
┌───────────────────┐
│    Node.eval()    │──► Get inputs via get_input()
└────────┬──────────┘    Compute result
         │               Store in self.value
         ▼
┌───────────────────┐
│ mark_invalid(False)│──► graphics_node.update()
│ mark_dirty(False)  │    Triggers paint()
└───────────────────┘
```

### Dirty/Invalid State Propagation

```python
# When input changes:
def on_input_changed(self, socket):
    self.mark_dirty()             # This node needs re-eval
    self.mark_descendants_dirty() # Children need re-eval too

# After successful evaluation:
def eval(self):
    # ... compute ...
    self.mark_dirty(False)        # No longer dirty
    self.mark_invalid(False)      # Valid result

# After failed evaluation:
def eval(self):
    self.mark_invalid(True)       # Show error state
    self.graphics_node.setToolTip("Error message")
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
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│QDMGraphicsNode │   │QDMGraphicsEdge │   │QDMGraphicsScene│
│init_assets     │   │init_assets     │   │init_assets     │
└────────────────┘   └────────────────┘   └────────────────┘
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
from node_editor.themes.theme_engine import ThemeEngine

# Change the theme
ThemeEngine.set_theme("light")

# Refresh existing graphics items to apply new colors
ThemeEngine.refresh_graphics_items(scene)
```

**Process**:
1. `set_theme()` instantiates the new theme class
2. Loads QSS file from `themes/{theme_name}/style.qss`
3. Applies QSS to QApplication (affects widgets)
4. `refresh_graphics_items()` calls `initAssets()` on all nodes/edges/sockets

**Note**: Graphics items cache theme colors at initialization. Without calling `refresh_graphics_items()`, existing items retain the previous theme's colors.

---

## Serialization

### Snapshot Format v2

Scene data is converted to/from snapshots (IO-free format):

```python
# Serialization
snapshot = scene.to_snapshot()  # Dict[str, Any], ready for JSON
json_str = json.dumps(snapshot)

# Deserialization  
snapshot = json.loads(json_str)
scene.from_snapshot(snapshot)  # Restores state from snapshot
```

### Format Overview

The framework uses JSON for persistence. All serializable classes inherit from `Serializable` base.

```
Snapshot
  ├─ version: str (format version, e.g. "2.0.0")
  ├─ id: str (ULID for scene)
  ├─ scene_width: int
  ├─ scene_height: int
  ├─ nodes: list[NodeSnapshot]
  │    ├─ sid: str (ULID)
  │    ├─ title: str
  │    ├─ pos_x, pos_y: float
  │    ├─ inputs: list[SocketSnapshot]
  │    ├─ outputs: list[SocketSnapshot]
  │    └─ content: dict
  └─ edges: list[EdgeSnapshot]
       ├─ sid: str (ULID)
       ├─ edge_type: int
       ├─ start_sid: str (socket ULID)
       └─ end_sid: str (socket ULID)
```
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

**Required fields**: Each socket entry must include `multi_edges`.

### ID Resolution During Deserialization

Snapshot references use stable IDs (ULID), not Python object IDs:

```python
sid_map = {}  # sid (string) → object
for node_data in snapshot["nodes"]:
    node = NodeClass(scene, ...)
    sid_map[node_data["sid"]] = node  # ULID → object
    
for edge_data in snapshot["edges"]:
    start_socket = sid_map[edge_data["start_sid"]]  # Resolve ULID
    # ...
```

**Benefits**:
- Stable across sessions
- Human-readable for debugging
- Sortable (useful for diffs)

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

Snapshot format includes version field for identification:

```json
{
    "version": "2.0.0",
    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    ...
}
```

**Implementation** (in `Scene.to_snapshot/from_snapshot`):

```python
def to_snapshot(self) -> dict:
    return {
        "version": "2.0.0",  # Current format version
        "id": self.sid,      # Scene's stable ID
        # ... nodes, edges ...
    }

def from_snapshot(self, snapshot: dict) -> bool:
    version = snapshot.get("version", "1.0.0")
    # Migrate if needed
    if version != "2.0.0":
        snapshot = self._migrate_snapshot(snapshot, version)
    # ... restore nodes/edges ...
```

**Guidelines**:
- Bump version when changing snapshot schema (add/remove/rename fields)
- Use semantic versioning: major.minor.patch
- v2.0.0: Introduced ULID (sid) replacing Python object IDs

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
    _graphics_node_class = MyGraphicsNode  # Use custom graphics
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

scene.set_node_class_selector(select_node_class)
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
    _graphics_node_class = QDMGraphicsNode  # Class attribute
```

Allows subclasses to override without modifying Node code. Set once via `_init_graphics_classes()`.

### Why Op Codes?

Operation codes provide:
- Stable identifiers for serialization (class names can change)
- Fast lookup in registry
- Clear namespace separation (1-113 built-in, 200+ custom)

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
*Last updated: 2025-12-15*
