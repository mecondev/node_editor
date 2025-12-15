"""Guard test ensuring node_editor.core has no runtime Qt dependencies.

This test enforces the architectural constraint that core domain classes
(Scene, Node, Edge, Socket, Serializable) remain independent of Qt at
runtime, allowing TYPE_CHECKING imports only.

Author:
    Michael Economou

Date:
    2025-12-15
"""

import ast
from pathlib import Path


def test_core_has_no_runtime_qt_imports():
    """Verify core modules only import Qt in TYPE_CHECKING blocks.

    Parses all files in node_editor/core/ and ensures Qt imports
    are guarded behind TYPE_CHECKING to prevent runtime dependencies.
    """
    core_dir = Path(__file__).parent.parent / "node_editor" / "core"
    assert core_dir.exists(), f"Core directory not found: {core_dir}"

    violations = []

    for py_file in core_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        with open(py_file, encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError as e:
            violations.append(f"{py_file.name}: Syntax error - {e}")
            continue

        # Track TYPE_CHECKING context
        in_type_checking = False

        for node in ast.walk(tree):
            # Detect TYPE_CHECKING guard
            if isinstance(node, ast.If):
                test = node.test
                if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
                    in_type_checking = True
                elif isinstance(test, ast.Attribute):
                    # Handle typing.TYPE_CHECKING
                    if (
                        isinstance(test.value, ast.Name)
                        and test.value.id == "typing"
                        and test.attr == "TYPE_CHECKING"
                    ):
                        in_type_checking = True

            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Get module name
                module = ""
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                elif isinstance(node, ast.Import):
                    module = node.names[0].name if node.names else ""

                # Check if Qt-related
                is_qt = any(
                    qt_lib in module
                    for qt_lib in ["PyQt5", "PyQt6", "PySide2", "PySide6", "qtpy"]
                )

                if is_qt:
                    # Find line number
                    lineno = getattr(node, "lineno", "?")

                    # Check if inside TYPE_CHECKING block
                    if not in_type_checking:
                        violations.append(
                            f"{py_file.name}:{lineno} - Runtime Qt import: {module}"
                        )

    assert not violations, (
        "Core layer has runtime Qt dependencies:\n" + "\n".join(violations)
    )


if __name__ == "__main__":
    test_core_has_no_runtime_qt_imports()
    print("✅ All core modules are Qt-free at runtime")
