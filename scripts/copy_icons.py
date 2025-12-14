#!/usr/bin/env python3
"""Copy Material Design icons (SVG) to example folders.

This script copies SVG icons from Material Design to example folders.
SVG format is used for dynamic coloring and better quality.

Usage:
    python scripts/copy_icons.py

Author: Michael Economou
Date: 2025-12-14
"""

import shutil
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ICONS_SOURCE = Path("/mnt/data_1/edu/Tools/Google_material_design_icons/outlined")
EXAMPLES_DIR = PROJECT_ROOT / "examples"

# Icon mappings per example (output_name: source_svg)
ICON_MAPPINGS = {
    "calculator": {
        "in.svg": "input.svg",
        "out.svg": "output.svg",
        "add.svg": "add.svg",
        "sub.svg": "remove.svg",
        "mul.svg": "close.svg",
        "divide.svg": "more_horiz.svg",
        "percent.svg": "percent.svg",
        "power.svg": "exposure_plus_1.svg",
        "sqrt.svg": "square_foot.svg",
        "abs.svg": "vertical_align_center.svg",
        "min.svg": "unfold_less.svg",
        "max.svg": "unfold_more.svg",
        "round.svg": "360.svg",
        "mod.svg": "grid_3x3.svg",
    },
    "string_processor": {
        "text_in.svg": "text_fields.svg",
        "text_out.svg": "output.svg",
        "concat.svg": "link.svg",
        "format.svg": "data_object.svg",
        "length.svg": "tag.svg",
        "substring.svg": "content_cut.svg",
        "split.svg": "call_split.svg",
        "uppercase.svg": "uppercase.svg",
        "lowercase.svg": "lowercase.svg",
        "trim.svg": "horizontal_rule.svg",
        "replace.svg": "find_replace.svg",
        "starts.svg": "start.svg",
        "ends.svg": "keyboard_tab.svg",
    },
    "logic_builder": {
        "num_in.svg": "123.svg",
        "bool_in.svg": "check_box.svg",
        "bool_out.svg": "toggle_on.svg",
        "equal.svg": "drag_handle.svg",
        "not_equal.svg": "code.svg",
        "less.svg": "chevron_left.svg",
        "less_eq.svg": "keyboard_double_arrow_left.svg",
        "greater.svg": "chevron_right.svg",
        "greater_eq.svg": "keyboard_double_arrow_right.svg",
        "and.svg": "join_inner.svg",
        "or.svg": "join_full.svg",
        "not.svg": "block.svg",
        "xor.svg": "difference.svg",
        "if.svg": "question_mark.svg",
    },
    "type_converter": {
        "input.svg": "text_fields.svg",
        "output.svg": "output.svg",
        "to_string.svg": "abc.svg",
        "to_number.svg": "123.svg",
        "to_bool.svg": "toggle_on.svg",
        "to_int.svg": "pin.svg",
        "convert.svg": "swap_horiz.svg",
    },
    "list_manager": {
        "value_in.svg": "input.svg",
        "list_out.svg": "output.svg",
        "create_list.svg": "data_array.svg",
        "get_item.svg": "filter_1.svg",
        "length.svg": "tag.svg",
        "append.svg": "playlist_add.svg",
        "join.svg": "merge.svg",
        "list.svg": "view_list.svg",
    },
    "utility_toolbox": {
        "num_in.svg": "123.svg",
        "output.svg": "output.svg",
        "constant.svg": "looks_one.svg",
        "print.svg": "print.svg",
        "comment.svg": "comment.svg",
        "clamp.svg": "compress.svg",
        "random.svg": "casino.svg",
    },
    "time_tools": {
        "text_in.svg": "text_fields.svg",
        "num_in.svg": "123.svg",
        "output.svg": "output.svg",
        "time_now.svg": "schedule.svg",
        "format_date.svg": "event.svg",
        "parse_date.svg": "date_range.svg",
        "time_delta.svg": "update.svg",
        "compare_time.svg": "compare_arrows.svg",
    },
    "advanced_toolkit": {
        "text_in.svg": "text_fields.svg",
        "path_in.svg": "description.svg",
        "output.svg": "output.svg",
        "regex.svg": "manage_search.svg",
        "file_read.svg": "description.svg",
        "file_write.svg": "save.svg",
        "http.svg": "http.svg",
    },
}


def copy_and_rename_icons():
    """Copy and rename SVG icons to example folders."""
    print("=" * 70)
    print("Copying Material Design SVG icons to examples")
    print("=" * 70)
    print()

    total_copied = 0
    total_missing = 0

    for example_name, mappings in ICON_MAPPINGS.items():
        print(f"📁 {example_name}")
        print("-" * 70)

        # Create icons directory
        icons_dir = EXAMPLES_DIR / example_name / "icons"
        icons_dir.mkdir(parents=True, exist_ok=True)

        copied = 0
        missing = 0

        for dest_name, src_name in mappings.items():
            src_path = ICONS_SOURCE / src_name
            dest_path = icons_dir / dest_name

            # Check if source exists
            if not src_path.exists():
                print(f"  ❌ Missing: {src_name}")
                missing += 1
                total_missing += 1
                continue

            # Copy
            try:
                shutil.copy2(src_path, dest_path)
                print(f"  ✅ {dest_name} ← {src_name}")
                copied += 1
                total_copied += 1
            except Exception as e:
                print(f"  ⚠️  Error copying {src_name}: {e}")

        print(f"  → Copied: {copied}, Missing: {missing}")
        print()

    print("=" * 70)
    print("✨ Summary:")
    print(f"   Total copied: {total_copied}")
    print(f"   Total missing: {total_missing}")
    print("=" * 70)
    print()
    print("📝 Note: SVG icons support dynamic coloring via Qt stylesheets.")
    print("   No need for separate light/dark versions!")



def main():
    """Main entry point."""
    # Check if source directory exists
    if not ICONS_SOURCE.exists():
        print(f"Error: Source directory not found: {ICONS_SOURCE}")
        sys.exit(1)

    copy_and_rename_icons()


if __name__ == "__main__":
    main()
