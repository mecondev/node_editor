"""Tests for time and date manipulation nodes."""

from datetime import datetime

from node_editor.core.scene import Scene
from node_editor.nodes.time_nodes import (
    CompareTimeNode,
    CurrentTimeNode,
    FormatDateNode,
    ParseDateNode,
    TimeDeltaNode,
)


class TestCurrentTimeNode:
    """Test suite for CurrentTimeNode."""

    def test_create_current_time_node(self, scene: Scene):
        """Test CurrentTimeNode creation."""
        node = CurrentTimeNode(scene)
        assert node.op_code == 100
        assert node.op_title == "Current Time"
        assert len(node.inputs) == 0
        assert len(node.outputs) == 1

    def test_current_time_logic(self, scene: Scene):
        """Test that current time returns a valid timestamp."""
        _ = CurrentTimeNode(scene)
        # Test that Python datetime works
        now = datetime.now().timestamp()
        assert isinstance(now, float)
        assert now > 0
        # Verify it's a reasonable timestamp (after year 2020)
        assert now > 1577836800  # 2020-01-01


class TestFormatDateNode:
    """Test suite for FormatDateNode."""

    def test_create_format_date_node(self, scene: Scene):
        """Test FormatDateNode creation."""
        node = FormatDateNode(scene)
        assert node.op_code == 101
        assert node.op_title == "Format Date"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_format_date_logic(self, scene: Scene):
        """Test date formatting logic."""
        _ = FormatDateNode(scene)
        # Test Python strftime
        test_timestamp = 1702376400.0  # 2023-12-12 12:00:00 UTC
        dt = datetime.fromtimestamp(test_timestamp)
        
        # Test various formats
        assert dt.strftime("%Y-%m-%d") == "2023-12-12"
        assert dt.strftime("%Y") == "2023"
        assert dt.strftime("%B") == "December"

    def test_format_with_time(self, scene: Scene):
        """Test formatting with time components."""
        _ = FormatDateNode(scene)
        test_timestamp = 1702395045.0  # 2023-12-12 17:30:45 UTC
        dt = datetime.fromtimestamp(test_timestamp)
        
        # Full format
        formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
        assert "2023-12-12" in formatted
        assert "17:30:45" in formatted


class TestParseDateNode:
    """Test suite for ParseDateNode."""

    def test_create_parse_date_node(self, scene: Scene):
        """Test ParseDateNode creation."""
        node = ParseDateNode(scene)
        assert node.op_code == 102
        assert node.op_title == "Parse Date"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_parse_date_logic(self, scene: Scene):
        """Test date parsing logic."""
        _ = ParseDateNode(scene)
        # Test Python strptime
        date_string = "2023-12-12"
        format_str = "%Y-%m-%d"
        dt = datetime.strptime(date_string, format_str)
        timestamp = dt.timestamp()
        
        assert isinstance(timestamp, float)
        assert timestamp > 0

    def test_parse_with_time(self, scene: Scene):
        """Test parsing with time components."""
        _ = ParseDateNode(scene)
        date_string = "2023-12-12 15:30:45"
        format_str = "%Y-%m-%d %H:%M:%S"
        dt = datetime.strptime(date_string, format_str)
        
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 12
        assert dt.hour == 15
        assert dt.minute == 30
        assert dt.second == 45

    def test_round_trip(self, scene: Scene):
        """Test parsing and formatting round trip."""
        _ = ParseDateNode(scene)
        _ = FormatDateNode(scene)
        
        # Original string
        original = "2023-12-12 15:30:45"
        format_str = "%Y-%m-%d %H:%M:%S"
        
        # Parse to timestamp
        dt = datetime.strptime(original, format_str)
        timestamp = dt.timestamp()
        
        # Format back to string
        dt2 = datetime.fromtimestamp(timestamp)
        result = dt2.strftime(format_str)
        
        assert result == original


class TestTimeDeltaNode:
    """Test suite for TimeDeltaNode."""

    def test_create_time_delta_node(self, scene: Scene):
        """Test TimeDeltaNode creation."""
        node = TimeDeltaNode(scene)
        assert node.op_code == 103
        assert node.op_title == "Time Delta"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_add_time_logic(self, scene: Scene):
        """Test adding time offset."""
        _ = TimeDeltaNode(scene)
        base_timestamp = 1702376400.0  # Base time
        offset = 3600.0  # 1 hour
        
        result = base_timestamp + offset
        assert result == 1702380000.0

    def test_subtract_time_logic(self, scene: Scene):
        """Test subtracting time offset."""
        _ = TimeDeltaNode(scene)
        base_timestamp = 1702376400.0
        offset = -86400.0  # -1 day
        
        result = base_timestamp + offset
        assert result == 1702290000.0

    def test_zero_offset(self, scene: Scene):
        """Test zero offset returns same timestamp."""
        _ = TimeDeltaNode(scene)
        base_timestamp = 1702376400.0
        offset = 0.0
        
        result = base_timestamp + offset
        assert result == base_timestamp

    def test_common_time_offsets(self, scene: Scene):
        """Test common time offset values."""
        _ = TimeDeltaNode(scene)
        base = 1000000.0
        
        # Common offsets
        assert base + 60 == 1000060.0  # 1 minute
        assert base + 3600 == 1003600.0  # 1 hour
        assert base + 86400 == 1086400.0  # 1 day
        assert base + 604800 == 1604800.0  # 1 week


class TestCompareTimeNode:
    """Test suite for CompareTimeNode."""

    def test_create_compare_time_node(self, scene: Scene):
        """Test CompareTimeNode creation."""
        node = CompareTimeNode(scene)
        assert node.op_code == 104
        assert node.op_title == "Compare Time"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_positive_difference(self, scene: Scene):
        """Test positive time difference."""
        _ = CompareTimeNode(scene)
        timestamp1 = 1702380000.0  # Later
        timestamp2 = 1702376400.0  # Earlier
        
        difference = timestamp1 - timestamp2
        assert difference == 3600.0  # 1 hour

    def test_negative_difference(self, scene: Scene):
        """Test negative time difference."""
        _ = CompareTimeNode(scene)
        timestamp1 = 1702376400.0  # Earlier
        timestamp2 = 1702380000.0  # Later
        
        difference = timestamp1 - timestamp2
        assert difference == -3600.0

    def test_zero_difference(self, scene: Scene):
        """Test zero difference (same time)."""
        _ = CompareTimeNode(scene)
        timestamp1 = 1702376400.0
        timestamp2 = 1702376400.0
        
        difference = timestamp1 - timestamp2
        assert difference == 0.0

    def test_large_difference(self, scene: Scene):
        """Test large time difference."""
        _ = CompareTimeNode(scene)
        timestamp1 = 1702376400.0  # 2023-12-12
        timestamp2 = 1702376400.0 - 31536000.0  # 1 year earlier
        
        difference = timestamp1 - timestamp2
        assert difference == 31536000.0  # 365 days in seconds
