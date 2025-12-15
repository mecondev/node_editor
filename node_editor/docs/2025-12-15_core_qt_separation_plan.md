# Core Qt Separation - Implementation Plan

**Date:** 2025-12-15  
**Author:** Implementation plan for removing runtime Qt coupling from core layer  
**Status:** Plan (awaiting confirmation)

---

## Objectives

Remove runtime Qt dependencies from `node_editor/core/` while keeping the standalone GUI application fully functional.

### What Changes and Why

**Primary Goal:**
- Core layer (`node_editor/core/`) must not return or manipulate Qt graphics objects at runtime
- Core must contain only graph/domain logic, serialization, history, clipboard, and host bridge
- Qt usage remains in `graphics/` and `widgets/` layers

**What Does NOT Change:**
- ✅ ULID sid system - untouched
- ✅ Snapshot schema v2 - untouched
- ✅ Persistence adapter - untouched
- ✅ Host bridge semantics - untouched
- ✅ TYPE_CHECKING Qt imports - remain in core (typing-only, no runtime impact)
- ✅ Node/Edge domain logic - untouched

---

## Methods Being Removed from `core/scene.py`

### 1. View Access Methods (Lines 369-386)

**Methods:**
- `get_view() -> QGraphicsView`
- `view` property (returns `QGraphicsView`)

**Why UI-Bound:**
- Return Qt widget objects directly
- View is a UI concern, not domain logic
- Scene (domain) should not expose UI layer objects

**Where They Go:**
- **REMOVED** - callers already have access via `widget.view`
- Existing code: `NodeEditorWidget.view` already provides this
- Update callers to use `self.view` instead of `self.scene.get_view()`

---

### 2. Graphics Item Query (Lines 388-397)

**Method:**
- `get_item_at(pos: QPointF) -> QGraphicsItem | None`

**Why UI-Bound:**
- Takes Qt coordinate type (`QPointF`)
- Returns Qt graphics item (`QGraphicsItem`)
- Hit-testing is view/graphics responsibility

**Where It Goes:**
- Move to `widgets/editor_widget.py` as:
  ```python
  def get_item_at(self, pos: QPointF) -> QGraphicsItem | None:
      """Find graphics item at scene position."""
      return self.view.itemAt(pos)
  ```

---

### 3. Drag/Drop Listener Registration (Lines 351-366)

**Methods:**
- `add_drag_enter_listener(callback)`
- `add_drop_listener(callback)`

**Why UI-Bound:**
- Delegate directly to view
- Drag/drop is view-level event handling
- Scene (domain) should not manage view events

**Where They Go:**
- **REMOVED** - callers use `view.add_drag_enter_listener()` directly
- Examples: `self.view.add_drag_enter_listener(self.on_drag_enter)`

---

### 4. Graphics Selection Query (Lines 248-254)

**Method:**
- `get_selected_items() -> list[QGraphicsItem]`

**Why UI-Bound:**
- Returns Qt graphics items, not domain objects
- Selection state should be queried from domain model

**Replacement in Core:**
```python
def get_selected_nodes(self) -> list[Node]:
    """Return nodes currently marked as selected."""
    return [n for n in self.nodes if n.is_selected()]

def get_selected_edges(self) -> list[Edge]:
    """Return edges currently marked as selected."""
    return [e for e in self.edges if e.is_selected()]
```

**For UI Layer:**
- If Qt items needed: `scene.graphics_scene.selectedItems()` (direct call from widgets)

---

### 5. Graphics Deselection (Lines 256-264)

**Method:**
- `do_deselect_items(silent: bool = False)`

**Current Implementation:**
```python
def do_deselect_items(self, silent: bool = False):
    for item in self.get_selected_items():  # Returns QGraphicsItem
        item.setSelected(False)             # Qt API call
    if not silent:
        self.on_items_deselected()
```

**Refactored Version (stays in core, but uses domain objects):**
```python
def deselect_all(self) -> None:
    """Deselect all nodes and edges."""
    for node in self.nodes:
        if node.is_selected():
            node.do_select(False)
    for edge in self.edges:
        if edge.is_selected():
            edge.do_select(False)
```

---

### 6. Graphics State Reset (Lines 266-276)

**Method:**
- `reset_last_selected_states()`

**Current Implementation:**
```python
def reset_last_selected_states(self):
    for node in self.nodes:
        node.graphics_node._last_selected_state = False
    for edge in self.edges:
        edge.graphics_edge._last_selected_state = False
```

**Why UI-Bound:**
- Accesses `_last_selected_state` - a graphics-layer internal flag
- Not domain logic - purely graphics bookkeeping

**Where It Goes:**
- Move to `graphics/scene.py` (QDMGraphicsScene class):
  ```python
  def reset_last_selected_states(self):
      """Clear internal selection state flags on graphics items."""
      for item in self.items():
          if hasattr(item, '_last_selected_state'):
              item._last_selected_state = False
  ```
- Called from graphics layer when needed, not from core

---

## APIs Remaining in Core (Domain-Only)

### Node/Edge Management (unchanged)
- `nodes: list[Node]`
- `edges: list[Edge]`
- `add_node(node)`, `remove_node(node)`
- `add_edge(edge)`, `remove_edge(edge)`

### Selection (domain-level, NEW)
- `get_selected_nodes() -> list[Node]`
- `get_selected_edges() -> list[Edge]`
- `deselect_all()` (refactored to use domain objects)

### Serialization (unchanged)
- `serialize()`, `deserialize()`
- `to_snapshot()`, `from_snapshot()`
- ULID sid tracking
- Snapshot schema v2

### State Management (unchanged)
- `has_been_modified` property
- `history: SceneHistory`
- `clipboard: SceneClipboard`
- `host_bridge: NodeHostBridge`

### Callbacks (unchanged)
- `add_has_been_modified_listener()`
- `add_item_selected_listener()`
- `add_items_deselected_listener()`
- Selection event handlers: `on_item_selected()`, `on_items_deselected()`

### Node/Edge Factory (unchanged)
- `get_node_class()`, `get_edge_class()`
- `set_node_class_selector()`

---

## Files to Touch

| File | Changes | Lines Affected |
|------|---------|----------------|
| `node_editor/core/scene.py` | Remove: `get_view()`, `view`, `get_item_at()`, `add_drag_enter_listener()`, `add_drop_listener()`, `reset_last_selected_states()` <br> Refactor: `get_selected_items()` → `get_selected_nodes/edges()` <br> Refactor: `do_deselect_items()` → `deselect_all()` | ~369-397, 248-276 |
| `node_editor/graphics/scene.py` | Add: `reset_last_selected_states()` method | New method |
| `node_editor/widgets/editor_widget.py` | Add: `get_item_at(pos)` convenience method (optional) | New method (optional) |
| `tests/test_core_no_runtime_qt.py` | New file: Guard test to prevent runtime Qt imports in core | New file |
| `tests/test_core_scene.py` | Update tests to use new domain-level selection APIs | Various |
| `examples/string_processor/str_sub_window.py` | Update: Use `self.view` instead of `self.scene.get_view()` | ~2-3 calls |
| `examples/calculator/calc_sub_window.py` | Update: Use `self.view` instead of `self.scene.get_view()` | ~2-3 calls |

**Note:** Examples may break temporarily - will be fixed in a later phase.

---

## Tests to Add / Update

### New Test: Runtime Qt Import Guard

**File:** `tests/test_core_no_runtime_qt.py`

**Purpose:**
- Ensure core modules have no runtime Qt imports
- TYPE_CHECKING imports are explicitly allowed
- Fail if any Qt library is imported outside TYPE_CHECKING blocks

**Implementation:**
```python
"""Verify core modules have no runtime Qt imports."""

import ast
import pathlib

CORE_PATH = pathlib.Path("node_editor/core")
FORBIDDEN_PREFIXES = ("PyQt5", "PyQt6", "PySide2", "PySide6", "qtpy")

def test_core_no_runtime_qt_imports():
    """Core must not import Qt at runtime (TYPE_CHECKING is allowed)."""
    violations = []
    
    for pyfile in CORE_PATH.glob("*.py"):
        source = pyfile.read_text()
        tree = ast.parse(source)
        
        # Find TYPE_CHECKING block line ranges
        type_checking_ranges = []
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                    start = node.body[0].lineno if node.body else node.lineno
                    end = node.body[-1].end_lineno if node.body else node.lineno
                    type_checking_ranges.append((start, end))
        
        # Check all imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Skip if inside TYPE_CHECKING block
                in_type_checking = any(
                    start <= node.lineno <= end
                    for start, end in type_checking_ranges
                )
                if in_type_checking:
                    continue
                
                # Check module name
                module = getattr(node, "module", None) or ""
                names = [alias.name for alias in node.names]
                for name in [module] + names:
                    if name and any(name.startswith(p) for p in FORBIDDEN_PREFIXES):
                        violations.append(f"{pyfile.name}:{node.lineno} imports {name}")
    
    assert not violations, f"Runtime Qt imports in core:\n" + "\n".join(violations)
```

### Updated Tests: Domain-Level Selection

**File:** `tests/test_core_scene.py`

**Changes:**
- Replace `scene.get_selected_items()` with `scene.get_selected_nodes()` + `scene.get_selected_edges()`
- Replace `scene.do_deselect_items()` with `scene.deselect_all()`
- Remove any direct Qt item manipulation in core tests
- Test that selection APIs return domain objects (Node/Edge), not Qt items

---

## Implementation Sequence

### Step 1: Add New Domain Selection APIs (non-breaking)
- Add `get_selected_nodes()` to Scene
- Add `get_selected_edges()` to Scene
- These are additions, don't break existing code

### Step 2: Add Guard Test (validates constraint)
- Create `tests/test_core_no_runtime_qt.py`
- Run it - should pass (no runtime Qt in core currently)

### Step 3: Refactor `do_deselect_items()` (minor breaking)
- Rename to `deselect_all()`
- Change implementation to iterate domain objects
- Update internal callers (history, clipboard)

### Step 4: Move `reset_last_selected_states()` to Graphics
- Add method to `QDMGraphicsScene` in `graphics/scene.py`
- Update callers to use `scene.graphics_scene.reset_last_selected_states()`

### Step 5: Remove View Access Methods (breaking for examples)
- Remove `get_view()`, `view` property
- Remove `get_item_at()`
- Remove `add_drag_enter_listener()`, `add_drop_listener()`
- Update internal callers (should be minimal)

### Step 6: Remove/Deprecate `get_selected_items()`
- Remove or mark deprecated
- All internal code uses new domain APIs

### Step 7: Update Tests
- Update `test_core_scene.py` for new selection APIs
- Ensure `test_core_no_runtime_qt.py` passes

### Step 8: Verify
- Run `pytest -q`
- Run `ruff check .`
- Confirm examples may be broken (expected)

---

## Breaking Changes & Migration

### For Internal Code (node_editor/*)

| Old API | New API |
|---------|---------|
| `scene.get_view()` | `widget.view` or `self.view` |
| `scene.view` | `widget.view` |
| `scene.get_item_at(pos)` | `widget.view.itemAt(pos)` or add `widget.get_item_at()` |
| `scene.add_drag_enter_listener(cb)` | `view.add_drag_enter_listener(cb)` |
| `scene.add_drop_listener(cb)` | `view.add_drop_listener(cb)` |
| `scene.get_selected_items()` | `scene.get_selected_nodes()` + `scene.get_selected_edges()` |
| `scene.do_deselect_items()` | `scene.deselect_all()` |
| `scene.reset_last_selected_states()` | `scene.graphics_scene.reset_last_selected_states()` |

### For Examples (to be fixed later)

Examples will need updates in their sub-window classes:
- Change `self.scene.get_view()` → `self.view`
- Change `self.scene.add_drag_enter_listener()` → `self.view.add_drag_enter_listener()`
- Change `self.scene.add_drop_listener()` → `self.view.add_drop_listener()`

**Decision:** Examples allowed to break temporarily.

---

## Validation Criteria

### Must Pass:
- ✅ `pytest -q` - all tests pass
- ✅ `ruff check .` - no linting errors
- ✅ `test_core_no_runtime_qt.py` - guard test passes
- ✅ Core modules import no Qt at runtime (verified by guard test)

### Expected to Break:
- ⚠️ Examples (`examples/string_processor/`, `examples/calculator/`)
- Will be fixed in a later phase

### Must NOT Change:
- ❌ ULID sid system
- ❌ Snapshot schema v2
- ❌ Persistence adapter
- ❌ Host bridge semantics
- ❌ TYPE_CHECKING Qt imports (remain for type hints)

---

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Break existing code unknowingly | Comprehensive test suite, guard test |
| Miss runtime Qt usage | Guard test catches all runtime imports |
| Examples break | Accepted - fix in later phase |
| Unclear separation boundary | Clear documentation of what belongs in core vs graphics |

---

## Summary

This plan removes 8 UI-bound methods from `core/scene.py` and establishes a clean separation:

- **Core:** Domain logic, serialization, history, clipboard (no Qt at runtime)
- **Graphics:** Visual representation, Qt scene/items, state flags
- **Widgets:** Qt windows, views, user interaction

The separation is enforced by a guard test and validated by the existing test suite.

**Next Step:** Await confirmation to proceed with implementation (PHASE 1).
