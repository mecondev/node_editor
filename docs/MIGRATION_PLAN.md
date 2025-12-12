# Migration Plan: Direct Renaming to PEP8 Conventions

**Status**: Proposed  
**Target Version**: 2.0.0  
**Migration Duration**: 2-4 weeks  
**Approach**: Direct renames with comprehensive testing

---

## Overview

This plan performs direct renames from camelCase to snake_case without maintaining backward compatibility. Each phase is small, tested thoroughly, and committed independently to enable easy rollback if needed.

---

## Phase 1: Rename State Methods (Days 1-2)

**Target**: `markDirty` → `mark_dirty`, `markInvalid` → `mark_invalid`  
**Files**: `node_editor/core/node.py` and all call sites  
**Impact**: Public API, widely used

### Step 1.1: Prepare rename script (Day 1 morning)

Create `scripts/rename_state_methods.sh`:
```bash
#!/bin/bash
# Automated rename of state methods
find node_editor tests examples -name "*.py" -exec sed -i \
  -e 's/\.markDirty(/.mark_dirty(/g' \
  -e 's/\.markInvalid(/.mark_invalid(/g' \
  -e 's/\.markDescendantsDirty(/.mark_descendants_dirty(/g' \
  -e 's/\.markDescendantsInvalid(/.mark_descendants_invalid(/g' \
  {} +
```

### Step 1.2: Rename method definitions (Day 1 afternoon)

1. In `node_editor/core/node.py`, rename methods:
   - `markDirty` → `mark_dirty`
   - `markInvalid` → `mark_invalid`
   - `markDescendantsDirty` → `mark_descendants_dirty`
   - `markDescendantsInvalid` → `mark_descendants_invalid`

2. Update all docstrings referencing these methods

### Step 1.3: Update all call sites (Day 2)

1. Run the rename script on entire codebase
2. Manually verify changes in critical files:
   - `node_editor/core/node.py`
   - `node_editor/nodes/*.py`
   - `examples/*/main.py`

### Testing
- ✓ Run `pytest` - all 328 tests must pass
- ✓ Run `ruff check .` - no new errors
- ✓ Run examples manually to verify behavior
- ✓ Check git diff for unintended changes

### Commit
```bash
git commit -m "Rename state methods to snake_case (BREAKING)

- markDirty → mark_dirty
- markInvalid → mark_invalid  
- markDescendantsDirty → mark_descendants_dirty
- markDescendantsInvalid → mark_descendants_invalid"
```

---

## Phase 2: Rename Graphics Attributes (Days 3-5)

**Target**: `grNode` → `graphics_node`, `grEdge` → `graphics_edge`, `grSocket` → `graphics_socket`  
**Files**: All files accessing these attributes  
**Impact**: High - public attributes accessed directly

### Step 2.1: Prepare rename script (Day 3 morning)

Create `scripts/rename_graphics_attrs.sh`:
```bash
#!/bin/bash
# Automated rename of graphics attributes
find node_editor tests examples -name "*.py" -exec sed -i \
  -e 's/\.grNode\b/.graphics_node/g' \
  -e 's/\.grEdge\b/.graphics_edge/g' \
  -e 's/\.grSocket\b/.graphics_socket/g' \
  -e 's/\.grScene\b/.graphics_scene/g' \
  {} +
```

### Step 2.2: Rename attribute definitions (Day 3 afternoon)

1. In `node_editor/core/node.py`:
   - `self.grNode` → `self.graphics_node`
   
2. In `node_editor/core/edge.py`:
   - `self.grEdge` → `self.graphics_edge`
   
3. In `node_editor/core/socket.py`:
   - `self.grSocket` → `self.graphics_socket`

4. In `node_editor/core/scene.py`:
   - `self.grScene` → `self.graphics_scene`

### Step 2.3: Update all usage (Days 4-5)

1. Run rename script on codebase
2. Manual review of:
   - All `node_editor/core/` files
   - All `node_editor/graphics/` files
   - All `node_editor/widgets/` files
   - All `node_editor/nodes/` files
   - Examples and tests

3. Update docstrings and comments

### Testing
- ✓ Run `pytest` after each subsystem change
- ✓ Run `ruff check .`
- ✓ Test serialization compatibility
- ✓ Run all examples manually

### Commit (one per subsystem)
```bash
git commit -m "Rename graphics attributes to snake_case in core/ (BREAKING)"
git commit -m "Rename graphics attributes to snake_case in graphics/ (BREAKING)"
git commit -m "Rename graphics attributes to snake_case in widgets/ (BREAKING)"
git commit -m "Rename graphics attributes to snake_case in nodes/ (BREAKING)"
git commit -m "Rename graphics attributes to snake_case in tests/examples (BREAKING)"
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

### Testi3: Update Graphics Class Names (Day 6)

**Target**: `GraphicsNode_class` → `_graphics_node_class`  
**Files**: `node_editor/core/__init__.py` and custom node classes  
**Impact**: Medium - affects subclassing

### Tasks

1. In `node_editor/core/__init__.py`:
   - Rename all `GraphicsNode_class` → `_graphics_node_class`
   - Rename `GraphicsEdge_class` → `_graphics_edge_class`
   - Rename `GraphicsSocket_class` → `_graphics_socket_class`

2. Update all built-in nodes that override these

### Testing
- ✓ Test custom node classes
- ✓ Verify subclassing works
- ✓ Run full test suite

### Commit
```bash
git commit -m "Rename Graphics*_class to snake_case (BREAKING)"
```

---

## Phase 4: Update Documentation (Day 7)

**Goal**: Ensure all documentation reflects new naming

### Tasks
1. Update `README.md` code examples
2. Update `docs/architecture.md` references
3. Update all docstring examples in code
4. Update `examples/` if any manual changes needed

### Testing
- ✓ Run all examples
- ✓ Build docs (if applicable)
- ✓ Search for any remaining old names

### Commit
```bash
git commit -m "Update all documentation to reflect PEP8 naming"
```

---

## Phase 5: Release v2.0.0 (Day 8)

**Goal**: Ship breaking changes with clear migration notes

### Tasks
1. Update `__version__` to `2.0.0`
2. Update `CHANGES.rst`:
   ```
   Version 2.0.0 (2025-XX-XX)
   --------------------------
   
   BREAKING CHANGES:
   - Renamed all methods to snake_case:
     * markDirty → mark_dirty
     * markInvalid → mark_invalid
     * markDescendantsDirty → mark_descendants_dirty
     * markDescendantsInvalid → mark_descendants_invalid
   
   - Renamed all graphics attributes:
     * grNode → graphics_node
     * grEdge → graphics_edge
     * grSocket → graphics_socket
     * grScene → graphics_scene
   
   - Renamed internal class attributes:
     * GraphicsNode_class → _graphics_node_class
     * GraphicsEdge_class → _graphics_edge_class
     * GraphicsSocket_class → _graphics_socket_class
   
   Migration: Use provided sed scripts in scripts/ to update your code.
   ```

3. Tag release: `git tag v2.0.0`
4. Create GitHub release with migration guide

### User Migration Script

Provide `scripts/migrate_to_v2.sh`:
```bash
#!/bin/bash
# Migrate downstream code to v2.0.0 naming

echo "Migrating to node_editor v2.0.0 naming conventions..."

# Methods
find . -name "*.py" -exec sed -i \
  -e 's/\.markDirty(/.mark_dirty(/g' \
  -e 's/\.markInvalid(/.mark_invalid(/g' \
  -e 's/\.markDescendantsDirty(/.mark_descendants_dirty(/g' \
  -e 's/\.markDescendantsInvalid(/.mark_descendants_invalid(/g' \
  {} +

# Attributes  
find . -name "*.py" -exec sed -i \
  -e 's/\.grNode\b/.graphics_node/g' \
  -e 's/\.grEdge\b/.graphics_edge/g' \
  -e 's/\.grSocket\b/.graphics_socket/g' \
  -e 's/\.grScene\b/.graphics_scene/g' \
  {} +

# Class attributes (for custom nodes)
find . -name "*.py" -exec sed -i \
  -e 's/GraphicsNode_class/_graphics_node_class/g' \
  -e 's/GraphicsEdge_class/_graphics_edge_class/g' \
  -e 's/GraphicsSocket_class/_graphics_socket_class/g' \
  {} +

echo "Migration complete! Run tests to verify."
```

### Testing
- ✓ Full test suite passes
- ✓ Examples work
- ✓ PDuring renaming**: Revert the specific commit
2. **After testing fails**: Fix the issue or revert
3. **After release**: Must issue patch release with fixes

Each phase is small enough to revert easily. Test thoroughly before proceeding.

---

## Testing Checklist (Every Phase)

- [ ] Run `pytest` - all 328 tests pass
- [ ] Run `ruff check .` - no new linting errors
- [ ] Run examples manually
- [ ] Check serialization format unchanged
- [ ] Visual inspection of git diff for unintended changes

---

## Success Criteria

✅ **Phase complete when**:
- All tests pass
- No ruff/mypy errors
- Examples work correctly
- Documentation updated
- Clean git diff (no unintended changes)
- Commit pushed with clear BREAKING message

✅ **Migration successful when**:
- Clean PEP8 naming throughout
- All 328 tests passing
- Examples working
- v2.0.0 released with migration script

---

## Timeline Summary

| Phase | Duration | Cumulative |
|-------|----------|------------|
| 1. State methods | 2 days | Day 2 |
| 2. Graphics attrs | 3 days | Day 5 |
| 3. Class names | 1 day | Day 6 |
| 4. Documentation | 1 day | Day 7 |
| 5. Release v2.0.0 | 1 day | Day 8 |
| **Total** | **8 days** | **~2 weeks** |

**Buffer**: Add 1-2 weeks for thorough testing and fixing any issues.

---

## Pre-Migration Checklist

Before starting Phase 1:

- [ ] Create feature branch: `git checkout -b feature/pep8-naming`
- [ ] Ensure all tests pass on main: `pytest`
- [ ] Ensure clean working directory: `git status`
- [ ] Back up current state: `git tag pre-pep8-rename`
- [ ] Communicate breaking changes to users (GitHub issue)

---

## Post-Migration Checklist

After completing Phase 5:

- [ ] All 328 tests passing
- [ ] Examples work correctly
- [ ] Documentation updated and accurate
- [ ] `CHANGES.rst` includes migration notes
- [ ] Migration script tested
- [ ] GitHub release created with notes
- [ ] Tag pushed: `git push origin v2.0.0`

---

**Next Steps**:
1. Create feature branch
2. Start with Phase 1 (state methods)
3. Test thoroughly after each commit
4. Proceed to next phase only when tests pass

**Important**: This is a breaking change. Communicate clearly to users before releasing v2.0.0