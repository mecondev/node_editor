
# Node Editor - Technical Audit Report

**Version:** 1.0.0  
**Audit Date:** 2025-01-27  
**Auditor:** Claude 4.5 Opus (Senior Python & Qt Architect)  
**Target Python Version:** 3.11+  
**Backward Compatibility Required:** No

---

## Executive Summary

The node_editor is a well-organized PyQt5 framework for visual node editors. The Model-View-Graphics architecture is correctly implemented with clean separation of concerns. 23 potential improvements were identified across 4 categories: architecture (7), performance (4), code/naming (8), and documentation (4). The most significant changes address modernizing type hints with contemporary Python syntax, removing `OrderedDict` in favor of plain `dict`, and improving the evaluation system for large graphs. No critical vulnerabilities were identified. Incremental refactoring starting from the core layer is recommended.

---

## 1. Architecture Findings

### 1.1 Layer Structure ✅ Well-Designed

| Layer | Path | Responsibility | Status |
|-------|------|----------------|--------|
| core | `node_editor/core/` | Model classes (Node, Edge, Socket, Scene) | ✅ Solid |
| graphics | `node_editor/graphics/` | Qt graphics items (QDMGraphics*) | ✅ Clean |
| widgets | `node_editor/widgets/` | High-level Qt widgets | ✅ Good |
| nodes | `node_editor/nodes/` | Built-in node implementations | ✅ Extensible |
| themes | `node_editor/themes/` | Visual theming system | ✅ Flexible |
| tools | `node_editor/tools/` | Interactive tools (dragging, snapping) | ✅ Modular |
| utils | `node_editor/utils/` | Helpers, logging | ⚠️ Minimal |

### 1.2 Graphics Class Injection Mechanism

**File:** [node_editor/core/__init__.py](../node_editor/core/__init__.py#L36-L45)

```python
def _init_graphics_classes():
    """Initialize graphics class references."""
    from node_editor.graphics.edge import QDMGraphicsEdge
    from node_editor.graphics.node import QDMGraphicsNode
    from node_editor.graphics.socket import QDMGraphicsSocket
    from node_editor.widgets.content_widget import QDMNodeContentWidget

    Socket.Socket_Graphics_Class = QDMGraphicsSocket
    Node._graphics_node_class = QDMGraphicsNode
    Node.NodeContent_class = QDMNodeContentWidget
    Edge._graphics_edge_class = QDMGraphicsEdge
```

**Assessment:** The mechanism avoids circular imports effectively. However, the class attributes `Socket_Graphics_Class`, `_graphics_node_class`, `NodeContent_class`, `_graphics_edge_class` have inconsistent naming convention.

**Proposal A1 - Consistent naming for injected graphics classes:**

| Current | Proposed |
|---------|----------|
| `Socket.Socket_Graphics_Class` | `Socket._graphics_socket_class` |
| `Node._graphics_node_class` | ✅ Already correct |
| `Node.NodeContent_class` | `Node._content_widget_class` |
| `Edge._graphics_edge_class` | ✅ Already correct |

### 1.3 Serialization System - OrderedDict Legacy

**Files:** 
- [node_editor/core/serializable.py](../node_editor/core/serializable.py)
- [node_editor/core/node.py](../node_editor/core/node.py#L590-L650)
- [node_editor/core/edge.py](../node_editor/core/edge.py#L280-L320)

**Finding:** `OrderedDict` is used everywhere for serialization, but since Python 3.7+ the standard `dict` preserves insertion order.

**Proposal A2 - Replace OrderedDict with dict:**

```python
# Before (all serializable classes)
from collections import OrderedDict

def serialize(self) -> OrderedDict:
    return OrderedDict([("id", self.id), ("pos", self.pos)])

# After
def serialize(self) -> dict:
    return {"id": self.id, "pos": self.pos}
```

**Impact:** ~25 files, reduces imports and verbosity.

### 1.4 View State Machine Complexity

**File:** [node_editor/graphics/view.py](../node_editor/graphics/view.py)

**Finding:** The `QDMGraphicsView` manages 5 modes with inline state logic in mouse events (~650 lines). This creates tight coupling between interaction modes.

**Proposal A3 - Extract state handlers to protocol classes:**

```python
# Proposed: node_editor/tools/view_states.py
from typing import Protocol

class ViewState(Protocol):
    """Protocol for view interaction states."""
    
    def on_mouse_press(self, view: QDMGraphicsView, event: QMouseEvent) -> bool: ...
    def on_mouse_move(self, view: QDMGraphicsView, event: QMouseEvent) -> None: ...
    def on_mouse_release(self, view: QDMGraphicsView, event: QMouseEvent) -> None: ...
    def enter(self, view: QDMGraphicsView) -> None: ...
    def exit(self, view: QDMGraphicsView) -> None: ...

class NoopState:
    """Default idle state."""
    ...

class EdgeDragState:
    """State during edge creation drag."""
    ...
```

**Priority:** Medium - Improves testability and extensibility.

### 1.5 Scene-Node-Edge Coupling

**Files:** [node_editor/core/scene.py](../node_editor/core/scene.py), [node_editor/core/node.py](../node_editor/core/node.py)

**Finding:** Nodes and Edges are added to the scene via their constructors (`self.scene.add_node(self)`), not through Scene factory methods. This makes creating nodes/edges impossible without a scene.

**Proposal A4 - Factory methods in Scene:**

```python
# Scene class enhancement
class Scene:
    def create_node(self, node_class: type[Node], title: str, **kwargs) -> Node:
        """Factory method for creating and registering nodes."""
        node = node_class(self, title, **kwargs)
        return node
    
    def create_edge(self, start_socket: Socket, end_socket: Socket, **kwargs) -> Edge:
        """Factory method for creating and registering edges."""
        return self.get_edge_class()(self, start_socket, end_socket, **kwargs)
```

**Priority:** Low - Current pattern works, factory is optional enhancement.

### 1.6 Node Class Selector Pattern

**File:** [node_editor/core/scene.py](../node_editor/core/scene.py#L180-L220)

```python
def get_node_class_from_data(self, data: dict) -> type[Node]:
    """Resolve node class from serialized data."""
    return self._node_class_selector(data)
```

**Assessment:** ✅ Good design - allows custom node resolution without monkey-patching.

### 1.7 Edge Validator Registry

**File:** [node_editor/core/edge.py](../node_editor/core/edge.py#L50-L90)

```python
class Edge(Serializable):
    edge_validators: list[Callable] = []
    
    @classmethod
    def register_edge_validator(cls, validator_callback: Callable) -> None:
        cls.edge_validators.append(validator_callback)
```

**Finding:** Class-level list is mutable and shared across all Edge subclasses.

**Proposal A5 - Per-class validator isolation:**

```python
class Edge(Serializable):
    edge_validators: ClassVar[list[Callable]] = []
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Create isolated validator list for subclass
        cls.edge_validators = cls.edge_validators.copy()
```

---

## 2. Performance & Threading Analysis

### 2.1 Evaluation Cascade - Potential Bottleneck

**File:** [node_editor/core/node.py](../node_editor/core/node.py#L350-L420)

```python
def mark_descendants_dirty(self, new_value: bool = True) -> None:
    """Mark all downstream nodes as needing re-evaluation."""
    for child_node in self.get_children_nodes():
        child_node.mark_dirty(new_value)
        child_node.mark_descendants_dirty(new_value)
```

**Finding:** Recursive DFS without cycle detection. In graphs with cycles or very deep nesting can cause:
- Stack overflow (recursive calls)
- Repeated visits in shared descendants
- Exponential complexity in diamond patterns

**Proposal P1 - Iterative traversal with visited set:**

```python
def mark_descendants_dirty(self, new_value: bool = True) -> None:
    """Mark all downstream nodes as needing re-evaluation."""
    visited: set[int] = set()
    queue: deque[Node] = deque(self.get_children_nodes())
    
    while queue:
        node = queue.popleft()
        if node.id in visited:
            continue
        visited.add(node.id)
        node.mark_dirty(new_value)
        queue.extend(node.get_children_nodes())
```

**Impact:** O(n) instead of potentially O(2^n) for diamond graphs.

### 2.2 Edge Update on Node Move

**File:** [node_editor/graphics/node.py](../node_editor/graphics/node.py#L160-L180)

```python
def mouseMoveEvent(self, event) -> None:
    super().mouseMoveEvent(event)
    for node in list(scene.scene.nodes):
        if node.graphics_node and node.graphics_node.isSelected():
            node.update_connected_edges()
    self._was_moved = True
```

**Finding:** During drag of multiple nodes, each mouse move event updates edges for all selected nodes. With 100 selected nodes × 4 edges/node × 60 FPS = 24,000 edge updates/second.

**Proposal P2 - Batch edge updates:**

```python
def mouseMoveEvent(self, event) -> None:
    super().mouseMoveEvent(event)
    if not self._was_moved:
        # First move triggers batch update scheduling
        QTimer.singleShot(0, self._batch_update_edges)
    self._was_moved = True

def _batch_update_edges(self) -> None:
    """Update edges for all selected nodes once per frame."""
    scene = self.scene()
    if scene and hasattr(scene, 'scene'):
        for node in scene.scene.nodes:
            if node.graphics_node and node.graphics_node.isSelected():
                node.update_connected_edges()
```

### 2.3 History Snapshot Size

**File:** [node_editor/core/history.py](../node_editor/core/history.py#L170-L200)

**Finding:** Each history stamp saves the entire serialized scene (nodes, edges, sockets). With 1000 nodes × 32 history steps = significant memory usage.

**Proposal P3 - Incremental/delta snapshots (future consideration):**

```python
# Future enhancement - not critical for current scale
class DeltaHistory:
    """Store only changed objects between snapshots."""
    ...
```

**Priority:** Low - Current approach works for typical use cases (<500 nodes).

### 2.4 Thread Safety

**Finding:** All operations run on the main Qt thread. There are no background workers for evaluation. This is correct for Qt GUI but can cause freeze with computationally heavy nodes.

**Recommendation:** Document this limitation. For CPU-heavy evaluations, users should implement async patterns in their custom nodes.

---

## 3. Code Quality & Refactoring Proposals

### 3.1 Type Hints Modernization

**Scope:** All files under `node_editor/`

**Finding:** Python 3.8 compatible syntax is used (`List[str]`, `Optional[X]`). With target Python 3.11+ we can use modern syntax.

**Proposal C1 - Modern type syntax:**

| Before | After |
|--------|-------|
| `Optional[X]` | `X \| None` |
| `List[str]` | `list[str]` |
| `Dict[str, int]` | `dict[str, int]` |
| `Tuple[int, int]` | `tuple[int, int]` |
| `Union[A, B]` | `A \| B` |

**Example transformation:**

```python
# Before (node_editor/core/node.py)
from typing import TYPE_CHECKING, Optional, List

def get_input(self, index: int = 0) -> Optional["Node"]:
    ...

def get_children_nodes(self) -> List["Node"]:
    ...

# After
from typing import TYPE_CHECKING

def get_input(self, index: int = 0) -> "Node | None":
    ...

def get_children_nodes(self) -> list["Node"]:
    ...
```

**Files affected:** ~30 files with type hints.

### 3.2 Enum Usage for Constants

**Files:**
- [node_editor/core/socket.py](../node_editor/core/socket.py#L25-L35) - Position constants
- [node_editor/core/edge.py](../node_editor/core/edge.py#L25-L35) - Edge type constants

```python
# Current
LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2
```

**Proposal C2 - Use IntEnum for type safety:**

```python
from enum import IntEnum, auto

class SocketPosition(IntEnum):
    LEFT_TOP = 1
    LEFT_CENTER = 2
    LEFT_BOTTOM = 3
    RIGHT_TOP = 4
    RIGHT_CENTER = 5
    RIGHT_BOTTOM = 6

class EdgeType(IntEnum):
    DIRECT = 1
    BEZIER = 2
    SQUARE = 3
    IMPROVED_SHARP = 4
    IMPROVED_BEZIER = 5

# Backward compatible via IntEnum subclassing
```

### 3.3 Property vs Method Consistency

**File:** [node_editor/core/node.py](../node_editor/core/node.py)

**Finding:** Inconsistent use of properties vs methods:

| Name | Current | Suggested |
|------|---------|-----------|
| `node.pos` | Property | ✅ Keep |
| `node.get_socket_position()` | Method | ✅ Keep (has side effects) |
| `node.title` | Property | ✅ Keep |
| `socket.is_input` | Property | ✅ Keep |
| `socket.is_output` | Property | ✅ Keep |
| `scene.get_view()` | Method | Could be `view` property |

**Proposal C3 - Add `view` property to Scene:**

```python
@property
def view(self) -> QDMGraphicsView | None:
    """Get the graphics view displaying this scene."""
    return self.get_view()
```

### 3.4 Magic Numbers

**File:** [node_editor/graphics/edge_path.py](../node_editor/graphics/edge_path.py#L30-L40)

```python
EDGE_CP_ROUNDNESS = 100
WEIGHT_SOURCE = 0.2
EDGE_IBCP_ROUNDNESS = 75
NODE_DISTANCE = 12
EDGE_CURVATURE = 2
```

**Assessment:** ✅ Already extracted as named constants. Consider moving to theme for customization.

### 3.5 Exception Handling Specificity

**File:** [node_editor/graphics/node.py](../node_editor/graphics/node.py#L170-L175)

```python
except (RuntimeError, AttributeError):
    # Ignore errors from deleted Qt objects
    pass
```

**Finding:** Silent exception swallowing. Appropriate for Qt cleanup but better to have logging at DEBUG level.

**Proposal C4 - Add debug logging for silenced exceptions:**

```python
except (RuntimeError, AttributeError) as e:
    logger.debug("Ignoring Qt cleanup error: %s", e)
```

### 3.6 Dataclass Candidates

**Finding:** Some simple data containers could be dataclasses:

**Proposal C5 - Convert simple containers to dataclasses:**

```python
# node_editor/core/history.py - History stamp
@dataclass
class HistoryStamp:
    """Single snapshot in the undo/redo stack."""
    description: str
    snapshot: dict
    selection: list[int]
```

### 3.7 String Formatting Consistency

**Scope:** Multiple files

**Finding:** Mix of f-strings and `.format()`. f-strings are more readable and faster.

**Proposal C6 - Use f-strings everywhere:**

```python
# Before
"Error: {}".format(str(e))

# After  
f"Error: {e}"
```

### 3.8 Method Ordering Convention

**Recommendation C7:** Follow consistent method ordering in classes:

1. `__init__` and other dunderes
2. Class methods / Static methods
3. Properties
4. Public methods (alphabetical or logical grouping)
5. Protected methods (`_method`)
6. Private methods (`__method`)

---

## 4. Naming & API Cleanup

### 4.1 Inconsistent Attribute Naming

| Location | Current | Proposed |
|----------|---------|----------|
| `Socket` | `Socket_Graphics_Class` | `_graphics_socket_class` |
| `Node` | `NodeContent_class` | `_content_widget_class` |
| `QDMGraphicsEdge` | `pathCalculator` | `path_calculator` |
| `QDMGraphicsEdge` | `posSource` | `pos_source` |
| `QDMGraphicsEdge` | `posDestination` | `pos_destination` |
| `EdgeDragging` | `drag_start_socket` | ✅ Already snake_case |
| `SceneHistory` | `history_current_step` | ✅ Already snake_case |

**Proposal N1 - Rename to snake_case:**

```python
# node_editor/graphics/edge.py
class QDMGraphicsEdge:
    def __init__(self, ...):
        self.path_calculator = self.determine_edge_path_class()(self)
        self.pos_source = [0, 0]
        self.pos_destination = [200, 100]
```

### 4.2 Boolean Parameter Naming

**File:** [node_editor/core/edge.py](../node_editor/core/edge.py#L250-L270)

```python
def remove(self, silent: bool = False) -> None:
```

**Recommendation N2:** For boolean params, use descriptive names:

```python
def remove(self, *, notify_sockets: bool = True) -> None:
```

(Inverted logic makes positive case explicit)

### 4.3 Method Name Clarity

| Current | Suggested | Reason |
|---------|-----------|--------|
| `do_select()` | `select()` | "do_" prefix unnecessary |
| `do_deselect_items()` | `deselect_all()` | Clearer intent |
| `getSnappedSocketItem()` | `get_snapped_socket()` | snake_case |
| `getSnappedToSocketPosition()` | `get_snap_position()` | Shorter, clearer |

### 4.4 Unused Parameters

**Files:** Multiple

**Finding:** Some methods have unused parameters (correctly prefixed with `_`):

```python
def paint(self, painter, _option, _widget=None) -> None:
```

**Assessment:** ✅ Already following convention with `_` prefix.

---

## 5. Documentation & Logging

### 5.1 Missing Module Docstrings

**Status:** ✅ All modules have docstrings with Author and Date.

### 5.2 Logger Usage

**Files:** Only `edge_rerouting.py` imports logger:

```python
# node_editor/tools/edge_rerouting.py
logger = logging.getLogger(__name__)
```

**Proposal D1 - Add logging to all modules:**

```python
# Add to each module that performs significant operations
import logging

logger = logging.getLogger(__name__)
```

**Key places to add logging:**
- `core/scene.py` - File operations, node/edge add/remove
- `core/history.py` - Undo/redo operations
- `widgets/editor_widget.py` - File load/save
- `tools/edge_dragging.py` - Edge creation
- `themes/theme_engine.py` - Theme switching

### 5.3 Error Messages

**Proposal D2 - Improve error messages with context:**

```python
# Before
raise ValueError(f"Theme '{name}' not registered.")

# After
raise ValueError(
    f"Theme '{name}' not registered. "
    f"Available themes: {', '.join(cls._themes.keys())}"
)
```

### 5.4 API Documentation

**Proposal D3 - Add module-level `__all__` exports:**

Currently only `node_editor/__init__.py` and `node_editor/core/__init__.py` have `__all__`. Add to:
- `node_editor/graphics/__init__.py`
- `node_editor/widgets/__init__.py`
- `node_editor/tools/__init__.py`
- `node_editor/themes/__init__.py`
- `node_editor/nodes/__init__.py`

---

## 6. Testing Improvements

### 6.1 Current Coverage

- 338 tests passing
- Test files exist for: core (node, edge, scene), nodes (all categories)
- No tests for: graphics layer, widgets, tools, themes

**Proposal T1 - Add integration tests:**

```python
# tests/test_integration_workflow.py
class TestNodeEditorWorkflow:
    """Integration tests for common workflows."""
    
    def test_create_connect_evaluate(self):
        """Test creating nodes, connecting them, and evaluating."""
        ...
    
    def test_copy_paste_workflow(self):
        """Test clipboard operations."""
        ...
    
    def test_undo_redo_sequence(self):
        """Test history operations."""
        ...
```

### 6.2 Graphics Testing

**Proposal T2 - Add graphics layer tests with pytest-qt:**

```python
# tests/test_graphics_view.py
class TestGraphicsView:
    def test_zoom_in(self, qtbot, scene):
        view = scene.get_view()
        initial_scale = view.transform().m11()
        # Simulate wheel event
        ...
```

---

## 7. Change Tracking Matrix

### Priority Legend
- 🔴 **HIGH** - Significant impact, should be done first
- 🟡 **MEDIUM** - Valuable improvement, can be scheduled
- 🟢 **LOW** - Nice to have, opportunistic
- ✅ **DONE** - Completed

### Proposed Changes

| ID | Category | Description | Files | Priority | Breaking |
|----|----------|-------------|-------|----------|----------|
| ~~A1~~ | ~~Architecture~~ | ~~Consistent graphics class naming~~ | ~~`core/__init__.py`, `socket.py`, `node.py`, all node files~~ | ✅ DONE | Yes |
| ~~A2~~ | ~~Architecture~~ | ~~Replace OrderedDict with dict~~ | ~~7 files~~ | ✅ DONE | No |
| A3 | Architecture | Extract view states to protocol | `graphics/view.py`, new `tools/view_states.py` | 🟢 | No |
| A4 | Architecture | Add Scene factory methods | `core/scene.py` | 🟢 | No |
| A5 | Architecture | Per-class edge validators | `core/edge.py` | 🟡 | No |
| ~~P1~~ | ~~Performance~~ | ~~Iterative mark_descendants_dirty~~ | ~~`core/node.py`~~ | ✅ DONE | No |
| ~~P2~~ | ~~Performance~~ | ~~Batch edge updates on move~~ | ~~`graphics/node.py`~~ | ✅ DONE | No |
| P3 | Performance | Delta history snapshots | `core/history.py` | 🟢 | No |
| ~~C1~~ | ~~Code~~ | ~~Modern type syntax (3.11+)~~ | ~~Already implemented~~ | ✅ DONE | No |
| ~~C2~~ | ~~Code~~ | ~~IntEnum for constants~~ | ~~`core/socket.py`, `core/edge.py`, `core/__init__.py`~~ | ✅ DONE | No |
| ~~C3~~ | ~~Code~~ | ~~Add `view` property to Scene~~ | ~~`core/scene.py`~~ | ✅ DONE | No |
| ~~C4~~ | ~~Code~~ | ~~Debug logging for silenced exceptions~~ | ~~`graphics/node.py`~~ | ✅ DONE | No |
| C5 | Code | Dataclass for HistoryStamp | `core/history.py` | 🟢 | No |
| C6 | Code | f-strings everywhere | Multiple | 🟢 | No |
| C7 | Code | Consistent method ordering | All classes | 🟢 | No |
| ~~N1~~ | ~~Naming~~ | ~~snake_case attributes~~ | ~~`graphics/edge.py`, `graphics/edge_path.py`~~ | ✅ DONE | Yes |
| N2 | Naming | Positive boolean params | `core/edge.py` | 🟡 | Yes |
| N3 | Naming | Clearer method names | Multiple | 🟡 | Yes |
| ~~D1~~ | ~~Docs~~ | ~~Add logging to modules~~ | ~~5 files~~ | ✅ DONE | No |
| D2 | Docs | Improve error messages | Multiple | 🟢 | No |
| D3 | Docs | Add `__all__` to packages | ~5 `__init__.py` files | 🟢 | No |
| T1 | Testing | Integration tests | New files | 🟡 | No |
| T2 | Testing | Graphics layer tests | New files | 🟢 | No |

---

## 8. Recommended Implementation Order

### ~~Phase 1: Non-Breaking Quick Wins~~ ✅ COMPLETED (2025-01-27)
1. ~~**A2** - Replace OrderedDict with dict~~ ✅
2. ~~**C1** - Modern type syntax~~ ✅ (already implemented)
3. ~~**P1** - Fix recursive mark_descendants_dirty~~ ✅
4. ~~**D1** - Add logging to modules~~ ✅

### Phase 2: Naming Cleanup (1 day, requires test updates)
5. **N1** - snake_case attributes in graphics/edge.py
6. **A1** - Consistent graphics class naming

### Phase 3: Enhancements (ongoing)
7. **C2** - IntEnum for constants
8. **P2** - Batch edge updates
9. **T1/T2** - New tests

---

## 9. Files Modified

### Phase 1 Changes (2025-01-27)

**P1 - Iterative traversal:**
- `node_editor/core/node.py` - `mark_descendants_dirty()` and `mark_descendants_invalid()` now use BFS with visited set

**A2 - OrderedDict removal:**
- `node_editor/core/serializable.py` - Return type changed to `dict`
- `node_editor/core/socket.py` - `serialize()` returns dict literal
- `node_editor/core/edge.py` - `serialize()` returns dict literal
- `node_editor/core/scene.py` - `serialize()` returns dict literal
- `node_editor/core/node.py` - `serialize()` returns dict literal
- `node_editor/core/clipboard.py` - `serialize_selected()` returns dict literal
- `node_editor/widgets/content_widget.py` - `serialize()` returns dict literal

**D1 - Logging added:**
- `node_editor/core/scene.py`
- `node_editor/core/history.py`
- `node_editor/tools/edge_dragging.py`
- `node_editor/themes/theme_engine.py`
- `node_editor/widgets/editor_widget.py`

---

*End of Audit Report*


```python
# Future enhancement - not critical for current scale
class DeltaHistory:
    """Store only changed objects between snapshots."""
    ...
```


**Priority:** Low - Current approach works for typical use cases (<500 nodes).

### 2.4 Thread Safety

**Finding:** All operations run on the main Qt thread. There are no background workers for evaluation. This is correct for Qt GUI but can cause freezing with computationally heavy nodes.

**Recommendation:** Document this limitation. For CPU-heavy evaluations, users should implement async patterns in their custom nodes.

---

## 3. Code Quality & Refactoring Proposals

### 3.1 Type Hints Modernization

**Scope:** All files under `node_editor/`

**Finding:** Python 3.8 compatible syntax is used (`List[str]`, `Optional[X]`). With target Python 3.11+ we can use modern syntax.

**Proposal C1 - Modern type syntax:**

| Before | After |
|--------|-------|
| `Optional[X]` | `X \| None` |
| `List[str]` | `list[str]` |
| `Dict[str, int]` | `dict[str, int]` |
| `Tuple[int, int]` | `tuple[int, int]` |
| `Union[A, B]` | `A \| B` |

**Example transformation:**

```python
# Before (node_editor/core/node.py)
from typing import TYPE_CHECKING, Optional, List

def get_input(self, index: int = 0) -> Optional["Node"]:
    ...

def get_children_nodes(self) -> List["Node"]:
    ...

# After
from typing import TYPE_CHECKING

def get_input(self, index: int = 0) -> "Node | None":
    ...

def get_children_nodes(self) -> list["Node"]:
    ...
```

**Files affected:** ~30 files with type hints.

### 3.2 Enum Usage for Constants

**Files:**
- [node_editor/core/socket.py](../node_editor/core/socket.py#L25-L35) - Position constants
- [node_editor/core/edge.py](../node_editor/core/edge.py#L25-L35) - Edge type constants

```python
# Current
LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2
```

**Proposal C2 - Use IntEnum for type safety:**

```python
from enum import IntEnum, auto

class SocketPosition(IntEnum):
    LEFT_TOP = 1
    LEFT_CENTER = 2
    LEFT_BOTTOM = 3
    RIGHT_TOP = 4
    RIGHT_CENTER = 5
    RIGHT_BOTTOM = 6

class EdgeType(IntEnum):
    DIRECT = 1
    BEZIER = 2
    SQUARE = 3
    IMPROVED_SHARP = 4
    IMPROVED_BEZIER = 5

# Backward compatible via IntEnum subclassing
```

### 3.3 Property vs Method Consistency

**File:** [node_editor/core/node.py](../node_editor/core/node.py)

**Finding:** Inconsistent use of properties vs methods:

| Name | Current | Suggested |
|------|---------|-----------|
| `node.pos` | Property | ✅ Keep |
| `node.get_socket_position()` | Method | ✅ Keep (has side effects) |
| `node.title` | Property | ✅ Keep |
| `socket.is_input` | Property | ✅ Keep |
| `socket.is_output` | Property | ✅ Keep |
| `scene.get_view()` | Method | Could be `view` property |

**Proposal C3 - Add `view` property to Scene:**

```python
@property
def view(self) -> QDMGraphicsView | None:
    """Get the graphics view displaying this scene."""
    return self.get_view()
```

### 3.4 Magic Numbers

**File:** [node_editor/graphics/edge_path.py](../node_editor/graphics/edge_path.py#L30-L40)

```python
EDGE_CP_ROUNDNESS = 100
WEIGHT_SOURCE = 0.2
EDGE_IBCP_ROUNDNESS = 75
NODE_DISTANCE = 12
EDGE_CURVATURE = 2
```

**Assessment:** ✅ Already extracted as named constants. Consider moving to theme for customization.

### 3.5 Exception Handling Specificity

**File:** [node_editor/graphics/node.py](../node_editor/graphics/node.py#L170-L175)

```python
except (RuntimeError, AttributeError):
    # Ignore errors from deleted Qt objects
    pass
```

**Finding:** Silent exception swallowing. Appropriate for Qt cleanup but better to have logging at DEBUG level.

**Proposal C4 - Add debug logging for silenced exceptions:**

```python
except (RuntimeError, AttributeError) as e:
    logger.debug("Ignoring Qt cleanup error: %s", e)
```

### 3.6 Dataclass Candidates

**Finding:** Some simple data containers could be dataclasses:

**Proposal C5 - Convert simple containers to dataclasses:**

```python
# node_editor/core/history.py - History stamp
@dataclass
class HistoryStamp:
    """Single snapshot in the undo/redo stack."""
    description: str
    snapshot: dict
    selection: list[int]
```

### 3.7 String Formatting Consistency

**Scope:** Multiple files

**Finding:** Mix of f-strings and `.format()`. f-strings are more readable and faster.

**Proposal C6 - Use f-strings everywhere:**

```python
# Before
"Error: {}".format(str(e))

# After  
f"Error: {e}"
```

### 3.8 Method Ordering Convention

**Recommendation C7:** Follow consistent method ordering in classes:

1. `__init__` and other dunderes
2. Class methods / Static methods
3. Properties
4. Public methods (alphabetical or logical grouping)
5. Protected methods (`_method`)
6. Private methods (`__method`)

---

## 4. Naming & API Cleanup

### 4.1 Inconsistent Attribute Naming

| Location | Current | Proposed |
|----------|---------|----------|
| `Socket` | `Socket_Graphics_Class` | `_graphics_socket_class` |
| `Node` | `NodeContent_class` | `_content_widget_class` |
| `QDMGraphicsEdge` | `pathCalculator` | `path_calculator` |
| `QDMGraphicsEdge` | `posSource` | `pos_source` |
| `QDMGraphicsEdge` | `posDestination` | `pos_destination` |
| `EdgeDragging` | `drag_start_socket` | ✅ Already snake_case |
| `SceneHistory` | `history_current_step` | ✅ Already snake_case |

**Proposal N1 - Rename to snake_case:**

```python
# node_editor/graphics/edge.py
class QDMGraphicsEdge:
    def __init__(self, ...):
        self.path_calculator = self.determine_edge_path_class()(self)
        self.pos_source = [0, 0]
        self.pos_destination = [200, 100]
```

### 4.2 Boolean Parameter Naming

**File:** [node_editor/core/edge.py](../node_editor/core/edge.py#L250-L270)

```python
def remove(self, silent: bool = False) -> None:
```

**Recommendation N2:** For boolean params, use descriptive names:

```python
def remove(self, *, notify_sockets: bool = True) -> None:
```

(Inverted logic makes positive case explicit)

### 4.3 Method Name Clarity

| Current | Suggested | Reason |
|---------|-----------|--------|
| `do_select()` | `select()` | "do_" prefix unnecessary |
| `do_deselect_items()` | `deselect_all()` | Clearer intent |
| `getSnappedSocketItem()` | `get_snapped_socket()` | snake_case |
| `getSnappedToSocketPosition()` | `get_snap_position()` | Shorter, clearer |

### 4.4 Unused Parameters

**Files:** Multiple

**Finding:** Some methods have unused parameters (correctly prefixed with `_`):

```python
def paint(self, painter, _option, _widget=None) -> None:
```

**Assessment:** ✅ Already following convention with `_` prefix.

---

## 5. Documentation & Logging

### 5.1 Missing Module Docstrings

**Status:** ✅ All modules have docstrings with Author and Date.

### 5.2 Logger Usage

**Files:** Only `edge_rerouting.py` imports logger:

```python
# node_editor/tools/edge_rerouting.py
logger = logging.getLogger(__name__)
```

**Proposal D1 - Add logging to all modules:**

```python
# Add to each module that performs significant operations
import logging

logger = logging.getLogger(__name__)
```

**Key places to add logging:**
- `core/scene.py` - File operations, node/edge add/remove
- `core/history.py` - Undo/redo operations
- `widgets/editor_widget.py` - File load/save
- `tools/edge_dragging.py` - Edge creation
- `themes/theme_engine.py` - Theme switching

### 5.3 Error Messages

**Proposal D2 - Improve error messages with context:**

```python
# Before
raise ValueError(f"Theme '{name}' not registered.")

# After
raise ValueError(
    f"Theme '{name}' not registered. "
    f"Available themes: {', '.join(cls._themes.keys())}"
)
```

### 5.4 API Documentation

**Proposal D3 - Add module-level `__all__` exports:**

Currently only `node_editor/__init__.py` and `node_editor/core/__init__.py` have `__all__`. Add to:
- `node_editor/graphics/__init__.py`
- `node_editor/widgets/__init__.py`
- `node_editor/tools/__init__.py`
- `node_editor/themes/__init__.py`
- `node_editor/nodes/__init__.py`

---

## 6. Testing Improvements

### 6.1 Current Coverage

- 338 tests passing
- Test files exist for: core (node, edge, scene), nodes (all categories)
- No tests for: graphics layer, widgets, tools, themes

**Proposal T1 - Add integration tests:**

```python
# tests/test_integration_workflow.py
class TestNodeEditorWorkflow:
    """Integration tests for common workflows."""
    
    def test_create_connect_evaluate(self):
        """Test creating nodes, connecting them, and evaluating."""
        ...
    
    def test_copy_paste_workflow(self):
        """Test clipboard operations."""
        ...
    
    def test_undo_redo_sequence(self):
        """Test history operations."""
        ...
```

### 6.2 Graphics Testing

**Proposal T2 - Add graphics layer tests with pytest-qt:**

```python
# tests/test_graphics_view.py
class TestGraphicsView:
    def test_zoom_in(self, qtbot, scene):
        view = scene.get_view()
        initial_scale = view.transform().m11()
        # Simulate wheel event
        ...
```

---

## 7. Change Tracking Matrix

### Priority Legend
- 🔴 **HIGH** - Significant impact, should be done first
- 🟡 **MEDIUM** - Valuable improvement, can be scheduled
- 🟢 **LOW** - Nice to have, opportunistic
- ✅ **DONE** - Completed

### Proposed Changes

| ID | Category | Description | Files | Priority | Breaking |
|----|----------|-------------|-------|----------|----------|
| ~~A1~~ | ~~Architecture~~ | ~~Consistent graphics class naming~~ | ~~`core/__init__.py`, `socket.py`, `node.py`, all node files~~ | ✅ DONE | Yes |
| ~~A2~~ | ~~Architecture~~ | ~~Replace OrderedDict with dict~~ | ~~7 files~~ | ✅ DONE | No |
| A3 | Architecture | Extract view states to protocol | `graphics/view.py`, new `tools/view_states.py` | 🟢 | No |
| A4 | Architecture | Add Scene factory methods | `core/scene.py` | 🟢 | No |
| A5 | Architecture | Per-class edge validators | `core/edge.py` | 🟡 | No |
| ~~P1~~ | ~~Performance~~ | ~~Iterative mark_descendants_dirty~~ | ~~`core/node.py`~~ | ✅ DONE | No |
| ~~P2~~ | ~~Performance~~ | ~~Batch edge updates on move~~ | ~~`graphics/node.py`~~ | ✅ DONE | No |
| P3 | Performance | Delta history snapshots | `core/history.py` | 🟢 | No |
| ~~C1~~ | ~~Code~~ | ~~Modern type syntax (3.11+)~~ | ~~Already implemented~~ | ✅ DONE | No |
| ~~C2~~ | ~~Code~~ | ~~IntEnum for constants~~ | ~~`core/socket.py`, `core/edge.py`, `core/__init__.py`~~ | ✅ DONE | No |
| ~~C3~~ | ~~Code~~ | ~~Add `view` property to Scene~~ | ~~`core/scene.py`~~ | ✅ DONE | No |
| ~~C4~~ | ~~Code~~ | ~~Debug logging for silenced exceptions~~ | ~~`graphics/node.py`~~ | ✅ DONE | No |
| C5 | Code | Dataclass for HistoryStamp | `core/history.py` | 🟢 | No |
| C6 | Code | f-strings everywhere | Multiple | 🟢 | No |
| C7 | Code | Consistent method ordering | All classes | 🟢 | No |
| ~~N1~~ | ~~Naming~~ | ~~snake_case attributes~~ | ~~`graphics/edge.py`, `graphics/edge_path.py`~~ | ✅ DONE | Yes |
| N2 | Naming | Positive boolean params | `core/edge.py` | 🟡 | Yes |
| N3 | Naming | Clearer method names | Multiple | 🟡 | Yes |
| ~~D1~~ | ~~Docs~~ | ~~Add logging to modules~~ | ~~5 files~~ | ✅ DONE | No |
| D2 | Docs | Improve error messages | Multiple | 🟢 | No |
| D3 | Docs | Add `__all__` to packages | ~5 `__init__.py` files | 🟢 | No |
| T1 | Testing | Integration tests | New files | 🟡 | No |
| T2 | Testing | Graphics layer tests | New files | 🟢 | No |

---

## 8. Recommended Implementation Order

### ~~Phase 1: Non-Breaking Quick Wins~~ ✅ COMPLETED (2025-01-27)
1. ~~**A2** - Replace OrderedDict with dict~~ ✅
2. ~~**C1** - Modern type syntax~~ ✅ (already implemented)
3. ~~**P1** - Fix recursive mark_descendants_dirty~~ ✅
4. ~~**D1** - Add logging to modules~~ ✅

### Phase 2: Naming Cleanup (1 day, requires test updates)
5. **N1** - snake_case attributes in graphics/edge.py
6. **A1** - Consistent graphics class naming

### Phase 3: Enhancements (ongoing)
7. **C2** - IntEnum for constants
8. **P2** - Batch edge updates
9. **T1/T2** - New tests

---

## 9. Files Modified

### Phase 1 Changes (2025-01-27)

**P1 - Iterative traversal:**
- `node_editor/core/node.py` - `mark_descendants_dirty()` and `mark_descendants_invalid()` now use BFS with visited set

**A2 - OrderedDict removal:**
- `node_editor/core/serializable.py` - Return type changed to `dict`
- `node_editor/core/socket.py` - `serialize()` returns dict literal
- `node_editor/core/edge.py` - `serialize()` returns dict literal
- `node_editor/core/scene.py` - `serialize()` returns dict literal
- `node_editor/core/node.py` - `serialize()` returns dict literal
- `node_editor/core/clipboard.py` - `serialize_selected()` returns dict literal
- `node_editor/widgets/content_widget.py` - `serialize()` returns dict literal

**D1 - Logging added:**
- `node_editor/core/scene.py`
- `node_editor/core/history.py`
- `node_editor/tools/edge_dragging.py`
- `node_editor/themes/theme_engine.py`
- `node_editor/widgets/editor_widget.py`

---

*End of Audit Report*


---

## 10. Phase 2 Completion Summary (2025-12-13)

### Changes Applied

**N1 - snake_case attributes:**
- `node_editor/graphics/edge.py` - Renamed `pathCalculator` → `path_calculator`, `posSource` → `pos_source`, `posDestination` → `pos_destination`
- `node_editor/graphics/edge_path.py` - Updated all path calculators to use new attributes

**A1 - Consistent graphics class naming:**
- `node_editor/core/socket.py` - `Socket_Graphics_Class` → `_graphics_socket_class`
- `node_editor/core/node.py` - `NodeContent_class` → `_content_widget_class` 
- `node_editor/core/__init__.py` - Updated injection logic
- All built-in nodes (27+ instances across 8 files)
- Custom example nodes (calculator)

### Validation
- ✅ All 338 tests passing
- ✅ Ruff linting clean
- ✅ Calculator example verified

### Migration Note
This is a **BREAKING CHANGE** for custom node implementations. Update:
```python
# Before
class MyNode(Node):
    NodeContent_class = MyContent
    
# After  
class MyNode(Node):
    _content_widget_class = MyContent
```


---

## 11. Phase 3 Completion Summary (2025-12-13)

### Changes Applied

**C2 - IntEnum for constants:**
- `node_editor/core/socket.py` - Created `SocketPosition(IntEnum)` with backward-compatible module constants
- `node_editor/core/edge.py` - Created `EdgeType(IntEnum)` with backward-compatible module constants
- `node_editor/core/__init__.py` - Exported new enum types

**C3 - Add view property to Scene:**
- `node_editor/core/scene.py` - Added `view` property as convenience accessor for `get_view()`

**C4 - Debug logging for silenced exceptions:**
- `node_editor/graphics/node.py` - Added debug logging for Qt cleanup errors in `mouseMoveEvent()` and `_batch_update_edges()`

**P2 - Batch edge updates on node move:**
- `node_editor/graphics/node.py` - Implemented deferred batch updates using QTimer to optimize performance when dragging multiple nodes. Edge updates now happen once per frame instead of on every mouse move event.

### Benefits

- **Type Safety**: IntEnum provides IDE autocomplete and type checking while maintaining backward compatibility
- **Performance**: Batch edge updates reduce redundant calculations during multi-node drag operations
- **Debugging**: Silent exceptions are now logged at DEBUG level for troubleshooting
- **API Convenience**: `scene.view` property provides cleaner syntax than `scene.get_view()`

### Validation
- ✅ All 338 tests passing
- ✅ Ruff linting clean
- ✅ Backward compatibility maintained (old constants still work)

### Breaking Changes
None - All changes are backward compatible. Existing code using integer constants continues to work.

