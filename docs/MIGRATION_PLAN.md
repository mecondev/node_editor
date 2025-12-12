# Migration Plan: Incremental Renaming to PEP8 Conventions

**Status**: Proposed  
**Target Version**: 2.0.0  
**Migration Duration**: 3-6 months  
**Approach**: Gradual with deprecation warnings

---

## Overview

This plan ensures backward compatibility during the transition from camelCase to snake_case naming conventions. Each phase includes deprecation warnings, testing, and a grace period before removal.

---

## Phase 1: Add Deprecation Infrastructure (Week 1)

**Goal**: Create helper utilities for deprecation warnings without changing any public API.

### Tasks
1. Create `node_editor/utils/deprecation.py`:
   ```python
   import warnings
   from functools import wraps
   
   def deprecated_alias(old_name: str, new_name: str, version: str):
       """Emit deprecation warning for renamed attributes/methods."""
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               warnings.warn(
                   f"'{old_name}' is deprecated, use '{new_name}' instead. "
                   f"Will be removed in version {version}.",
                   DeprecationWarning,
                   stacklevel=2
               )
               return func(*args, **kwargs)
           return wrapper
       return decorator
   ```

2. Add deprecation testing utilities in `tests/test_deprecations.py`

### Testing
- ✓ Run full test suite: `pytest`
- ✓ No existing tests should break
- ✓ Verify deprecation warnings can be captured in tests

### Commit
```bash
git commit -m "Add deprecation infrastructure for gradual API migration"
```

---

## Phase 2: Rename State Methods (Weeks 2-3)

**Target**: `markDirty` → `mark_dirty`, `markInvalid` → `mark_invalid`  
**Files**: `node_editor/core/node.py`  
**Impact**: Public API, widely used

### Step 2.1: Add new snake_case methods (Week 2)

1. In `node_editor/core/node.py`, add new methods alongside old:
   ```python
   def mark_dirty(self, dirty: bool = True) -> None:
       """Mark this node as needing re-evaluation (PEP8 naming)."""
       # Implementation here
   
   def markDirty(self, dirty: bool = True) -> None:
       """Mark this node as needing re-evaluation.
       
       .. deprecated:: 1.1.0
           Use :meth:`mark_dirty` instead.
       """
       warnings.warn(
           "'markDirty' is deprecated, use 'mark_dirty' instead. "
           "Will be removed in version 2.0.0.",
           DeprecationWarning,
           stacklevel=2
       )
       return self.mark_dirty(dirty)
   ```

2. Add similar aliases for:
   - `markInvalid` → `mark_invalid`
   - `markDescendantsDirty` → `mark_descendants_dirty`
   - `markDescendantsInvalid` → `mark_descendants_invalid`

### Step 2.2: Update internal usage (Week 3)

1. Update all **internal** calls in `node_editor/` to use new names
2. Keep examples using old names (to test deprecation warnings)

### Testing
- ✓ Run `pytest -W error::DeprecationWarning` on internal code
- ✓ Verify examples show deprecation warnings but still work
- ✓ All 328 tests pass
- ✓ Check that both old and new names work identically

### Commit
```bash
git commit -m "Add snake_case aliases for mark_* methods with deprecation warnings"
git commit -m "Update internal usage to mark_dirty/mark_invalid"
```

---

## Phase 3: Rename Graphics Attributes (Weeks 4-6)

**Target**: `grNode` → `graphics_node`, `grEdge` → `graphics_edge`, `grSocket` → `graphics_socket`  
**Files**: `node_editor/core/{node,edge,socket}.py`  
**Impact**: High - public attributes accessed directly

### Step 3.1: Add property aliases (Week 4)

In `node_editor/core/node.py`:
```python
@property
def graphics_node(self):
    """Graphics representation of this node (PEP8 naming)."""
    return self._graphics_node

@property
def grNode(self):
    """Graphics representation of this node.
    
    .. deprecated:: 1.1.0
        Use :attr:`graphics_node` instead.
    """
    warnings.warn(
        "'grNode' is deprecated, use 'graphics_node' instead. "
        "Will be removed in version 2.0.0.",
        DeprecationWarning,
        stacklevel=2
    )
    return self._graphics_node

@graphics_node.setter
def graphics_node(self, value):
    self._graphics_node = value

@grNode.setter
def grNode(self, value):
    warnings.warn(
        "'grNode' is deprecated, use 'graphics_node' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    self._graphics_node = value
```

### Step 3.2: Update internal usage (Week 5)

1. Search and replace in internal code:
   - `self.grNode` → `self.graphics_node`
   - `node.grNode` → `node.graphics_node`
   - `edge.grEdge` → `edge.graphics_edge`
   - `socket.grSocket` → `socket.graphics_socket`

2. Update all docstrings and comments

### Step 3.3: Update graphics class assignments (Week 6)

In `node_editor/core/__init__.py` `_init_graphics_classes()`:
```python
Node.GraphicsNode_class = QDMGraphicsNode  # Keep for now
Node._graphics_node_class = QDMGraphicsNode  # New internal name
```

### Testing
- ✓ Run full test suite after each file change
- ✓ Test with `-W error::DeprecationWarning` on internal code
- ✓ Verify external examples using `grNode` still work with warnings
- ✓ Check serialization/deserialization compatibility

### Commit (one per subsystem)
```bash
git commit -m "Add graphics_node/graphics_edge/graphics_socket property aliases"
git commit -m "Update core/ internal usage to graphics_* attributes"
git commit -m "Update graphics/ internal usage to graphics_* attributes"
git commit -m "Update widgets/ internal usage to graphics_* attributes"
git commit -m "Update nodes/ internal usage to graphics_* attributes"
```

---

## Phase 4: Update Graphics Class Names (Weeks 7-8)

**Target**: Internal class attribute naming consistency  
**Files**: `node_editor/core/__init__.py`  
**Impact**: Low - mostly internal

### Tasks
1. Rename `GraphicsNode_class` → `_graphics_node_class` (private convention)
2. Add deprecated alias:
   ```python
   @property
   def GraphicsNode_class(self):
       warnings.warn(...)
       return self._graphics_node_class
   ```

### Testing
- ✓ Test custom node classes that override `GraphicsNode_class`
- ✓ Verify subclassing still works

### Commit
```bash
git commit -m "Rename GraphicsNode_class to _graphics_node_class (internal)"
```

---

## Phase 5: Update Examples and Documentation (Week 9)

**Goal**: Show users the new API while old API still works

### Tasks
1. Update `README.md` code examples to use new names
2. Update `examples/` to use new API
3. Add migration guide to docs
4. Update all docstring examples

### Testing
- ✓ Run all examples
- ✓ Verify they show NO deprecation warnings
- ✓ Check documentation builds correctly

### Commit
```bash
git commit -m "Update examples and docs to use new PEP8 naming"
```

---

## Phase 6: Release v1.1.0 with Deprecations (Week 10)

**Goal**: Ship dual API with warnings

### Tasks
1. Update `__version__` to `1.1.0`
2. Update `CHANGES.rst`:
   ```
   Version 1.1.0 (2025-XX-XX)
   --------------------------
   
   Deprecations:
   - markDirty/markInvalid → mark_dirty/mark_invalid
   - grNode/grEdge/grSocket → graphics_node/graphics_edge/graphics_socket
   - GraphicsNode_class → _graphics_node_class (internal)
   
   All old names still work but emit DeprecationWarning.
   Will be removed in version 2.0.0 (estimated 6 months).
   ```

3. Tag release: `git tag v1.1.0`
4. Announce on GitHub with migration guide

### Testing
- ✓ Full test suite passes
- ✓ Examples work
- ✓ Package installs correctly
- ✓ Backwards compatibility verified

---

## Phase 7: Grace Period (Months 4-6)

**Duration**: 3 months minimum  
**Activities**:
- Monitor GitHub issues for migration problems
- Help users migrate their code
- Collect feedback on API improvements

### User Migration Checklist
Provide this to users:

```bash
# Find all occurrences in your codebase
grep -r "\.grNode\|\.grEdge\|\.grSocket" .
grep -r "markDirty\|markInvalid" .

# Automated replacement (use with caution!)
# Test thoroughly after!
find . -name "*.py" -exec sed -i 's/\.grNode/.graphics_node/g' {} +
find . -name "*.py" -exec sed -i 's/\.grEdge/.graphics_edge/g' {} +
find . -name "*.py" -exec sed -i 's/\.grSocket/.graphics_socket/g' {} +
find . -name "*.py" -exec sed -i 's/\.markDirty(/.mark_dirty(/g' {} +
find . -name "*.py" -exec sed -i 's/\.markInvalid(/.mark_invalid(/g' {} +
```

---

## Phase 8: Remove Deprecated Names (Month 7)

**Target**: v2.0.0 release  
**Breaking Changes**: Yes

### Tasks
1. Remove all deprecated aliases:
   - Delete `markDirty`, `markInvalid` methods
   - Delete `grNode`, `grEdge`, `grSocket` properties
   - Delete `GraphicsNode_class` property

2. Update version to `2.0.0`
3. Update docs to reflect breaking changes

### Testing
- ✓ Full test suite passes
- ✓ No deprecation warnings in internal code
- ✓ Examples work
- ✓ Update tests that explicitly tested deprecated API

### Commit
```bash
git commit -m "Remove deprecated camelCase API (BREAKING: v2.0.0)"
```

---

## Rollback Strategy

If issues arise at any phase:

1. **Before v1.1.0 release**: Revert commits, no external impact
2. **After v1.1.0 release**: Keep deprecated API indefinitely if needed
3. **Emergency fix**: Release v1.1.1 with extended deprecation period

---

## Testing Checklist (Every Phase)

- [ ] Run `pytest` - all 328 tests pass
- [ ] Run `pytest -W error::DeprecationWarning` on `node_editor/`
- [ ] Run `ruff check .` - no new linting errors
- [ ] Run examples manually
- [ ] Check serialization format unchanged
- [ ] Verify backwards compatibility

---

## Success Criteria

✅ **Phase complete when**:
- All tests pass
- No unintended deprecation warnings in internal code
- Examples work with new API
- Documentation updated
- Commit pushed with clear message

✅ **Migration successful when**:
- Clean PEP8 naming throughout
- Zero deprecation warnings in framework code
- Users had 6+ months to migrate
- v2.0.0 released with removed deprecated API

---

## Timeline Summary

| Phase | Duration | Release |
|-------|----------|---------|
| 1. Infrastructure | 1 week | - |
| 2. State methods | 2 weeks | - |
| 3. Graphics attrs | 3 weeks | - |
| 4. Class names | 2 weeks | - |
| 5. Examples/docs | 1 week | - |
| 6. Release v1.1.0 | 1 week | **v1.1.0** |
| 7. Grace period | 3 months | - |
| 8. Remove old API | 1 week | **v2.0.0** |
| **Total** | **~6 months** | |

---

**Next Steps**:
1. Review this plan with team/maintainers
2. Get approval for breaking changes
3. Start with Phase 1 (infrastructure)
4. Proceed incrementally, testing at each step

**Questions?** Open an issue to discuss before starting.
