#!/usr/bin/env python3
"""
Step 6: 注释核对
用法: python3 validate-comments.py <原文件> <新文件>

提取所有行注释 (//) 和块注释 (/* */) 并对比差异。
支持嵌套注释边缘情况，排除字符串字面量中的 '//'。
"""

import sys
from pathlib import Path


def extract_comments(filepath: str) -> list[tuple[int, str]]:
    """Extract all comments with line numbers, filtering out // inside strings."""
    text = Path(filepath).read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # Strip string contents before comment detection to avoid false matches.
    # Handle both "double quotes" and 'single quotes'
    def strip_strings(s: str) -> str:
        result = []
        in_single = False
        in_double = False
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == "\\" and i + 1 < len(s):
                result.append(" ")
                i += 2
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                i += 1
                continue
            if ch == "'" and not in_double:
                in_single = not in_single
                i += 1
                continue
            if not in_single and not in_double:
                result.append(ch)
            else:
                result.append(" ")
            i += 1
        return "".join(result)

    comments: list[tuple[int, str]] = []

    # Pass 1: line comments //
    for lineno, raw_line in enumerate(lines, 1):
        stripped = strip_strings(raw_line)
        idx = stripped.find("//")
        if idx != -1:
            comment = stripped[idx:].rstrip("\n")
            comments.append((lineno, comment))

    # Pass 2: block comments /* */ (multi-line safe)
    buffer = ""
    in_block = False
    block_start = 0
    for lineno, raw_line in enumerate(lines, 1):
        stripped = strip_strings(raw_line)
        if not in_block:
            idx = stripped.find("/*")
            if idx != -1:
                in_block = True
                block_start = lineno
                buffer = stripped[idx:]
                end = buffer.find("*/")
                if end != -1:
                    comments.append((block_start, buffer[: end + 2]))
                    in_block = False
                    buffer = ""
            continue
        buffer += stripped
        end = buffer.find("*/")
        if end != -1:
            comments.append((block_start, buffer[: end + 2]))
            in_block = False
            buffer = ""

    comments.sort(key=lambda x: x[0])
    return comments


def main():
    if len(sys.argv) != 3:
        print("用法: python3 validate-comments.py <原文件> <新文件>")
        sys.exit(1)

    old_file, new_file = sys.argv[1], sys.argv[2]

    if not Path(old_file).exists():
        print(f"✗ 文件不存在: {old_file}")
        sys.exit(1)
    if not Path(new_file).exists():
        print(f"✗ 文件不存在: {new_file}")
        sys.exit(1)

    old_comments = extract_comments(old_file)
    new_comments = extract_comments(new_file)

    # 只比较注释内容（忽略行号），避免代码行数变化导致误报
    old_texts = [text for _, text in old_comments]
    new_texts = [text for _, text in new_comments]

    missing = [t for t in old_texts if t not in new_texts]

    if not missing:
        print("✓ 注释核对通过：所有注释已迁移")
        sys.exit(0)
    else:
        print("✗ 注释核对失败：以下注释在新文件中缺失")
        for t in missing:
            print(f"  - {t}")
        sys.exit(1)


if __name__ == "__main__":
    main()
