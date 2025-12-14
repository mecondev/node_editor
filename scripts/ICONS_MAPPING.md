# Node Editor Icons Mapping

This document maps Material Design icons to Node Editor nodes across all examples.

**Source**: `/mnt/data_1/edu/Tools/Google_material_design_icons/outlined`

**Total Icons Selected**: 77

---

## 🔌 Common Icons (Input/Output)

| Icon File | Node Type | Description |
|-----------|-----------|-------------|
| `input.svg` | Input Node | Generic input node |
| `output.svg` | Output Node | Generic output node |
| `login.svg` | Input Node | Alternative input icon |
| `logout.svg` | Output Node | Alternative output icon |

---

## 🔢 Calculator / Math Nodes

| Icon File | Node Type | Description | Op Code |
|-----------|-----------|-------------|---------|
| `add.svg` | Add | Addition (+) | 10 |
| `remove.svg` | Subtract | Subtraction (-) | 11 |
| `close.svg` | Multiply | Multiplication (×) | 12 |
| `more_horiz.svg` | Divide | Division (÷) | 13 |
| `percent.svg` | Percentage | Percentage (%) | NEW |
| `calculate.svg` | Calculator | General calculator | - |
| `functions.svg` | Functions | Math functions | - |
| `exposure_plus_1.svg` | Power | Exponentiation (^) | 50 |
| `square_foot.svg` | Square Root | Square root (√) | 51 |
| `vertical_align_center.svg` | Absolute | Absolute value \|x\| | 52 |
| `unfold_less.svg` | Minimum | Minimum of two values | 53 |
| `unfold_more.svg` | Maximum | Maximum of two values | 54 |
| `360.svg` | Round | Round number | 55 |
| `grid_3x3.svg` | Modulo | Modulo operation (mod) | 56 |

---

## 📝 String Processing Nodes

| Icon File | Node Type | Description | Op Code |
|-----------|-----------|-------------|---------|
| `text_fields.svg` | Text Input | Text input field | 201 |
| `output.svg` | Text Output | Text output display | 202 |
| `link.svg` | Concatenate | Join strings (++) | 203 |
| `data_object.svg` | Format | Format string {} | 204 |
| `tag.svg` | Length | String length (#) | 205 |
| `content_cut.svg` | Substring | Extract substring | 206 |
| `call_split.svg` | Split | Split string to list | 207 |
| `uppercase.svg` | Uppercase | Convert to UPPERCASE | - |
| `lowercase.svg` | Lowercase | Convert to lowercase | - |
| `horizontal_rule.svg` | Trim | Trim whitespace | - |
| `find_replace.svg` | Replace | Find and replace | - |
| `start.svg` | StartsWith | Check string prefix | - |
| `keyboard_tab.svg` | EndsWith | Check string suffix | - |

---

## 🔀 Logic / Comparison Nodes

| Icon File | Node Type | Description | Op Code |
|-----------|-----------|-------------|---------|
| `123.svg` | Number Input | Number input field | 221 |
| `check_box.svg` | Bool Input | Boolean input | 222 |
| `toggle_on.svg` | Bool Output | Boolean output | 223 |
| `drag_handle.svg` | Equal | Equality (==) | 224 |
| `code.svg` | Not Equal | Inequality (!=) | 225 |
| `chevron_left.svg` | Less Than | Less than (<) | 226 |
| `keyboard_double_arrow_left.svg` | Less or Equal | Less or equal (<=) | 227 |
| `chevron_right.svg` | Greater Than | Greater than (>) | 228 |
| `keyboard_double_arrow_right.svg` | Greater or Equal | Greater or equal (>=) | 229 |
| `join_inner.svg` | AND | Logical AND (&&) | 230 |
| `join_full.svg` | OR | Logical OR (\|\|) | 231 |
| `block.svg` | NOT | Logical NOT (!) | 232 |
| `difference.svg` | XOR | Logical XOR (^) | 233 |
| `question_mark.svg` | If/Switch | Conditional (?:) | 234 |

---

## 🔄 Type Conversion Nodes

| Icon File | Node Type | Description | Op Code |
|-----------|-----------|-------------|---------|
| `abc.svg` | To String | Convert to string | 244 |
| `123.svg` | To Number | Convert to float | 245 |
| `toggle_on.svg` | To Bool | Convert to boolean | 246 |
| `pin.svg` | To Int | Convert to integer | 247 |
| `swap_horiz.svg` | Convert | Generic converter | - |
| `transform.svg` | Transform | Alternative icon | - |

---

## 📋 List Manipulation Nodes

| Icon File | Node Type | Description | Op Code |
|-----------|-----------|-------------|---------|
| `data_array.svg` | Create List | Create list [ ] | 253 |
| `filter_1.svg` | Get Item | Get item [i] | 254 |
| `tag.svg` | List Length | List length #[] | 255 |
| `playlist_add.svg` | Append | Append to list | 256 |
| `merge.svg` | Join | Join list → string | 257 |
| `view_list.svg` | List View | Alternative icon | - |
| `reorder.svg` | Reorder | Alternative icon | - |

---

## 🛠️ Utility Nodes

| Icon File | Node Type | Description | Op Code |
|-----------|-----------|-------------|---------|
| `looks_one.svg` | Constant | Constant value (C) | 263 |
| `print.svg` | Print | Print to console | 264 |
| `comment.svg` | Comment | Comment node (//) | 265 |
| `compress.svg` | Clamp | Clamp min/max | 266 |
| `casino.svg` | Random | Random number | 267 |
| `tune.svg` | Settings | Alternative icon | - |
| `build.svg` | Tool | Alternative icon | - |

---

## ⏰ Time / Date Nodes

| Icon File | Node Type | Description | Op Code |
|-----------|-----------|-------------|---------|
| `schedule.svg` | Current Time | Current timestamp | 274 |
| `event.svg` | Format Date | Format timestamp | 275 |
| `date_range.svg` | Parse Date | Parse date string | 276 |
| `update.svg` | Time Delta | Add/subtract time | 277 |
| `compare_arrows.svg` | Compare Time | Compare timestamps | 278 |
| `alarm.svg` | Alarm | Alternative icon | - |
| `calendar_today.svg` | Calendar | Alternative icon | - |
| `history.svg` | History | Alternative icon | - |
| `av_timer.svg` | Timer | Alternative icon | - |

---

## 🚀 Advanced Nodes

| Icon File | Node Type | Description | Op Code |
|-----------|-----------|-------------|---------|
| `manage_search.svg` | Regex Match | Pattern matching (.*) | 284 |
| `description.svg` | File Read | Read file contents | 285 |
| `save.svg` | File Write | Write to file | 286 |
| `http.svg` | HTTP Request | HTTP GET request | 287 |
| `cloud_download.svg` | Download | Alternative icon | - |
| `cloud_upload.svg` | Upload | Alternative icon | - |
| `public.svg` | Web | Alternative icon | - |
| `api.svg` | API | Alternative icon | - |

---

## 📊 Summary by Category

| Category | Primary Icons | Alternative Icons | Total |
|----------|---------------|-------------------|-------|
| Common | 2 | 2 | 4 |
| Math | 14 | 0 | 14 |
| String | 7 | 6 | 13 |
| Logic | 14 | 0 | 14 |
| Conversion | 4 | 2 | 6 |
| List | 5 | 2 | 7 |
| Utility | 5 | 2 | 7 |
| Time | 5 | 4 | 9 |
| Advanced | 4 | 4 | 8 |
| **TOTAL** | **60** | **22** | **82** |

---

## 🎨 Icon Conversion Guide

### From SVG to PNG (32x32)

To convert icons for use in examples:

```bash
# Single icon
inkscape --export-type=png --export-width=32 --export-height=32 \
  /path/to/icon.svg -o output.png

# Batch convert
for icon in *.svg; do
  inkscape --export-type=png --export-width=32 --export-height=32 \
    "$icon" -o "${icon%.svg}.png"
done
```

### Alternative: Using ImageMagick

```bash
convert -background none -resize 32x32 input.svg output.png
```

---

## 📝 Notes

1. **Primary icons** are the main icons used for each node type
2. **Alternative icons** are provided as options for variation
3. Some icons are reused across categories (e.g., `123.svg`, `toggle_on.svg`)
4. All icons are from Material Design Outlined set
5. Icons should be converted to PNG format (32x32) for use in examples

---

## 🔄 Changes from Initial Plan

| Node | Old Icon | New Icon | Reason |
|------|----------|----------|--------|
| Divide | `percent.svg` | `more_horiz.svg` | Reserved percent for Percentage node |
| Modulo | `grid_3x3.svg` (%) | `grid_3x3.svg` (mod) | Clarified label |

---

**Last Updated**: 2025-12-14  
**Author**: Michael Economou
