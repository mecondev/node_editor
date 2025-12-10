<!-- GitHub Copilot / AI agent instructions for this repository -->

# node_editor — AI assistant guidelines

These instructions help AI coding agents work productively and safely in this repository.

## Quick context

- **Project:** PyQt Node Editor — A Python framework for creating node-based visual programming interfaces using PyQt5/PyQt6/PySide2/PySide6.
- **Main focus:** Provide a reusable, customizable node editor with support for nodes, edges, sockets, undo/redo, serialization, and evaluation logic.

When in doubt, prefer a **stable, extendable** solution over a "clever" one.

---

## Communication & style conventions

- **Human-facing explanations:** Greek. Keep the tone friendly and clear.
- **Code, comments, docstrings, log messages, UI text:** English.
- Communicate with the user in Greek.
- All code-related output (commit messages, comments, docstrings, variables, filenames, documentation) must be in English.

- Always:
  - Add **module-level docstrings** when missing.
  - Add **type annotations** to new functions and methods.
  - Keep **existing loggers, docstrings and comments**; do not delete or drastically restructure code unless the user explicitly asks.
  - **Use only ASCII characters** in code, comments, log messages, and docstrings.

Do **not** fix linting issues (ruff/mypy) unless the user requests it. The repo is configured with strict mypy and ruff/black in `pyproject.toml`.

---

## Architecture map (where to look first)

Read these files in this order when understanding behavior:

1. `nodeeditor/__init__.py` — package initialization, Qt API detection.
2. `nodeeditor/node_editor_window.py` — main window implementation with menus and file operations.
3. `nodeeditor/node_editor_widget.py` — core widget containing the graphics view and scene.

Core components (in `nodeeditor/`):

- `node_scene.py` — Scene management, node/edge container, serialization.
- `node_node.py` — Node implementation with sockets, content, and graphics.
- `node_edge.py` — Edge implementation connecting sockets.
- `node_socket.py` — Socket implementation for node connections.
- `node_graphics_view.py` — Custom QGraphicsView with zoom, pan, and interaction.
- `node_graphics_scene.py` — Custom QGraphicsScene with grid background.
- `node_graphics_node.py` — Visual representation of nodes.
- `node_graphics_edge.py` — Visual representation of edges.
- `node_graphics_socket.py` — Visual representation of sockets.

Utility modules:

- `node_scene_clipboard.py` — Copy/paste functionality.
- `node_scene_history.py` — Undo/redo system.
- `node_serializable.py` — Base class for serialization.
- `node_edge_validators.py` — Edge validation logic.
- `node_edge_dragging.py` — Edge dragging behavior.
- `node_content_widget.py` — Base class for node content widgets.

For examples, see `examples/` directory.

---

## Developer workflows

Preferred commands (Python 3.8+):

- Install runtime deps:
  - `pip install -r requirements.txt`
- Install dev deps:
  - `pip install -e ".[dev]"`
- Run the app examples:
  - `python examples/example_calculator/main.py`
- Run tests:
  - `pytest` or `pytest tests -q`

---

## Patterns to follow

When modifying or adding node-related logic:

- Keep node components **modular and reusable**:
  - Nodes should be subclassable for custom behavior.
  - Sockets define connection points and types.
  - Edges handle connections between sockets.
- Respect the graphics/model separation:
  - `node_*.py` files contain logic/model.
  - `node_graphics_*.py` files contain visual representation.
- Use the serialization system for save/load.
- Use the history system for undo/redo.

When working on the UI:

- Let the graphics classes handle visual behavior.
- Keep business logic in the model classes.
- Use signals/slots for communication between components.

---

## Safety rules for AI agents

- **Do not run git commands** (commit, pull, push, reset, clean) without explicit user approval.
- For **multi-file or high-impact changes**:
  - First present a **short, structured plan** (bulleted list of files and changes).
  - Wait for user confirmation before applying edits.
- Never remove or significantly restructure logging, docstrings, or comments unless the user asks.
- When unsure which class or module to extend, propose options and ask the user which direction fits their existing architecture.

If anything is ambiguous, ask the user in Greek which behavior they prefer before proceeding.
