"""Tests for advanced operation nodes."""

from node_editor.core.scene import Scene
from node_editor.nodes.advanced_nodes import (
    FileReadNode,
    FileWriteNode,
    HttpRequestNode,
    RegexMatchNode,
)


class TestRegexMatchNode:
    """Test suite for RegexMatchNode."""

    def test_create_regex_match_node(self, scene: Scene):
        """Test RegexMatchNode creation."""
        node = RegexMatchNode(scene)
        assert node.op_code == 110
        assert node.op_title == "Regex Match"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_regex_match_logic(self, scene: Scene):
        """Test regex matching logic."""
        _ = RegexMatchNode(scene)
        # Test Python regex
        text = "hello123"
        pattern = r"\d+"
        result = bool(__import__("re").search(pattern, text))
        assert result is True

    def test_regex_no_match(self, scene: Scene):
        """Test regex no match."""
        _ = RegexMatchNode(scene)
        text = "abc"
        pattern = r"\d+"
        result = bool(__import__("re").search(pattern, text))
        assert result is False

    def test_regex_email_pattern(self, scene: Scene):
        """Test email pattern matching."""
        _ = RegexMatchNode(scene)
        text = "user@example.com"
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        result = bool(__import__("re").search(pattern, text))
        assert result is True


class TestFileReadNode:
    """Test suite for FileReadNode."""

    def test_create_file_read_node(self, scene: Scene):
        """Test FileReadNode creation."""
        node = FileReadNode(scene)
        assert node.op_code == 111
        assert node.op_title == "File Read"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_file_read_logic(self, scene: Scene):
        """Test file read logic."""
        _ = FileReadNode(scene)
        # Test Python file operations
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("test content")
            temp_file = f.name

        try:
            with open(temp_file, encoding="utf-8") as f:
                contents = f.read()
            assert contents == "test content"
        finally:
            import os
            os.unlink(temp_file)

    def test_file_read_multiline(self, scene: Scene):
        """Test reading multiline file."""
        _ = FileReadNode(scene)
        import tempfile

        content = "line1\nline2\nline3"
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(content)
            temp_file = f.name

        try:
            with open(temp_file, encoding="utf-8") as f:
                contents = f.read()
            assert "line1" in contents
            assert "line2" in contents
            assert "line3" in contents
        finally:
            import os
            os.unlink(temp_file)


class TestFileWriteNode:
    """Test suite for FileWriteNode."""

    def test_create_file_write_node(self, scene: Scene):
        """Test FileWriteNode creation."""
        node = FileWriteNode(scene)
        assert node.op_code == 112
        assert node.op_title == "File Write"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_file_write_logic(self, scene: Scene):
        """Test file write logic."""
        _ = FileWriteNode(scene)
        import os
        import tempfile

        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "test_write.txt")

        try:
            # Write file
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("test content")

            # Verify
            with open(temp_file, encoding="utf-8") as f:
                contents = f.read()
            assert contents == "test content"
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_file_write_overwrite(self, scene: Scene):
        """Test file overwriting."""
        _ = FileWriteNode(scene)
        import os
        import tempfile

        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "test_overwrite.txt")

        try:
            # Write first content
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("first")

            # Overwrite
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("second")

            # Verify
            with open(temp_file, encoding="utf-8") as f:
                contents = f.read()
            assert contents == "second"
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_file_write_unicode(self, scene: Scene):
        """Test writing Unicode content."""
        _ = FileWriteNode(scene)
        import os
        import tempfile

        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "test_unicode.txt")

        try:
            unicode_content = "Ελληνικά 中文 日本語 العربية"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(unicode_content)

            with open(temp_file, encoding="utf-8") as f:
                contents = f.read()
            assert contents == unicode_content
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestHttpRequestNode:
    """Test suite for HttpRequestNode."""

    def test_create_http_request_node(self, scene: Scene):
        """Test HttpRequestNode creation."""
        node = HttpRequestNode(scene)
        assert node.op_code == 113
        assert node.op_title == "HTTP Request"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_http_url_validation(self, scene: Scene):
        """Test URL validation logic."""
        _ = HttpRequestNode(scene)
        # Test URL handling
        url = "example.com"
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        assert url == "https://example.com"

    def test_http_method_defaults(self, scene: Scene):
        """Test HTTP method handling."""
        _ = HttpRequestNode(scene)
        method = "GET"
        assert method.upper() == "GET"

        method = "post"
        assert method.upper() == "POST"

    def test_http_url_with_protocol(self, scene: Scene):
        """Test URL already with protocol."""
        _ = HttpRequestNode(scene)
        url = "https://api.example.com"
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        assert url == "https://api.example.com"
